"""geo.txt per a ODM amb les posicions GPS corregides pel retard de l'obturador i precisions per foto.

posicio corregida = posicio TRIG + v * tau   (la camera exposa tau segons despres del comandament)

Entrades: georef/geotags.csv (posicions TRIG), el log .bin (velocitat GPS al disparo) i el tau estimat
          per analisi/estima_retard.py del processat de referencia.
Sortides: georef/geo.txt (vigent) i georef/geotags_corregit.csv (el que s'ha canviat de cada foto).
Nomes es corregeix l'horitzontal: en vol nivellat el vertical gairebe no depen del retard (desv. est. 0,12 m).
"""
import csv, json, math, os
import numpy as np
from pymavlink import mavutil

ARREL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOREF = os.path.join(ARREL, "georef")
LOG = os.path.join(ARREL, "entrades", "vol_2026-10-08_12-24-58.bin")   # copia del log de vol dins del projecte
RESUM = os.path.join(ARREL, "processats", "run1_webodm_geo-v1", "analisi", "retard_resum.json")
# Precisions (m) segons el residu observat despres de corregir el retard: RMS 0,56 en vol recte (v > 3 m/s),
# 0,84 als girs (v <= 3 m/s, pics de 2,35 m) i desv. est. vertical 0,12 m. Els angles van a nan (son de l'aeronau).
V_RECTE = 3.0
HACC_RECTE, HACC_GIR, VACC = 0.5, 1.5, 0.3


def metres_per_grau(lat_deg):
    """Radis de curvatura WGS84 -> (m per radian de latitud, m per radian de longitud)."""
    a, e2 = 6378137.0, 0.00669437999014
    s = math.sin(math.radians(lat_deg))
    w = math.sqrt(1 - e2 * s * s)
    return a * (1 - e2) / w ** 3, a / w * math.cos(math.radians(lat_deg))


tau = json.load(open(RESUM))["tau_s"]
fotos = list(csv.DictReader(open(os.path.join(GEOREF, "geotags.csv"))))

m = mavutil.mavlink_connection(LOG)
tu, gps = [], []
while (x := m.recv_match(type=["TRIG", "GPS"], blocking=False)) is not None:
    if x.get_type() == "TRIG":
        tu.append(x.TimeUS)
    elif x.I == 0:
        gps.append((x.TimeUS, x.Spd, x.GCrs))
assert len(tu) == len(fotos), f"{len(tu)} TRIG i {len(fotos)} fotos"
gps = np.array(gps)
vE = np.interp(tu, gps[:, 0], gps[:, 1] * np.sin(np.radians(gps[:, 2])))
vN = np.interp(tu, gps[:, 0], gps[:, 1] * np.cos(np.radians(gps[:, 2])))
sp = np.hypot(vE, vN)

linies, taula = [], []
for i, f in enumerate(fotos):
    lat, lon, alt = float(f["lat"]), float(f["lon"]), float(f["alt_gps_m"])
    mlat, mlon = metres_per_grau(lat)
    lat2 = lat + math.degrees(vN[i] * tau / mlat)
    lon2 = lon + math.degrees(vE[i] * tau / mlon)
    hacc = HACC_RECTE if sp[i] > V_RECTE else HACC_GIR
    linies.append(f"{f['filename']} {lon2:.8f} {lat2:.8f} {alt:.3f} nan nan nan {hacc} {VACC}\n")
    taula.append([f["filename"], f"{lat2:.8f}", f"{lon2:.8f}", f"{alt:.3f}", round(float(sp[i]), 2),
                  round(math.hypot(vE[i], vN[i]) * tau, 3), hacc, VACC])

with open(os.path.join(GEOREF, "geo.txt"), "w") as f:
    f.write("EPSG:4326\n")
    f.writelines(linies)
with open(os.path.join(GEOREF, "geotags_corregit.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["filename", "lat_corr", "lon_corr", "alt_gps_m", "v_m_s", "despl_aplicat_m", "hacc_m", "vacc_m"])
    w.writerows(taula)
print(f"tau = {tau} s ; {len(linies)} fotos ; desplacament aplicat: mediana {np.median(sp * tau):.2f} m, max {np.max(sp * tau):.2f} m")
