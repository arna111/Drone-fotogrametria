"""Test 6 (13/10/2026, alba): fotos corregides, geotags amb el feedback CAM i fotos realcades del vol 2.

passos (arguments): corregides | realcades
- corregides: copia fotos_originals -> fotos_corregides (Orientation=1, optica, GPS) i escriu georef/geotags.csv i geo.txt.
- realcades:  del vol 2 (el vol 1 es inservible: guany x551 no recupera res) fa fotos_realcades/ amb guany per foto en llum lineal.

Aparellament foto <-> esdeveniment del log PER TEMPS (rellotge de la camera - hora GPS = offset constant), no per ordre:
hi ha una foto manual sense TRIG i un TRIG sense foto. Posicio = la del missatge CAM (instant real de l'exposicio);
si un TRIG no te CAM, TRIG + v * retard medià. Reutilitza patch_orientation, OPTICA i escriu_exif de test_5_parc/eines.
"""
import csv, datetime as dt, glob, os, shutil, subprocess, sys
import numpy as np
from multiprocessing import Pool
from pymavlink import mavutil

ARREL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ARREL, "..", "test_5_parc", "eines"))
import postproces_fotos as P5

ORIG, CORR, REAL = (os.path.join(ARREL, d) for d in ("fotos_originals", "fotos_corregides", "fotos_realcades"))
GEOREF = os.path.join(ARREL, "georef"); P5.GEOREF = GEOREF
VOLS = [("vol1", "vol1_2026-10-13_07-46-26.bin"), ("vol2", "vol2_2026-10-13_07-57-51.bin")]
V_RECTE, HACC_RECTE, HACC_GIR, VACC = 3.0, 0.5, 1.5, 0.3     # mateixos criteris que el test 5
TOL_S = 2.5                                                    # tolerancia de l'aparellament per temps (EXIF va a 1 s)
TARGET = 0.12                                                  # lluminositat lineal mitjana objectiu (el 8/10 era 0,16)
G0 = dt.datetime(1980, 1, 6)


def esdeveniments():
    ev = []
    for nom, f in VOLS:
        m = mavutil.mavlink_connection(os.path.join(ARREL, "entrades", f))
        tr, cm, gp = [], {}, []
        while (x := m.recv_match(type=["TRIG", "CAM", "GPS"], blocking=False)) is not None:
            t = x.get_type()
            if t == "TRIG": tr.append(x.to_dict())
            elif t == "CAM": cm[x.Img] = x.to_dict()
            elif x.I == 0: gp.append((x.TimeUS, x.Spd, x.GCrs))
        gp = np.array(gp)
        lag_med = float(np.median([(cm[t["Img"]]["TimeUS"] - t["TimeUS"]) / 1e6 for t in tr if t["Img"] in cm]))
        for t in tr:
            spd = float(np.interp(t["TimeUS"], gp[:, 0], gp[:, 1])); crs = float(np.interp(t["TimeUS"], gp[:, 0], np.unwrap(np.radians(gp[:, 2]))))
            c = cm.get(t["Img"])
            if c:
                lat, lon, alt, src, lag, tt, dlag = c["Lat"], c["Lng"], c["GPSAlt"], "CAM", (c["TimeUS"] - t["TimeUS"]) / 1e6, c, 0.0
            else:   # sense feedback: posicio del TRIG avancada v*retard
                mlon = 111320.0 * np.cos(np.radians(t["Lat"]))
                lat = t["Lat"] + spd * np.cos(crs) * lag_med / 111132.0; lon = t["Lng"] + spd * np.sin(crs) * lag_med / mlon
                alt, src, lag, tt, dlag = t["GPSAlt"], "TRIG+v*retard", lag_med, t, lag_med
            utc = G0 + dt.timedelta(weeks=int(tt["GPSWeek"]), milliseconds=int(tt["GPSTime"])) - dt.timedelta(seconds=18) + dt.timedelta(seconds=dlag)
            ev.append(dict(vol=nom, img=t["Img"], lat=lat, lon=lon, alt=alt, font=src, lag=lag, v=spd, yaw=tt["Y"], relalt=tt["RelAlt"],
                           hacc=HACC_RECTE if spd > V_RECTE else HACC_GIR, utc=utc))
    return ev


def aparella():
    from PIL import Image
    fotos = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ORIG, "*.JPG")))
    tf = {n: dt.datetime.strptime(Image.open(os.path.join(ORIG, n)).getexif().get_ifd(0x8769)[0x9003], "%Y:%m:%d %H:%M:%S") for n in fotos}
    ev = esdeveniments(); eu = np.array([(e["utc"] - G0).total_seconds() for e in ev]); fu = np.array([(tf[n] - G0).total_seconds() for n in fotos])
    # offset del rellotge: moda de les diferencies foto - esdeveniment mes proper (robust a les excepcions)
    d = np.array([fu[i] - eu[np.argmin(abs(eu - (fu[i] - 32557)))] for i in range(len(fotos))]); off = float(np.median(d))
    rows, usats, sense = [], set(), []
    for n, t in zip(fotos, fu):
        j = int(np.argmin(abs(eu - (t - off))))
        if abs(eu[j] - (t - off)) <= TOL_S and j not in usats: usats.add(j); rows.append(dict(ev[j], filename=n))
        else: sense.append((n, tf[n].strftime("%H:%M:%S")))
    print(f"offset rellotge camera - GPS UTC: {off:.1f} s ({off / 3600:.2f} h) | fotos aparellades: {len(rows)} de {len(fotos)} | esdeveniments sense foto: {[(e['vol'], e['img']) for k, e in enumerate(ev) if k not in usats]} | fotos sense esdeveniment: {sense}")
    return rows


def corregides():
    rows = aparella(); os.makedirs(CORR, exist_ok=True); os.makedirs(GEOREF, exist_ok=True)
    noms = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ORIG, "*.JPG"))); canvis = {}
    for n in noms:
        q = os.path.join(CORR, n); shutil.copy2(os.path.join(ORIG, n), q)
        try: o = P5.patch_orientation(q)
        except RuntimeError: o = "sense tag"        # alguna foto no porta Orientation: equival a 1 (normal), res a canviar
        canvis[o] = canvis.get(o, 0) + 1
    print("orientacions originals canviades a 1:", canvis)
    with open(os.path.join(GEOREF, "geotags.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["filename", "vol", "lat", "lon", "alt_gps_m", "font", "lag_trig_cam_s", "v_m_s", "yaw_deg", "relalt_m", "hacc_m", "vacc_m"])
        for r in rows: w.writerow([r["filename"], r["vol"], f"{r['lat']:.8f}", f"{r['lon']:.8f}", f"{r['alt']:.3f}", r["font"], round(r["lag"], 3), round(r["v"], 2), round(r["yaw"], 2), round(r["relalt"], 2), r["hacc"], VACC])
    r2 = [r for r in rows if r["vol"] == "vol2"]
    with open(os.path.join(GEOREF, "geo.txt"), "w") as f:       # nomes el vol 2: es el que es processa
        f.write("EPSG:4326\n")
        for r in r2: f.write(f"{r['filename']} {r['lon']:.8f} {r['lat']:.8f} {r['alt']:.3f} nan nan nan {r['hacc']} {VACC}\n")
    P5.escriu_exif(CORR, [(r["filename"], r["lat"], r["lon"], r["alt"]) for r in rows])
    print(f"{len(noms)} fotos corregides ({len(rows)} amb GPS); geo.txt amb {len(r2)} fotos del vol 2")


def realca(args):
    from PIL import Image
    src, dst = args
    im = Image.open(src); a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    l = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    lum = float((0.2126 * l[..., 0] + 0.7152 * l[..., 1] + 0.0722 * l[..., 2]).mean()); g = TARGET / max(lum, 1e-6)
    l = np.clip(l * g, 0, 1); e = np.where(l <= 0.0031308, 12.92 * l, 1.055 * l ** (1 / 2.4) - 0.055)
    Image.fromarray((e * 255 + 0.5).astype(np.uint8)).save(dst, quality=95, subsampling=0)
    return os.path.basename(src), g


def realcades():
    noms = [r["filename"] for r in csv.DictReader(open(os.path.join(GEOREF, "geotags.csv"))) if r["vol"] == "vol2"]
    os.makedirs(REAL, exist_ok=True)
    with Pool(6) as pool: res = pool.map(realca, [(os.path.join(CORR, n), os.path.join(REAL, n)) for n in noms])
    with open(os.path.join(GEOREF, "realcat_guanys.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["filename", "guany_lineal"]); w.writerows([(n, round(g, 2)) for n, g in res])
    args = os.path.join(GEOREF, "_args_exif.txt")
    tags = ["-Make", "-Model", "-DateTimeOriginal", "-ExposureTime", "-ISO", "-FNumber", "-ApertureValue", "-FocalLength", "-FocalLengthIn35mmFormat",
            "-LensMake", "-LensModel", "-MaxApertureValue", "-GPS:all", "-Orientation#=1"]   # '#': valor numeric (sense, "1" coincidiria amb el text "Rotate 180")
    with open(args, "w", encoding="utf-8") as f:
        for n, g in res:
            f.write("\n".join(["-tagsFromFile", os.path.join(CORR, n), *tags, f"-ImageDescription=Realcada digitalment: guany lineal x{g:.1f} (foto original molt subexposada)", os.path.join(REAL, n), "-overwrite_original", "-execute"]) + "\n")
    subprocess.run([P5.EXIFTOOL, "-@", args], check=True, stdout=subprocess.DEVNULL); os.remove(args)
    g = np.array([x for _, x in res]); print(f"{len(res)} fotos realcades; guany x{g.min():.0f}..x{g.max():.0f} (mediana x{np.median(g):.0f})")


if __name__ == "__main__":
    {"corregides": corregides, "realcades": realcades}[sys.argv[1]]()
