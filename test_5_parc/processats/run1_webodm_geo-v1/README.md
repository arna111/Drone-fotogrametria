# Vol de prova 5 — arxiu de resultats (WebODM)

Còpia dels resultats i del procés per reproduir-los i redactar el report (el log de vol i els paràmetres són compartits a `..\..\entrades\`). Només hi ha còpies:
WebODM (`E:\WebODM`, dins la carpeta de l'aplicació) i la SD de la càmera no s'han modificat.
Integritat: `SHA256SUMS.txt` (verificar amb `sha256sum -c SHA256SUMS.txt` des d'aquesta carpeta).

> Primer processat (run 1). El reprocés amb les posicions corregides pel retard és a `..\run2_retard-corregit\`; la visió general del vol és a `..\..\README.md`.

## 1. Advertències que cal reflectir al report
1. **`geo.txt` usat = versió sense precisions** (`proces/geo_usat_a_la_tasca.txt`). El motor va aplicar les precisions per defecte
   (σ horitzontal 3 m, vertical 9 m), no les 1,5/1,0 m de la versió nova.
2. **Rellotge de la càmera desfasat +9 h 02 m 33 s** respecte a UTC. Les hores del report d'ODX
   (19:29:30 – 19:32:42, 8/10/2026) són hora de càmera. Hora real del vol: **10:26:56 – 10:30:09 UTC** (12:26–12:30 hora local d'estiu), segons el GPS del log.
3. **Posicions de càmera biaixades pel retard de l'obturador** (secció 5): la posició GPS és la del comandament, ~0,27 s abans de l'exposició (≈1,3 m a 5 m/s). El model es va alinear amb aquestes posicions.
4. **No hi ha GCP ni punts de comprovació.** Els «errors GPS» d'ODX (secció 4) comparen el model amb el GPS de les fotos: **no són una precisió absoluta independent**. No es pot afirmar una precisió absoluta sense verificació externa.
5. **La posició absoluta depèn de la base RTK** (coordenades i mètode —survey-in o fixa— no consten aquí; vegeu la secció 6).
6. **Les fotos originals només són a la SD** (`G:\DCIM\100MSDCF`, 118 fitxers; no són a l'arxiu). Les del projecte (`..\..\fotos_corregides`) són còpies amb l'EXIF corregit (Orientation=1, òptica, GPS), generades amb `..\..\eines\postproces_fotos.py`. El `FNumber` (f/5,6) s'hi va escriure després d'aquest processat: només metadades, les dades d'imatge són idèntiques.
7. **La tasca es va tornar a executar a les 15:41** (reexecució sobre els resultats existents: no es va recalcular res, només es va reempaquetar `all.zip`). Conseqüències: el `benchmark.txt` i el `log.json` de NodeODX són els de la reexecució; s'han substituït pels originals (`proces/log.json` de WebODM, `proces/benchmark_execucio_real.txt` transcrit abans de la sobreescriptura). El contingut de `all.zip` s'ha verificat (CRC32 i mida) fitxer a fitxer contra el que WebODM va importar a les 15:27: idèntic, excepte `log.json`.

8. **Voltatge, corrent i mAh del log no són fiables:** `BATT_VOLT_MULT` 12,2 dona 27,65 V en repòs amb un pack 6S i `BATT_AMP_PERVLT` 17 dona 337 mAh en 7 min. No s'han de citar al report fins que es calibrin.

## 2. Equip i vol
| | |
|---|---|
| Autopilot | ArduCopter V4.6.3, placa KakuteH7, RC CRSF, ESC DShot300 |
| Càmera / òptica | Sony ILCE-6000 + TTArtisan 25 mm f/2 APS-C, enfocament i diafragma manuals (obertura no registrada); exposició 1/1600 s |
| Navegació | RTK Fixed el 100 % del vol (log, GPS[0] i GPS[1]); correccions d'una base RTK pròpia amb ZED-F9P (**SBC i distribució per confirmar**, secció 6) |
| Vol | 118 fotos, 8 passades separades 6,5 m, 7,1 m entre fotos (disparo per distància), ~30 m sobre el punt d'enlairament, ~5 m/s |
| Solapament (calculat) | ~75–77 % frontal, ~65–69 % lateral; ~11 imatges per punt |
| Ajust de la càmera (segons la fitxa d'estat) | mode M, 1/1600 s, **f/5,6** (anell fixat), MF a infinit, ISO auto (sostre 1600), Single, JPEG Fine, obturador electrònic 1a cortina ON; l'EXIF no porta f/5,6 |
| Disparo i feedback | Seagull MAP2 (pad M5, mode IS-T: `CAM1_SERVO_ON` 1700); feedback SYNC2→GPIO 55: **sense feedback en aquest vol** (cables invertits; corregit i verificat 7/8 al banc després, latència 0,12–0,19 s) |
| Càmera respecte al dron | girada 90° (costat llarg en el sentit de vol); els angles del log són de l'aeronau, no de la càmera |
| Paràmetres i log del vol | `..\..\entrades\params_vol.param` (extrets del log) · `..\..\entrades\vol_2026-10-08_12-24-58.bin` |

## 3. Processament
WebODM 3.3.0 · NodeODX 2.3.1 · motor ODX 3.8.3 · PC: i5-10400F (6 nuclis), 32 GB RAM, RTX 2060.
Temps: 43 min 24 s segons ODX (`stats.json`, abans de les etapes finals d'informe i postprocés); suma d'etapes del benchmark original: 45 min 7 s.

Opcions que no són les per defecte d'ODX: `orthophoto-resolution` 1 cm/px · `pc-quality` high · `dem-resolution` 2 cm/px ·
`dsm` sí · `auto-boundary` sí · `max-concurrency` 8 · `cog` sí · `gltf` sí · `pc-ept` sí.
Totes les opcions: `proces/options.json`; log complet: `proces/task_output.txt`.

## 4. Resultats (de `report_odx/stats.json`)
| | |
|---|---|
| Fotos reconstruïdes | 118 de 118 (1 component) |
| Punts del model dispers / observacions | 173.084 / 655.535 |
| Error de reprojecció | 0,90 px |
| GSD mitjà | 0,451 cm/px |
| Àrea reconstruïda | 6.633 m² |
| Núvol de punts dens | 38.547.923 punts |
| Sistema de coordenades de sortida | EPSG:32631 |
| Calibració de la càmera (Brown) | focal 1,0946 × amplada de sensor 23,5 mm ≈ **25,72 mm** (nominal 25 mm); k1 -0,1372, k2 0,1350, k3 0,1058, p1 -0,00012, p2 -0,00021 |
| Diferència model–GPS (desv. est.) | E 1,30 m · N 0,37 m · vertical 0,12 m; CE90 1,80 m, LE90 0,19 m (no és precisió absoluta; vegeu l'advertència 4) |

Temps per etapa (s, execució real): dataset 6, opensfm 641, openmvs 543, odm_filterpoints 70, odm_meshing 316, mvs_texturing 745, odm_georeferencing 194, odm_dem 39, odm_orthophoto 36, odm_report 81, odm_postprocess 36.
Entregables (ortofoto GeoTIFF, DSM, núvol LAZ/EPT, models OBJ/GLB, informe PDF): `resultats/all.zip`. Accés ràpid a l'informe i estadístiques: `report_odx/`.

### Revisió visual (8/10/2026)
- Ortofoto: 14.116 × 8.752 px a 1 cm/px; ~70 % del rectangle és zona vàlida (la graella està girada ~75°). Sense costures ni deformació «de bol» visibles; vies i rotondes coherents; nítida a escala 1:1 (juntes de formigó, fulles individuals).
- DSM: 7.057 × 4.376 px a 2 cm/px, 157,1–170,6 m (MSL). Interior net (edificis plans, arbres com a relleu); **franges i estries a la perifèria** (primera i última passada, vora NW i extrems), amb poques vistes: retallar el DSM al polígon d'interès o ampliar el pla de vol ~1 footprint més enllà de la zona.

## 5. Retard de l'obturador (`analisi/`)
Residu GPS − posició reconstruïda = −v·τ: té signe oposat a les passades d'anada i tornada, amb un desplaçament global ≈ 0 (+0,03, -0,02 m).
- **τ = 0,268 ± 0,009 s** (ENE 0,277 ± 0,007; WSW 0,267 ± 0,014).
- Residu horitzontal: mediana 1,38 m → 0,49 m després de corregir-lo (RMS 1,38 → 0,60 m). Vertical: desv. est. 0,12 m, independent de la velocitat.
- Límit: un desplaçament fix antena→càmera cap endavant es confon amb el retard (la velocitat és gairebé constant). Amb ell com a incògnita el retard surt 0,34 ± 0,03 s i el desplaçament 0,32 ± 0,16 m: no es poden separar.
- Context: en aquest vol no hi ha missatges `CAM` (feedback inactiu); la posició del `TRIG` és la de l'EKF a l'instant del comandament (coincideix amb `POS` a 0,000 s). El retard del banc (comandament→obturador, 0,12–0,19 s) no explica tot el 0,27 s del vol; la diferència pot ser el retard de posició GPS/EKF o un retard diferent en vol, i no es pot separar sense feedback.
- Fotos atípiques: DSC00082.JPG (v=1,4 m/s), DSC00187.JPG (v=3,7 m/s), DSC00094.JPG (v=5,0 m/s), a l'inici o als girs.
- Reproduir: `python analisi/estima_retard.py` (usa `proces/reconstruction.json` i `..\..\..\entrades\vol_*.bin`).

## 6. Pendent d'omplir (millora el report)
- Base RTK: quin SBC i programari va donar les correccions el 8/10 (la fitxa d'estat diu Orange Pi Zero 2W + `rtkbase` amb caster NTRIP local; una sessió anterior va configurar una Raspberry Pi Zero W amb `str2str` TCP :5000).
- Coordenades de la base RTK, mètode (survey-in / fixa) i durada del survey-in.
- Condicions: vent, llum/ombres, hora solar, estat del terreny.
- Punts de comprovació mesurats amb RTK a terra (per poder donar una precisió absoluta real).
- Dron (bastidor, massa) i bateria.

## 7. Contingut
```
README.md        aquesta fitxa
SHA256SUMS.txt       checksums de tots els fitxers
resultats/all.zip    ortofoto, DSM, núvol, models, informe (exportació completa de WebODM)
report_odx/          report.pdf, stats.json, shots.geojson, cameras.json
proces/              options.json, geo usat, log complet, benchmarks, reconstruction.json (OpenSfM)
analisi/             estima_retard.py + resultats
```
