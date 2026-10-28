"""Estima el retard entre l'event TRIG (posicio GPS al comandament de disparo) i l'exposicio real.

Idea: la posicio reconstruida de cada foto (WebODM/OpenSfM, dominada pels punts de lligam) es la posicio de la camera
a l'instant de l'exposicio. El GPS registra la posicio a l'instant del comandament. Si l'exposicio arriba tau segons
despres, residu = GPS - reconstruit = -v * tau (+ desplacament global b). El residu canvia de signe entre passades
d'anada i tornada, i aixo ho distingeix d'un biaix constant.

Entrades (rutes relatives a aquest fitxer): ../proces/reconstruction.json, ../../../entrades/vol_*.bin (log compartit del vol)
Sortides: retard_per_foto.csv, retard_resum.json
Si el geo.txt del processat ja duia el retard corregit, el tau que surt es el retard RESIDUAL (hauria de ser ~0).
Limitacio: un desplacament fix antena->camera cap endavant es confon amb el retard (velocitat gairebe constant).
"""
import csv, glob, json, math, os
import numpy as np
from pymavlink import mavutil

AQUI = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(AQUI, "..", "proces", "reconstruction.json")
BIN = glob.glob(os.path.join(AQUI, "..", "..", "..", "entrades", "vol_*.bin"))[0]


def rodrigues(w):
    w = np.array(w, float)
    th = np.linalg.norm(w)
    if th < 1e-12:
        return np.eye(3)
    k = w / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def ajusta(A, y):
    x = np.linalg.lstsq(A, y, rcond=None)[0]
    e = y - A @ x
    se = np.sqrt((e @ e / (len(y) - A.shape[1])) * np.diag(np.linalg.inv(A.T @ A)))
    return x, se, float(np.sqrt(e @ e / len(y)))


shots = json.load(open(REC))[0]["shots"]
noms = sorted(shots)                      # DSCxxxxx.JPG: mateix ordre que els TRIG del log
C, G = [], []
for n in noms:
    s = shots[n]
    C.append(-rodrigues(s["rotation"]).T @ np.array(s["translation"]))   # centre optic reconstruit (ENU)
    G.append(s["gps_position"])                                           # posicio GPS d'entrada (ENU)
C, G = np.array(C), np.array(G)
r = G - C

m = mavutil.mavlink_connection(BIN)
tu, gps = [], []
while (x := m.recv_match(type=["TRIG", "GPS"], blocking=False)) is not None:
    if x.get_type() == "TRIG":
        tu.append(x.TimeUS)
    elif x.I == 0:
        gps.append((x.TimeUS, x.Spd, x.GCrs))
assert len(tu) == len(noms), f"{len(tu)} TRIG i {len(noms)} fotos"
gps = np.array(gps)
vE = np.interp(tu, gps[:, 0], gps[:, 1] * np.sin(np.radians(gps[:, 2])))   # velocitat GPS a 5 Hz, interpolada
vN = np.interp(tu, gps[:, 0], gps[:, 1] * np.cos(np.radians(gps[:, 2])))
sp = np.hypot(vE, vN)

o, z = np.ones(len(r)), np.zeros(len(r))
y = np.concatenate([r[:, 0], r[:, 1]])
x, se, rms = ajusta(np.column_stack([np.concatenate([o, z]), np.concatenate([z, o]), -np.concatenate([vE, vN])]), y)
tau, tau_se = float(x[2]), float(se[2])

per_sentit = {}
for lab, sel in (("ENE", (sp > 4) & (vE > 0)), ("WSW", (sp > 4) & (vE < 0))):
    s2 = np.concatenate([sel, sel])
    xs, ses, _ = ajusta((-np.concatenate([vE, vN]))[s2][:, None], y[s2])
    per_sentit[lab] = dict(n=int(sel.sum()), tau_s=float(xs[0]), se_s=float(ses[0]))

rc = r.copy()
rc[:, 0] += vE * tau
rc[:, 1] += vN * tau                     # posicio GPS corregida = GPS + v*tau
h0, h1 = np.hypot(r[:, 0], r[:, 1]), np.hypot(rc[:, 0], rc[:, 1])
recte = sp > 3

with open(os.path.join(AQUI, "retard_per_foto.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["foto", "v_m_s", "res_E", "res_N", "res_U", "res_H_abans", "res_E_corr", "res_N_corr", "res_H_despres"])
    for i, n in enumerate(noms):
        w.writerow([n, round(sp[i], 2), *np.round(r[i], 3), round(h0[i], 3), round(rc[i, 0], 3), round(rc[i, 1], 3), round(h1[i], 3)])

resum = dict(
    tau_s=round(tau, 4), tau_se_s=round(tau_se, 4), desplacament_global_m=[round(float(x[0]), 3), round(float(x[1]), 3)],
    per_sentit=per_sentit, n_fotos=len(noms), n_vol_recte_v_gt_3=int(recte.sum()),
    residu_horitzontal_m=dict(
        abans=dict(mediana=round(float(np.median(h0)), 3), rms=round(float(np.sqrt((h0 ** 2).mean())), 3), max=round(float(h0.max()), 3)),
        despres=dict(mediana=round(float(np.median(h1)), 3), rms=round(float(np.sqrt((h1 ** 2).mean())), 3), max=round(float(h1.max()), 3)),
        despres_nomes_vol_recte=dict(mediana=round(float(np.median(h1[recte])), 3), rms=round(float(np.sqrt((h1[recte] ** 2).mean())), 3), max=round(float(h1[recte].max()), 3))),
    residu_vertical_std_m=round(float(r[:, 2].std()), 3),
    fotos_outlier=[dict(foto=noms[i], v=round(float(sp[i]), 1), residu_despres_m=round(float(h1[i]), 2)) for i in np.argsort(-h1)[:3] if h1[i] > 1.0],
)
json.dump(resum, open(os.path.join(AQUI, "retard_resum.json"), "w"), indent=1)
print(json.dumps(resum, indent=1))
