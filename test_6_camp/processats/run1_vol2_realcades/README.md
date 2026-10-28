# Test 6 (13/10/2026, alba) — vol 2 realçat: arxiu del processat

> Context i fotos: `../../README.md`. Integritat: `SHA256SUMS.txt` (`sha256sum -c SHA256SUMS.txt` des d'aquesta carpeta).

## 1. Què és (i què no)
Prova per veure si unes fotos **molt subexposades** (vol a l'alba) es poden aprofitar. Es processa **només el vol 2** (110 fotos): al vol 1 el guany ×551 no recupera senyal (2 coincidències entre fotos consecutives, igual que el soroll) i s'ha descartat.
Les 110 fotos s'han **realçat digitalment** (guany lineal ×2 a ×97, mediana ×49; `../../georef/realcat_guanys.csv`) abans de processar. **La geometria és vàlida; els colors i els valors radiomètrics no ho són** (to verd-blavós, soroll alt).

## 2. Advertències que cal reflectir al report
1. **Imatges modificades:** no s'han de fer servir per a color, índexs de vegetació ni cap mesura radiomètrica. Els originals sense tocar són a `../../fotos_originals/`.
2. **Llum:** sol a −3,2° (vol 1) i −0,1° a +0,8° (vol 2); fotos 6 *stops* subexposades a ISO 1600 (sostre de l'ISO automàtic), 1/1600 s, f/5,6. Repetir amb el sol a >10–15°.
3. **Qualitat inferior al test 5:** error de reprojecció 1,82 px (0,90 al test 5) i 101.094 punts (173.000 en una zona més petita); la perifèria oest té contorn irregular i estries al DSM (poques vistes).
4. **No hi ha GCP ni punts de comprovació:** cap precisió absoluta. La posició absoluta depèn de la base RTK (SBC, coordenades i mètode, per confirmar).
5. **Hora de la càmera** desfasada +9,04 h respecte a UTC; les hores del report d'ODX són hora de càmera.
6. Vol a ~50 m sobre el punt d'enlairament (no 30 m): GSD 0,743 cm/px.
7. Opcions diferents del test 5: `orthophoto-resolution` 3 cm/px (era 1) i `dem-resolution` 5 cm/px (era 2), perquè el soroll de les imatges fa preferir treballar a 3000 px.

## 3. Resultats (de `report_odx/stats.json`)
| | |
|---|---|
| Fotos reconstruïdes | 110 de 110 (components: 1) |
| Punts del model dispers / observacions | 101.094 / 354.361 |
| Error de reprojecció | 1,82 px |
| GSD mitjà / àrea | 0,743 cm/px / 30.626 m² |
| Núvol de punts dens | 27.207.845 punts |
| Sistema de coordenades de sortida | EPSG:32631 |
| Calibració (Brown) | focal 25,79 mm; k1 -0,1343, k2 0,1314, k3 0,0676 |
| Diferència model–GPS (desv. est. E / N / vertical) | 0,30 / 0,32 / 0,30 m; CE90 0,57 m, LE90 0,27 m (no és precisió absoluta) |
| Temps | 29 min 42 s segons ODX; suma d'etapes 30 min 45 s |

## 4. Retard residual de les posicions `CAM` (`analisi/`)
Aquestes fotos es geoetiqueten amb el missatge `CAM` (feedback de la sabata, instant real de l'obturador), no amb el `TRIG`. Mateixa anàlisi que al test 5 (GPS − posició reconstruïda = −v·τ):
- **τ residual = -0,056 ± 0,011 s** (els dos sentits: -0,060, -0,048). Negatiu: la posició `CAM` va uns 56 ms *per davant* de l'exposició (~0,28 m a 5 m/s).
- Retard `TRIG`→`CAM` mesurat al log: mediana 0,34 s (mitjana 0,31–0,33; rang 0,11–0,40 s). Retard `TRIG`→exposició = 0,34 − 0,056 ≈ **0,28 s**, d'acord amb els 0,268 s estimats al test 5 per un camí independent.
- Residu horitzontal GPS(`CAM`) − model: mediana 0,59 m, RMS 0,77 m (vol recte, v > 3 m/s, n = 88: 0,49 / 0,63 m). Vertical: desv. est. 0,30 m.
- Atípiques: DSC00404.JPG (v=1,6 m/s, 1,83 m), DSC00322.JPG (v=2,7 m/s, 1,79 m), DSC00403.JPG (v=2,3 m/s, 1,51 m), als girs.
- Reproduir: `python analisi/estima_retard.py`.

## 5. Revisió visual
Ortofoto 7.799 × 7.071 px a 3 cm/px: camp, camins, corba del camí i un vehicle blanc reconeixibles; to verd-blavós i soroll visibles; contorn oest irregular. DSM 4.679 × 4.242 px a 5 cm/px: interior detallat (solcs, rodades), estries i quadrícula d'interpolació a la vora oest/nord-oest.

## 6. Processament
ODX 3.8.3 directe (no surt a la base de dades de WebODM; es pot *Importar* `resultats/all.zip`) · i5-10400F, 32 GB, RTX 2060 · opcions no per defecte: `orthophoto-resolution` 3 · `pc-quality` high · `dem-resolution` 5 · `dsm` sí, `auto-boundary` sí, `cog` sí, `gltf` sí, `pc-ept` sí · `max-concurrency` 8. Ordre: `proces/comanda_execucio.bat` (calen `NoDefaultCurrentDirectoryInExePath` buit en aquest entorn). Log: `proces/task_output.txt`.

## 7. Contingut
```
README.md      aquesta fitxa
SHA256SUMS.txt     checksums
resultats/all.zip  ortofoto GeoTIFF, DSM, núvol LAZ/EPT, models OBJ/GLB, informe
report_odx/        report.pdf, stats.json, shots.geojson, cameras.json
proces/            options, geo usat (posicions CAM), log, benchmark, reconstruction.json, comanda d'execució
analisi/           estima_retard.py (CAM) + resultats
```
