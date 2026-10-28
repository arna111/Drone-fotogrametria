# Sistema d'aerofotogrametria de precisió amb base RTK pròpia

Disseny, construcció i validació en vol d'un sistema d'aerofotogrametria format per una base GNSS RTK (ZED-F9P + Raspberry Pi Zero W), un UAV S500 amb dos receptors GNSS en *moving baseline* (ArduCopter 4.6.3) i una càmera Sony α6000 amb *feedback* de sabata.

Informe complet: [`latex/main.pdf`](latex/main.pdf) (català) i [`latex/main_en.pdf`](latex/main_en.pdf) (English).

## Contingut

| Carpeta | Què hi ha |
|---|---|
| `latex/` | Font LaTeX de l'informe i els PDF (català i anglès). Vegeu [`latex/README.md`](latex/README.md) |
| `config/` | Fitxer de paràmetres d'ArduPilot de la configuració de referència |
| `base_rtk/` | Eines de la base RTK: servei `str2str` de la Pi, gestió de sessions i *survey-in* des del PC |
| `test_5_parc/`, `test_6_camp/` | Vols de prova 5 i 6: fitxa, *scripts* de post-procés, fitxes i *checksums* dels processats |

Cada vol té el seu `README.md` amb l'estructura, els resultats i les advertències.

## Dades de vol

Les fotografies, els *logs* `.bin`, les geoetiquetes, els resultats d'ODX (`all.zip`) i les sortides intermèdies (`report_odx/`, `proces/`) **no són al repositori**: pesen uns 8~GB i porten coordenades GPS. Es guarden en local, a les mateixes carpetes, i el `.gitignore` les exclou. Els `SHA256SUMS.txt` de cada processat permeten verificar-les.

## Requisits

- LaTeX amb `latexmk` i `biber` per compilar l'informe (`latexmk -pdf main.tex` i `latexmk -pdf main_en.tex` dins de `latex/`).
- Python 3 amb `pymavlink` i `numpy` per als *scripts* de post-procés.
- [ExifTool](https://exiftool.org/) (versió 13.59 als vols de prova): els *scripts* el busquen a `test_5_parc/eines/exiftool/exiftool-13.59_64/`.
- ODX / WebODM per reconstruir els models.

Repositori privat, sense llicència.
