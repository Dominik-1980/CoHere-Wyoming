# CoHere-Wyoming

**Lokale Cohere-Transcribe-Spracherkennung für Home Assistant und andere Wyoming-Clients**

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/dominik_w)
[![Support with PayPal](https://img.shields.io/badge/PayPal-Support-003087?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/DominikWeiland)

<img src="assets/logo.png" alt="CoHere-Wyoming Logo" width="240">

[English](README.md) · Deutsch

`Wyoming-Client → CoHere-Wyoming → Text`

Führt das unquantisierte Modell **Cohere Transcribe 03-2026** lokal auf einer
Linux-CPU aus. Grundlage ist das Transformers-Backend von
[Agent CLI](https://github.com/basnijholt/agent-cli).
Keine Cohere-API, kostenpflichtige Inferenz, GPU oder HA-Zugangsdaten nötig.
Das Modell bleibt geladen. Deutsch ist voreingestellt; Wyoming meldet alle
14 unterstützten Modellsprachen.

Ein unabhängiges Community-Projekt, kein offizielles Produkt von Cohere oder
Home Assistant. Das Image wird aktuell für **Linux/amd64** gebaut.

## Voraussetzungen

- Linux-Rechner mit 64-Bit-x86-CPU, die die PyTorch-CPU-Wheels unterstützt.
- Rund **4,2 GB Modelldownload** plus Speicher für Image und Cache.
  Das 2-Milliarden-Parameter-Modell läuft mit float32. Die Compose-Vorlage setzt
  ein Limit von **16 GiB RAM und 6 CPUs**.
- Für den ersten Download: Zugang zum
  [offiziellen Modell auf Hugging Face](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026).
  Dort die Zugangsbedingungen akzeptieren und einen Lese-Token erstellen.
- Vertrauenswürdiges lokales Netzwerk; Wyoming und HTTP-API haben keine Anmeldung.

Die Spracherkennung verarbeitet Audiodaten lokal. Image- und erster
Modelldownload benötigen Internet. Nach erfolgreichem Download wird der Cache
ohne erneuten Download verwendet. Python-Code aus dem Modellrepository wird
weder geladen noch ausgeführt.

## Start mit Docker Compose

```sh
git clone https://github.com/Dominik-1980/CoHere-Wyoming.git
cd CoHere-Wyoming
mkdir -p secrets
chmod 700 secrets
```

Mit einem lokalen Texteditor `secrets/hf_token` erstellen. Die Datei enthält
**nur den Hugging-Face-Lese-Token**. Privat halten und für den Containerbenutzer
lesbar machen (Standard UID/GID 1000:1000). Die Datei ist von Git und dem
Image-Build ausgeschlossen.

```sh
docker compose -f compose.yaml -f compose.hf-token.yaml up -d
docker compose logs -f cohere-wyoming
```

Der erste Start lädt das festgelegte offizielle Modell und prüft dessen Hash.
Das kann mehrere Minuten dauern. Erst mit geladenem Modell wird der Container
als gesund gemeldet. Anschließend kann die Token-Erweiterung entfallen:

```sh
docker compose up -d
```

Das Volume `cohere-data` enthält Modell und Cache. Bei Updates behalten.
Status: `http://DEIN_SERVER:10325/health`.
API-Dokumentation: `http://DEIN_SERVER:10325/docs`.

## Home Assistant und Noise Cancelling Proxy

Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen →
Wyoming Protocol** die Serveradresse und Port **10324** eintragen.
Die neue STT-Entität in der Assist-Pipeline auswählen.
[Offizielle HA-Anleitung](https://www.home-assistant.io/integrations/wyoming/).

Optional mit unserem
[Wyoming Noise Cancelling Proxy](https://github.com/Dominik-1980/wyoming-noise-cancelling-proxy):

`Home Assistant → Noise Cancelling Proxy → CoHere-Wyoming`

Im Proxy das STT-Ziel auf die Serveradresse dieses Containers und Port
**10324** setzen. Home Assistant verbindet sich dann mit dem Proxy
(Standardport **10322**).
Im selben Docker-Netz lautet das interne Ziel `cohere-wyoming:10300`.
`127.0.0.1` in einem Container bezeichnet ausschließlich diesen Container.

## Ports und Konfiguration

| Hostport | Containerport | Verwendung |
| --- | --- | --- |
| 10324/TCP | 10300/TCP | Wyoming-Spracherkennung |
| 10325/TCP | 10301/TCP | HTTP-Status, API und API-Dokumentation |

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `LANGUAGE` | `de` | Standardsprache |
| `OMP_NUM_THREADS`, `MKL_NUM_THREADS` | `6` | CPU-Threads |
| `MODEL_DIR` | `/data/model` | Modellverzeichnis |
| `MODEL_DOWNLOAD` | `1` | `0`: vorhandenes Modell ohne Download validieren |
| `HF_TOKEN_PATH` | `/run/secrets/hf_token` | Datei mit Hugging-Face-Token |
| `HF_TOKEN` | nicht gesetzt | Alternative per Umgebungsvariable; Datei bevorzugen |

Sprachcodes: `ar de el en es fr it ja ko nl pl pt vi zh`.
Wyoming-Clients können eine unterstützte Sprache pro Anfrage auswählen.
Compose verwendet `CPU_THREADS`, `PUID` und `PGID` zur entsprechenden
Containerkonfiguration. Appdata-Bindmounts müssen vom gewählten Benutzer
beschreibbar sein.

Ein bereits heruntergeladenes natives Modell kann unter `/data/model`
bereitgestellt und mit `MODEL_DOWNLOAD=0` gestartet werden.
Architektur, Konfiguration, Tokenizer, Gewichtsgröße und offizieller SHA-256
werden geprüft. Die Modellrevision steht in [model-manifest.json](model-manifest.json).
Beliebige alternative oder quantisierte Modelle sind nicht vorgesehen.

## Unraid

[unraid/cohere-wyoming.xml](unraid/cohere-wyoming.xml) importieren.
Die Vorlage enthält das vollständige Logo **inklusive Schrift**, Ports,
Ressourcenlimits und den eigenen Appdata-Pfad
`/mnt/user/appdata/cohere-wyoming`. Benutzer: UID99/GID100.

Für eine Neuinstallation die XML-Datei als
`/boot/config/plugins/dockerMan/templates-user/my-cohere-wyoming.xml` ablegen.
Danach unter **Docker → Add Container (Container hinzufügen)** die Benutzervorlage
`cohere-wyoming` auswählen und die Konfiguration übernehmen. Eine vorhandene
Vorlage vor dem Ersetzen sichern. DockerMan ergänzt beim Erstellen automatisch
`net.unraid.docker.managed=dockerman`.

**Bestehende CLI-/Compose-Container:** Das Ablegen der XML übernimmt einen bereits
laufenden Container nicht nachträglich in DockerMan; er kann weiterhin unter
**3rd Party** erscheinen. Für die Übernahme zunächst seine Konfiguration sichern
und ihn über die Unraid-Vorlage neu anlegen. Modell-/Appdata-Mount und Portzuordnung
beibehalten. Den bisherigen Container vor Wiederverwendung von Name und Ports
stoppen und erst nach erfolgreicher Prüfung des Ersatzes entfernen. Modell und
Appdata behalten. Das allgemeine Docker-/Compose-Image setzt kein DockerMan-Label.

Für den ersten Download eine private, für UID99/GID100 lesbare Datei
`/mnt/user/appdata/cohere-wyoming/hf_token` anlegen.
Appdata wird nach `/data` gemountet; die Vorlage setzt
`HF_TOKEN_PATH=/data/hf_token`. Nach erfolgreichem Download darf die
Token-Datei entfernt werden. Appdata und Exporte mit Zugangsdaten nicht teilen.

## Verhalten und Grenzen

- Wyoming-Audio wird bis `audio-stop` gepuffert und anschließend transkribiert.
  Keine fortlaufenden Teiltranskripte.
- **16 kHz, Mono, PCM16** empfohlen; der Wyoming-Adapter passt eingehendes PCM
  an. HTTP unterstützt passende WAV-Dateien. FFmpeg und Konvertierung
  komprimierter Uploads sind nicht enthalten.
- Keine Erkennung des Sprechendes, Wake Words, Sprachausgabe, Geräteaktionen,
  Aufzeichnungsoberfläche, Sprechertrennung oder Rauschfilterung.
- Das Modell bleibt geladen. Lange Aufnahmen benötigen mehr Ressourcen;
  maximal 512 generierte Tokens. Anfragen kurz halten.
- Erkennungsqualität und Antwortzeit hängen von Audio, Sprache und CPU ab.
- Der angepasste Wyoming-Handler schreibt erkannte Texte nicht ins Log.
  HTTP-API und Clients haben eigenes Verhalten; sensible Anfragen nicht mit
  Debug-Protokollierung betreiben.
- Beide Ports im vertrauenswürdigen Netzwerk halten.

## Prüfen und entwickeln

```sh
python3 -m unittest discover -s tests -v
docker build -t cohere-wyoming:local .
docker run --rm --network none --entrypoint python -v "$PWD/tests:/tests:ro" cohere-wyoming:local -m unittest discover -s /tests -v
python3 scripts/smoke_test.py --host DEIN_SERVER
```

Der Standard-Smoke-Test fragt nur Wyoming-Fähigkeiten ab.
Mit `--wav /pfad/test.wav` lässt sich eine lokale WAV-Datei direkt
transkribieren (16 kHz, Mono, PCM16). Keine HA-Verbindung und keine Geräteaktion.

CI baut das Image und prüft Modellvalidierung, Offline-Start, sichere
Quellpatches und echte installierte Wyoming-Metadaten ohne Modelldownload.
Modellinferenz wird separat geprüft. Persönliche Aufnahmen und Transkripte
gehören nicht ins Repository.

Tags veröffentlichen `ghcr.io/dominik-1980/cohere-wyoming:0.1.1` und
`:latest` mit SBOM und Build-Herkunft. Siehe [CHANGELOG](CHANGELOG.md).
Direkte Laufzeitversionen und Modellrevision sind festgelegt; transitive
Pakete und das Basisimage können sich beim Neubau ändern.
Für einen exakt wiederholbaren Einsatz den veröffentlichten Image-Digest behalten.

## Updates, Rückweg und Lizenzen

Vor Updates bisheriges Image (Tag/Digest), Vorlage und Einstellungen sichern.
`/data` behalten. Für den Rückweg das bisherige Image mit den gespeicherten
Einstellungen und demselben Datenmount verwenden. Das Image ändert keine
HA-Konfiguration.

Eigener Adaptercode, Skripte und Dokumentation: **MIT**.
Agent CLI von Bas Nijholt: **MIT**. Separat heruntergeladenes Cohere-Modell:
**Apache-2.0**. Alle Abhängigkeiten behalten ihre jeweiligen Lizenzen.
[LICENSE](LICENSE), [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md)
und [Lizenzen](licenses/) enthalten die Zuordnung.
Im Image bleiben Originalhinweise erhalten; eine Paketübersicht liegt unter
`/app/licenses/python-packages.json`. Markenrechte verbleiben bei ihren Inhabern.

