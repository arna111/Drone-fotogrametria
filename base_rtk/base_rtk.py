#!/usr/bin/env python3
"""Control de la base RTK des del PC (connectat al Wi-Fi BaseRTK).

  python base_rtk.py llista
  python base_rtk.py baixa [SESSIO|ultima] [-o CARPETA]
  python base_rtk.py esborra SESSIO... | --abans N
  python base_rtk.py survey [--estat] [--minuts N]

Tot el treball el fa l'eina 'rtkbase' de la Pi; aqui nomes es crida per SSH.
"""
import argparse
import os
import subprocess
import sys

HOST = "arnau@192.168.4.1"
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8"]


def remot(*args, tty=False):
    ordre = SSH + (["-t"] if tty else []) + [HOST, "rtkbase", *args]
    return subprocess.run(ordre)


def baixa(args):
    r = subprocess.run(SSH + [HOST, "rtkbase", "mida", args.sessio], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip() or "No s'ha pogut consultar la Pi.")
    n, mida = r.stdout.split()
    fitxer = os.path.join(args.o, "base_s%s.rtcm3" % n)
    if os.path.exists(fitxer):
        sys.exit("%s ja existeix." % fitxer)
    with open(fitxer, "wb") as f:
        r = subprocess.run(SSH + [HOST, "rtkbase", "uneix", n], stdout=f)
    if r.returncode or os.path.getsize(fitxer) < int(mida):
        os.remove(fitxer)
        sys.exit("La descarrega no s'ha completat; no s'ha desat res.")
    print("%s  (%.1f MB)" % (fitxer, os.path.getsize(fitxer) / 1e6))
    r = subprocess.run(SSH + [HOST, "rtkbase", "info", n], capture_output=True, text=True)
    if r.stdout.strip():
        notes = os.path.join(args.o, "base_s%s_survey.txt" % n)
        open(notes, "w").write(r.stdout)
        print(notes)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="ordre", required=True)
    s = sub.add_parser("baixa", help="descarrega una sessio unida en un sol fitxer")
    s.add_argument("sessio", nargs="?", default="ultima")
    s.add_argument("-o", default=".", help="carpeta de destinacio")
    for nom in ("llista", "esborra", "survey"):
        sub.add_parser(nom, help="com a 'rtkbase %s' a la Pi (--help per veure les opcions)" % nom)
    # Aquestes tres es reenvien tal qual; argparse no admet una opcio com a primer argument.
    if len(sys.argv) > 1 and sys.argv[1] in ("llista", "esborra", "survey"):
        sys.exit(remot(*sys.argv[1:], tty=sys.argv[1] != "llista").returncode)
    baixa(p.parse_args())


if __name__ == "__main__":
    main()
