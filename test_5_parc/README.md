# Vol de prova 5 (8/10/2026) — índex del projecte

Aerofotogrametria amb quad ArduCopter 4.6.3 (moving baseline, RTK Fixed 100 %) i Sony A6000 + TTArtisan 25 mm: 118 fotos, 8 passades, ~30 m, ~0,8 ha.
**Què fer servir:** el processat **`processats/run2_retard-corregit/`** (posicions corregides pel retard de l'obturador). El run 1 és la referència sense correcció.

## Estructura
```
README.md              aquest índex
entrades/                  log de vol (.bin) i paràmetres del vol (extrets del log)
fotos_corregides/          118 JPG amb l'EXIF corregit (Orientation=1, òptica, GPS); els originals només són a la SD
georef/                    geo.txt VIGENT (posicions corregides + precisions) i les taules de geoetiquetes
eines/                     scripts i exiftool (vegeu «Com es regenera»)
processats/
  run1_webodm_geo-v1/      primer processat (WebODM, geo.txt sense precisions ni correcció)
  run2_retard-corregit/    reprocés amb posicions corregides  <-- RECOMANAT
  comparacio_run1_vs_run2.txt
```
Cada processat té la seva `README.md` (advertències, opcions, resultats) i `SHA256SUMS.txt`.

## En una línia
- **Retard de l'obturador (comandament → exposició): 0,268 ± 0,008 s** (≈1,3 m a 5 m/s). Al run 2 el retard residual és 0,004 ± 0,007 s.
- **Georeferenciació:** la diferència model–GPS baixa de CE90 1,80 m (run 1) a 0,59 m (run 2). La geometria del model no canvia (reprojecció 0,90 px, calibració igual). No hi ha punts de comprovació: **no és una precisió absoluta**.
- **Càmera:** el tag EXIF d'orientació depèn del rumb (apuntant a nadir); ja està normalitzat. Focal calibrada ≈ 25,7 mm; GSD 0,45 cm/px.
- **EXIF de les fotos:** òptica TTArtisan 25 mm, f/5,6 (`FNumber` i `ApertureValue`, escrits després dels dos processats: només metadades, hash de les dades d'imatge idèntic a les 118), GPS del log i orientació 1.
- **DSM:** net a l'interior; estries a la perifèria (poques vistes): retallar o ampliar el pla de vol.

## Com es regenera
| Pas | Eina | Entrada → sortida |
|---|---|---|
| 1. Fotos + geoetiquetes | `eines/postproces_fotos.py` | SD + log → `fotos_corregides/`, `georef/geotags*.csv`, `georef/geo_sense_correccio.txt` (cal la SD muntada) |
| 2. geo.txt vigent | `eines/geo_corregit.py` | `georef/geotags.csv` + log + τ del run 1 → `georef/geo.txt`, `georef/geotags_corregit.csv` |
| 3. Processar | WebODM (pujant les fotos + `geo.txt`) o ODX directe (`processats/run2_retard-corregit/proces/comanda_execucio.bat`) | → carpeta de resultats |
| 4. Retard residual | `processats/<run>/analisi/estima_retard.py` | `proces/reconstruction.json` + log → `retard_*.{csv,json}` |
| 5. Comparar | `eines/compara_runs.py` | stats i posicions de dos runs → `processats/comparacio_run1_vs_run2.txt` |

Per a un altre vol: copiar `eines/`, canviar les rutes del principi dels scripts (`FOTOS`, `LOG`, `SORTIDA`) i l'`OPTICA`/`HACC`/`VACC` si cal.
ODX directe en aquest PC: la variable `NoDefaultCurrentDirectoryInExePath` ha d'estar buida dins del `.bat` (ja ho està a `comanda_execucio.bat`).

## Pendent
- **Base RTK del 8/10:** va ser la Raspberry Pi Zero W amb `str2str` i *survey-in* a cada sessió (informe, secció 1.5.2); la posició resultant no es va anotar i no es pot recuperar.
- **Bateria (resolt):** `BATT_VOLT_MULT` 10,82 i `BATT_AMP_PERVLT` 87,73 ja estan calibrats (vols posteriors); els V/A/mAh d'aquest vol no són fiables.
- **Feedback de càmera** (SYNC2, resolt): sense missatges `CAM` en aquest vol (cablejat invertit); verificat al vol 6 (110 de 110).
- **Punts de comprovació** mesurats a terra, per poder afirmar una precisió absoluta.
- **Còpia de seguretat de la SD** (`G:\DCIM\100MSDCF`): els 118 JPG originals no són enlloc més.
