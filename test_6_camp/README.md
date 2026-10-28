# Test 6 (13/10/2026, alba) — índex del projecte

Dos vols de prova a ~50 m (~180 × 150 m) amb el mateix quad i càmera que el test 5 (`../test_5_parc/`), amb els paràmetres de bateria ja corregits. **Fets a l'alba (sol de −3° a +1°): les fotos van sortir molt fosques.** Aquest lot serveix de prova, no de producte: es repetirà amb el sol alt.

## Estructura
```
README.md           aquest índex
entrades/               logs dels dos vols (.bin)
fotos_originals/        204 JPG de la SD, sense tocar (còpia amb hash verificat)
fotos_corregides/       204 JPG amb EXIF corregit (Orientation=1, òptica, f/5,6, GPS); píxels intactes
fotos_realcades/        110 JPG del vol 2 amb guany digital (×2 a ×97) — NOMÉS per a geometria
georef/                 geotags.csv, geo.txt (vol 2, posicions CAM), realcat_guanys.csv, geotags_exif.csv
eines/                  prepara_fotos_vol6.py (usa postproces_fotos.py i exiftool de ../test_5_parc/eines)
processats/
  run1_vol2_realcades/  processat de les 110 fotos realçades (fitxa, checksums, all.zip, analisi)
```

## Què diuen els logs
| | Vol 1 (07:46) | Vol 2 (07:57) |
|---|---|---|
| mAh consumits (`CurrTot` / integral) | **2.326** / 2.306 | **2.434** / 2.426 |
| Motors en marxa | 5,5 min | 11,3 min (dos armats) |
| Tensió inicial / mínima / final | 24,65 / 21,25 / 21,95 V | 24,73 / 21,13 / 21,95 V |
| Corrent mitjà / màxim | 25 / 56 A | 22 / 58 A |
| Failsafe de bateria baixa | 268 s, 21,52 V, **1.887 mAh** | 635 s, 21,48 V, **2.012 mAh** |
| Disparos `TRIG` / feedback `CAM` / fotos | 94 / 93 / 94 | 110 / 110 / 110 |

- **Bateria:** els dos vols acaben per *bateria baixa* quan només s'ha gastat ~47–50 % dels 4.000 mAh: la tensió instantània cau per sota de 21,6 V sota càrrega (`BATT_FS_VOLTSRC` = 0). Paràmetres del vol: `BATT_VOLT_MULT` 10,82, `BATT_AMP_PERVLT` 87,73. Comparar els mAh amb el que torna el carregador (+5–10 % de pèrdues).
- **Fotos fosques:** 1/1600 s, f/5,6, ISO 1600 (sostre de l'ISO automàtic). Llum d'escena 11,9 (vol 1) i 8,5 (vol 2) *stops* per sota del vol del 8/10 (sol a 40°). Marge màxim de la càmera: 5,7 *stops*. **Cap avaria**: el sol era a −3,2° / ~0°.
- **Aparellament foto↔log per temps** (no per ordre): `DSC00207` és una foto manual sense `TRIG` (14:45:17) i el primer `TRIG` del vol 1 no té ni `CAM` ni foto. Rellotge de la càmera +9,04 h respecte a UTC.
- **Retard de l'obturador:** `TRIG`→`CAM` mediana 0,34 s (0,11–0,40). Amb posicions `CAM` el retard residual és −0,056 ± 0,011 s, o sigui `TRIG`→exposició ≈ 0,28 s, igual que els 0,268 s del test 5 (mètode independent).

## Resultat del processat (vol 2 realçat)
110 de 110 fotos reconstruïdes, 1 component, reprojecció 1,82 px (0,90 al test 5), GSD 0,743 cm/px, ~3 ha, 29 min 42 s. Ortofoto i DSM coherents però amb soroll, color no fidel i vora oest irregular. El vol 1 no és aprofitable (2 coincidències entre fotos consecutives, igual que el soroll). Detalls i advertències: `processats/run1_vol2_realcades/README.md`.

## Com es regenera
`python eines/prepara_fotos_vol6.py corregides` (fotos corregides, geotags amb `CAM`, `geo.txt`) i després `... realcades`. El processat és la comanda de `processats/run1_vol2_realcades/proces/comanda_execucio.bat` (cal buidar `NoDefaultCurrentDirectoryInExePath` dins del `.bat`).

## Pendent
- **Repetir el vol amb el sol a >10–15°** (≈1 h després de la sortida del sol a l'octubre). Si cal volar amb poca llum: 1/800 s, f/4, ISO 3200 al límit.
- **Bateria:** decidir si `BATT_FS_VOLTSRC` = 1 (tensió compensada per la caiguda) per no activar el failsafe per càrrega; verificar els mAh amb el carregador.
- **Posicions `CAM`:** van ~0,056 s per davant de l'exposició (~0,3 m a 5 m/s); es pot corregir amb τ = −0,056 s si interessa.
- **Base RTK** del 8/10 i del 13/10: SBC, coordenades i mètode (per confirmar). **Punts de comprovació** a terra per afirmar una precisió absoluta.
