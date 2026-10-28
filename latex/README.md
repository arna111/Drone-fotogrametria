# Sistema d'aerofotogrametria de precisió amb base RTK pròpia

Font LaTeX de l'informe. Compila a PDF en català (`main.pdf`, versió font) i en anglès (`main_en.pdf`).

## Estructura

```
latex/
├── main.tex                          # document principal en català (portada, resum, parts)
├── main_en.tex                       # edició en anglès (mateixa estructura i etiquetes)
├── parts/
│   ├── 01_construccio/
│   │   ├── construccio.tex           # cap. 1: disseny, materials i muntatge
│   │   └── manual.tex                # cap. 2: manual d'operació i procediments
│   ├── 02_proves_vol/
│   │   └── proves_vol.tex            # cap. 3: proves de vol, autonomia i grup propulsor
│   ├── 03_vols/
│   │   └── vols_prova.tex            # cap. 4: vols de fotogrametria (proves 5 i 6)
│   └── 02_surveys/
│       └── survey_template.tex       # plantilla opcional per a nous vols (no inclosa)
├── parts_en/                         # capítols de l'edició en anglès (mateixa estructura que parts/)
├── img/                              # fotos del muntatge i figures dels resultats
├── bib/referencies.bib               # bibliografia (català)
├── bib/references_en.bib             # bibliografia (anglès)
└── README.md
```

## Afegir un nou vol

1. Copia l'estructura d'una secció de `parts/03_vols/vols_prova.tex` (equip i vol, resultats, figures) o la plantilla de `parts/02_surveys/survey_template.tex`.
2. Etiquetes úniques amb prefix (`sec:`, `fig:`, `tab:`), p. ex. `fig:vol7-ortofoto`.
3. Les figures (ortofoto i DSM) es generen reduïdes des de l'`all.zip` de cada processat i es guarden a `img/`.

## Compilar

```
latexmk -pdf main.tex
```

Manualment: `pdflatex main.tex`, `biber main`, `pdflatex main.tex` (dues vegades). Si el PDF surt amb `??`, falta una passada de compilació.

## Convencions

- Cada etiqueta amb el seu prefix (`chap:`, `sec:`, `fig:`, `tab:`); mai repetida.
- Referències creuades amb `\cref{}` (noms en català definits a `main.tex`).
- No usar el caràcter `"` dins de llegendes ni títols (el `babel` català el converteix en una drecera activa); escriure «polzades».
- Bibliografia: entrades a `bib/referencies.bib`, cites amb `\cite{clau}`; cal `biber`.
- L'edició en anglès (`main_en.tex`, `parts_en/`) és una traducció manual del català: cada canvi a `parts/` s'ha de reflectir a `parts_en/`, amb les mateixes etiquetes. Compilar-la: `latexmk -pdf main_en.tex`.
