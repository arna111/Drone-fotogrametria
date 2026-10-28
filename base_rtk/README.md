# Eines de la base RTK

Gestió dels registres i del survey-in de la base (Pi Zero W). Cal estar connectat al Wi-Fi `BaseRTK`.

| Fitxer | On va | Què és |
|---|---|---|
| `rtkbase` | Pi, `/usr/local/bin/rtkbase` | L'eina: tota la lògica |
| `rtkbase.service` | Pi, `/etc/systemd/system/` | Servei `str2str` (port 5000 + registre per sessions) |
| `base_rtk.py` | PC | Crida l'eina de la Pi per SSH i baixa els fitxers |

## Ús (des del PC)

```
python base_rtk.py llista
python base_rtk.py baixa [SESSIO|ultima] [-o CARPETA]
python base_rtk.py esborra SESSIO... | --abans N [-y]
python base_rtk.py survey [--estat] [--minuts N]
```

- **Sessió** = una arrencada del servei (normalment, una connexió d'alimentació de la base). Viu a `~/logs/sNNNN/` amb els fitxers horaris dins; `~/logs/actual` apunta a la sessió en curs.
- `baixa` uneix els fitxers de la sessió en un de sol (`base_sNNNN.rtcm3`) i en comprova la mida. Si hi ha notes de survey-in, baixa també `base_sNNNN_survey.txt`. No esborra res a la Pi.
- `esborra` demana confirmació i **mai esborra la sessió activa**.
- `survey` reinicia el survey-in i espera que sigui vàlid (error mitjà ≤ 2 m, mínim 300 s; són els valors guardats al receptor). Quan ho és, desa la posició ECEF i la precisió a `survey.txt` de la sessió activa. Amb `--estat` només el consulta. Mentre dura, el servei està aturat (el port 5000 no serveix) i es reengega sol al final, també si es tallen el SSH o es prem Ctrl-C.
- Les hores de les llistes són les del rellotge de la Pi, que no té RTC ni internet i pot ser errònia.

## Instal·lació / recuperació a la Pi

```
scp rtkbase rtkbase.service arnau@192.168.4.1:/tmp/
ssh arnau@192.168.4.1 "sudo install -m 755 /tmp/rtkbase /usr/local/bin/rtkbase && sudo install -m 644 /tmp/rtkbase.service /etc/systemd/system/rtkbase.service && sudo systemctl daemon-reload && sudo systemctl restart rtkbase"
```

La unitat anterior (sense sessions) queda a la Pi com `rtkbase.service.bak-sense-sessions`.
