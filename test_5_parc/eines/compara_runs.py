import json, math, os, numpy as np
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "processats")
R1 = os.path.join(P, "run1_webodm_geo-v1"); R2 = os.path.join(P, "run2_retard-corregit")
S1 = json.load(open(os.path.join(R1, "report_odx", "stats.json"))); S2 = json.load(open(os.path.join(R2, "report_odx", "stats.json")))


def g(S):
    rs, ge, od, ps = S["reconstruction_statistics"], S["gps_errors"], S["odm_processing_statistics"], S["processing_statistics"]
    cam = list(S["camera_errors"].values())[0]["optimized_values"]
    return dict(fotos=rs["reconstructed_shots_count"], punts=rs["reconstructed_points_count"], obs=rs["observations_count"],
                reproj_px=rs["reprojection_error_pixels"], gsd=od["average_gsd"], area=ps["area"],
                focal_mm=cam["focal"] * 23.5, k1=cam["k1"], k2=cam["k2"], k3=cam["k3"],
                gps_std_E=ge["std"]["x"], gps_std_N=ge["std"]["y"], gps_std_U=ge["std"]["z"], ce90=ge["ce90"], le90=ge["le90"],
                gps_mitja_err=ge["average_error"], gps_sigma=tuple(ge["average_gps_std"].values()), temps_s=od["total_time"])


a, b = g(S1), g(S2)
print(f"{'metrica':16s} {'run1 (sense corr.)':>20s} {'run2 (retard corr.)':>20s}")
for k in a:
    fa, fb = a[k], b[k]
    print(f"{k:16s} {str(round(fa,4) if isinstance(fa,float) else fa):>20s} {str(round(fb,4) if isinstance(fb,float) else fb):>20s}")

# posicions de camera georeferenciades (shots.geojson): run1 -> run2
def shots(path):
    d = json.load(open(path)); out = {}
    for f in d["features"]:
        p = f["properties"]; nm = p.get("filename") or p.get("name") or p.get("image")
        out[nm] = f["geometry"]["coordinates"]
    return out
s1 = shots(os.path.join(R1, "report_odx", "shots.geojson")); s2 = shots(os.path.join(R2, "report_odx", "shots.geojson"))
nm = sorted(set(s1) & set(s2)); print("\nfotos comunes:", len(nm))
A = np.array([s1[n] for n in nm]); B = np.array([s2[n] for n in nm])
la = math.radians(A[:, 1].mean()); kx, ky = 111320 * math.cos(la), 110574
dE, dN, dU = (B[:, 0] - A[:, 0]) * kx, (B[:, 1] - A[:, 1]) * ky, B[:, 2] - A[:, 2]
print("Diferencia de posicio de camera run2 - run1 (m):  E mitjana %+.3f std %.3f | N mitjana %+.3f std %.3f | U mitjana %+.3f std %.3f" % (dE.mean(), dE.std(), dN.mean(), dN.std(), dU.mean(), dU.std()))
print("  modul horitzontal: mediana %.3f m, max %.3f m" % (np.median(np.hypot(dE, dN)), np.hypot(dE, dN).max()))
# rotacio i escala del model (Kabsch 2D)
X = np.column_stack([(A[:, 0] - A[:, 0].mean()) * kx, (A[:, 1] - A[:, 1].mean()) * ky]); Y = np.column_stack([(B[:, 0] - B[:, 0].mean()) * kx, (B[:, 1] - B[:, 1].mean()) * ky])
U_, S_, Vt = np.linalg.svd(X.T @ Y); Rm = Vt.T @ U_.T; ang = math.degrees(math.atan2(Rm[1, 0], Rm[0, 0])); esc = S_.sum() / (X ** 2).sum()
print("Rotacio del model run1->run2: %+.3f graus (%.1f mm/m a 50 m de radi) ; escala relativa %.5f" % (ang, abs(math.radians(ang)) * 1000, esc))
