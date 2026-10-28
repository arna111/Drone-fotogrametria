# Vol de prova 5 — run 2: reprocés amb posicions corregides pel retard

> **Aquest és el processat recomanat per al report.** El run 1 (`..\run1_webodm_geo-v1\`) és la referència sense correcció. Visió general del vol: `..\..\README.md`.
> Integritat: `SHA256SUMS.txt` (`sha256sum -c SHA256SUMS.txt` des d'aquesta carpeta).

## 1. Què canvia respecte al run 1
**Només el `geo.txt`.** Mateixes 118 fotos (hash idèntic), mateix motor (ODX 3.8.3, executat directament, no des de la interfície de WebODM), mateixes 9 opcions i mateix PC.
- Posicions: GPS del `TRIG` **+ v·τ** amb τ = 0,2684 s (retard de l'obturador estimat al run 1). Desplaçament aplicat: mediana 1,33 m, màx 1,39 m, només horitzontal (`proces/geo_usat_a_la_tasca.txt`; es genera amb `eines/geo_corregit.py`).
- Precisions per foto: 0,5 m (103 fotos en vol recte, v > 3 m/s), 1,5 m (15 fotos als girs), 0,3 m vertical. El run 1 va usar les per defecte (3/3/9 m).

## 2. Resultats i comparació amb el run 1
| | run 1 | run 2 |
|---|---|---|
| Fotos reconstruïdes | 118 | 118 |
| Error de reprojecció | 0,90 px | 0,90 px |
| Punts del model dispers | 173.084 | 173.401 |
| Calibració: focal efectiva | 25,72 mm | 25,74 mm |
| GSD mitjà | 0,451 cm/px | 0,452 cm/px |
| **Diferència model–GPS, E / N / vertical (desv. est.)** | 1,30 / 0,37 / 0,12 m | **0,40 / 0,14 / 0,11 m** |
| **CE90 / LE90 model–GPS** | 1,80 / 0,19 m | **0,59 / 0,18 m** |
| Error mitjà model–GPS | 1,26 m | 0,34 m |
| Àrea reconstruïda / núvol dens | 6.633 m² / 38.547.923 | 6.714 m² / 38.727.582 |
| Temps | 43 min 24 s | 41 min 34 s |

**Lectura:** la geometria del model no canvia (reprojecció, calibració i punts, iguals), cosa esperada perquè la dominen els punts de lligam. Canvia la **georeferenciació**: la concordança amb el GPS millora (E 1,30 → 0,40 m, CE90 1,80 → 0,59 m).
Les posicions de càmera georeferenciades es mouen de run 1 a run 2 0,162 m de mediana i com a màxim 0,309 m (mitjana E -0,001, N -0,021, vertical -0,003 m), amb una rotació del model de +0,199° i una escala relativa de 1,00396.
**Els errors model–GPS no són una precisió absoluta** (no hi ha punts de comprovació; vegeu les advertències).

## 3. Verificació del retard (`analisi/`)
Mateixa anàlisi que al run 1, sobre la nova reconstrucció (`python analisi/estima_retard.py`). Ara el retard que queda és **residual**:
- **τ residual = 0,004 ± 0,007 s** (run 1: 0,268 ± 0,009 s); ENE 0,010, WSW 0,004. Desplaçament global +0,03, +0,00 m.
- Residu horitzontal GPS corregit − model: mediana 0,35 m, RMS 0,51 m (en vol recte 0,34 / 0,47 m; run 1 amb la mateixa correcció aplicada a posteriori: 0,46 / 0,56 m). Vertical: desv. est. 0,12 m.
- Atípiques, igual que al run 1: DSC00082.JPG (v=1,4 m/s, 2,26 m), DSC00187.JPG (v=3,7 m/s, 1,14 m), DSC00085.JPG (v=5,0 m/s, 1,00 m).
- El soroll que queda (~0,3 m al llarg de la trajectòria) correspon a ~0,06 s de variació del retard entre fotos.

## 4. Revisió visual (8/10/2026)
Ortofoto 14.084 × 8.918 px a 1 cm/px i DSM 7.041 × 4.458 px a 2 cm/px, equivalents als del run 1: mosaic coherent, interior del DSM net i **les mateixes estries a la perifèria** (poques vistes): retallar al polígon d'interès o ampliar el pla de vol ~1 footprint.

## 5. Advertències que cal reflectir al report
1. **Rellotge de la càmera desfasat +9 h 02 m 33 s** respecte a UTC: les hores del report d'ODX (19:29:30 – 19:32:42) són hora de càmera. Hora real: **10:26:56 – 10:30:09 UTC** (12:26–12:30 hora local d'estiu).
2. **No hi ha GCP ni punts de comprovació:** no es pot afirmar una precisió absoluta. La posició absoluta depèn de la base RTK (SBC, coordenades i mètode, per confirmar).
3. **El retard τ és efectiu:** suma el retard de l'obturador i, possiblement, el de posició GPS/EKF; un desplaçament fix antena→càmera cap endavant es confon amb ell. Al banc el retard comandament→obturador és de 0,12–0,19 s (feedback inactiu en aquest vol; arreglat després).
4. **Fotos originals només a la SD** (`G:\DCIM\100MSDCF`); el projecte en té còpies amb l'EXIF corregit (`..\..\fotos_corregides`); el `FNumber` (f/5,6) s'hi va escriure després d'aquest processat (només metadades; dades d'imatge idèntiques).
5. **Voltatge, corrent i mAh del log no són fiables** (`BATT_VOLT_MULT` 12,2 dona 27,65 V en repòs; `BATT_AMP_PERVLT` 17): no s'han de citar.
6. Processat executat amb ODX 3.8.3 directament; no és a la base de dades de WebODM. Per veure'l a la interfície: *Importar* `resultats/all.zip`.

## 6. Processament
ODX 3.8.3 · i5-10400F, 32 GB, RTX 2060 · 43 min 16 s (suma d'etapes, `proces/benchmark.txt`).
Opcions no per defecte: `orthophoto-resolution` 1 · `pc-quality` high · `dem-resolution` 2 · `dsm`, `auto-boundary`, `cog`, `gltf`, `pc-ept` activats · `max-concurrency` 8. Ordre d'execució: `proces/comanda_execucio.bat` (calen `NoDefaultCurrentDirectoryInExePath` buit en aquest entorn). Log: `proces/task_output.txt`.

## 7. Contingut
```
README.md        aquesta fitxa
SHA256SUMS.txt       checksums de tots els fitxers
resultats/all.zip    ortofoto GeoTIFF, DSM, núvol LAZ/EPT, models OBJ/GLB, informe (mateixa estructura que el run 1)
report_odx/          report.pdf, stats.json, shots.geojson, cameras.json
proces/              options.json, geo usat, log, benchmark, reconstruction.json (OpenSfM), comanda d'execució
analisi/             estima_retard.py + retard residual
```
El log de vol (`.bin`) i els paràmetres són a `..\..\entrades\`.
