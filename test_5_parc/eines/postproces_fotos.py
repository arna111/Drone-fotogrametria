"""Postprocessat de fotos del vol: corregeix l'orientacio EXIF i genera geoetiquetes des del log.

- Copia les fotos a SORTIDA i hi posa EXIF Orientation=1 (patch de 2 bytes, sense recomprimir ni tocar la resta).
- Casa cada foto amb el seu esdeveniment TRIG del log per ordre (cal el mateix nombre de fotos i TRIG).
- Escriu geotags.csv (generic) i geo.txt (format OpenDroneMap/WebODM).
- Amb exiftool escriu a les copies l'optica i el GPS del log, i Orientation=1 tambe a la miniatura (IFD1).
"""
import glob, os, shutil, struct, csv, sys, subprocess
from pymavlink import mavutil

SORTIDA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta del vol (pare d'eines/)
FOTOS = r"G:\DCIM\100MSDCF"  # SD de la camera
LOG = os.path.join(SORTIDA, "entrades", "vol_2026-10-08_12-24-58.bin")
EXIFTOOL = os.path.join(SORTIDA, "eines", "exiftool", "exiftool-13.59_64", "exiftool.exe")
GEOREF = os.path.join(SORTIDA, "georef")
# TTArtisan 25 mm f/2 en APS-C (A6000, sensor de 23,5 mm): 25 x 1,53 = 38 mm equivalent.
# L'anella d'obertura es manual i la camera no la registra: f/5,6 es el valor fixat amb cinta (fitxa d'estat de l'usuari).
# Amb -n, ApertureValue va en APEX: 2*log2(5,6) = 4,9709. Canviar els dos junts si canvia l'obertura.
OPTICA = ["-FocalLength=25", "-FocalLengthIn35mmFormat=38", "-LensMake=TTArtisan",
          "-LensModel=TTArtisan 25mm f/2", "-MaxApertureValue=2", "-FNumber=5.6", "-ApertureValue=4.9709"]
# Precisio de posicio per foto al geo.txt (m, horitzontal i vertical). La posicio es la del comandament de
# disparo, no la de l'obturador, i el biaix canvia de signe entre passades: per aixo no s'hi posen centimetres.
# Els angles hi van a nan: son de l'aeronau, no de la camera (que esta girada ~90 graus).
HACC, VACC = 1.5, 1.0


def patch_orientation(path):
    """Posa Orientation=1 a IFD0 del EXIF modificant nomes els 2 bytes del valor. Retorna l'antic."""
    with open(path, "r+b") as f:
        d = f.read(65536)
        i = d.index(b"\xff\xe1")
        assert d[i + 4:i + 10] == b"Exif\0\0", "APP1 no es EXIF"
        t = i + 10                                   # inici de la capcalera TIFF
        e = "<" if d[t:t + 2] == b"II" else ">"
        ifd = t + struct.unpack(e + "I", d[t + 4:t + 8])[0]
        n = struct.unpack(e + "H", d[ifd:ifd + 2])[0]
        for k in range(n):
            ent = ifd + 2 + 12 * k
            if struct.unpack(e + "H", d[ent:ent + 2])[0] == 0x0112:
                old = struct.unpack(e + "H", d[ent + 8:ent + 10])[0]
                f.seek(ent + 8)
                f.write(struct.pack(e + "H", 1))
                return old
    raise RuntimeError("sense tag Orientation: " + path)


def main():
    fotos = sorted(glob.glob(os.path.join(FOTOS, "*.JPG")))
    m = mavutil.mavlink_connection(LOG)
    trig = []
    while (x := m.recv_match(type="TRIG", blocking=False)) is not None:
        trig.append(x)
    if len(fotos) != len(trig):
        sys.exit(f"ATENCIO: {len(fotos)} fotos pero {len(trig)} TRIG; no es pot casar per index")

    dst = os.path.join(SORTIDA, "fotos_corregides")
    os.makedirs(dst, exist_ok=True)
    rows, canvis = [], {}
    for p, t in zip(fotos, trig):
        q = os.path.join(dst, os.path.basename(p))
        shutil.copy2(p, q)
        old = patch_orientation(q)
        canvis[old] = canvis.get(old, 0) + 1
        rows.append((os.path.basename(p), t.Lat, t.Lng, t.GPSAlt, t.Alt, t.RelAlt, t.Y, t.P, t.R))

    os.makedirs(GEOREF, exist_ok=True)
    with open(os.path.join(GEOREF, "geotags.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "lat", "lon", "alt_gps_m", "alt_ekf_m", "alt_rel_m", "yaw_deg", "pitch_deg", "roll_deg"])
        w.writerows(rows)
    escriu_geo(rows)
    escriu_exif(dst, rows)

    print("Orientacions originals canviades a 1:", canvis)
    print("Sortida:", SORTIDA)


def escriu_geo(rows):
    """geo d'ODM SENSE corregir el retard: nom lon lat alt yaw pitch roll hacc vacc (angles a nan s'ignoren).
    El geo.txt vigent (amb el retard corregit) el genera geo_corregit.py."""
    with open(os.path.join(GEOREF, "geo_sense_correccio.txt"), "w") as f:
        f.write("EPSG:4326\n")
        for r in rows:
            f.write(f"{r[0]} {r[2]:.8f} {r[1]:.8f} {r[3]:.3f} nan nan nan {HACC} {VACC}\n")


def escriu_exif(dst, rows):
    """Escriu optica i GPS (del log, alt = MSL) a les copies amb exiftool."""
    csv_path = os.path.join(GEOREF, "geotags_exif.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["SourceFile", "GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef",
                    "GPSAltitude", "GPSAltitudeRef"])
        for r in rows:
            w.writerow([r[0], abs(r[1]), "N" if r[1] >= 0 else "S", abs(r[2]), "E" if r[2] >= 0 else "W",
                        abs(r[3]), 0 if r[3] >= 0 else 1])
    subprocess.run([EXIFTOOL, "-overwrite_original", "-n", f"-csv={csv_path}", *OPTICA,
                    "-GPSMapDatum=WGS-84", "-IFD1:Orientation=1", *[r[0] for r in rows]],
                   cwd=dst, check=True)


if __name__ == "__main__":
    main()
