# CoHere-Wyoming

**Local Cohere Transcribe speech recognition for Home Assistant and other Wyoming clients**

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white)](https://ko-fi.com/dominik_w)
[![Support with PayPal](https://img.shields.io/badge/PayPal-Support-003087?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/DominikWeiland)

<img src="assets/logo.png" alt="CoHere-Wyoming logo" width="240">

English · [Deutsch](README.de.md)

`Wyoming client → CoHere-Wyoming → text`

Runs the unquantized **Cohere Transcribe 03-2026** model locally on a Linux CPU,
using the Transformers backend of [Agent CLI](https://github.com/basnijholt/agent-cli).
No Cohere API key, paid inference service, GPU, or Home Assistant token is required.
The model stays loaded between requests. German is the default; the model's
14 supported languages are advertised over Wyoming.

This is an independent community integration, not an official Cohere or
Home Assistant product. The image is currently built for **Linux/amd64**.

## Requirements

- A 64-bit x86 Linux host with a CPU capable of running the PyTorch CPU wheels.
- Approximately **4.2 GB of model downloads**, additional cache/image storage,
  and sufficient RAM for a 2-billion-parameter model loaded as float32.
  The supplied Compose configuration reserves up to **16 GiB RAM and 6 CPUs**.
- First download: a Hugging Face account with access to the
  [official gated model](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026).
  Accept its access conditions and create a read token.
- A trusted local network. Wyoming and the HTTP API have no authentication.

Audio stays on your machine during recognition. Initial image/model downloads
need internet access. After a successful download the same cached model starts
offline; no remote model Python is executed.

## Quick start

Clone this repository and open its directory:

```sh
git clone https://github.com/Dominik-1980/CoHere-Wyoming.git
cd CoHere-Wyoming
mkdir -p secrets
chmod 700 secrets
```

Using a local text editor, create `secrets/hf_token` containing **only your
Hugging Face read token**. Keep this file private and readable by the container
user (UID/GID 1000:1000 by default). It is ignored by Git and excluded from the image.

```sh
docker compose -f compose.yaml -f compose.hf-token.yaml up -d
docker compose logs -f cohere-wyoming
```

The first start downloads and verifies the pinned official model. This can take
several minutes. The container becomes healthy only after the model is loaded.
On subsequent starts the model cache is reused. Once downloaded, the token
override can be removed:

```sh
docker compose up -d
```

The named volume `cohere-data` persists models and caches. Do not delete it during
an update. Check readiness at `http://YOUR_SERVER:10325/health`; API documentation
is at `http://YOUR_SERVER:10325/docs`.

## Home Assistant

In **Settings → Devices & services → Add integration → Wyoming Protocol**, enter
the container host's IP/hostname and **10324**. Select its speech-to-text entity
in your Assist pipeline. See the
[official HA instructions](https://www.home-assistant.io/integrations/wyoming/).

For optional noise reduction, use the companion
[Wyoming Noise Cancelling Proxy](https://github.com/Dominik-1980/wyoming-noise-cancelling-proxy):

`Home Assistant → Noise Cancelling Proxy → CoHere-Wyoming`

Set the proxy's STT target to the host running this container, port **10324**.
Home Assistant then connects to the proxy's Wyoming port (default **10322**).
Between containers on a shared Docker network use `cohere-wyoming:10300`.
A container's `127.0.0.1` refers to itself, not another container or the host.

## Ports and settings

| Host port | Container port | Purpose |
| --- | --- | --- |
| 10324/TCP | 10300/TCP | Wyoming speech-to-text |
| 10325/TCP | 10301/TCP | HTTP health, API and API docs |

| Variable | Default | Meaning |
| --- | --- | --- |
| `LANGUAGE` | `de` | Default recognition language |
| `OMP_NUM_THREADS`, `MKL_NUM_THREADS` | `6` | CPU worker thread limits |
| `MODEL_DIR` | `/data/model` | Local model directory |
| `MODEL_DOWNLOAD` | `1` | `0`: validate existing model without network/downloads |
| `HF_TOKEN_PATH` | `/run/secrets/hf_token` | Hugging Face token file |
| `HF_TOKEN` | unset | Alternative token environment variable; prefer a file |

Supported language codes:
`ar de el en es fr it ja ko nl pl pt vi zh`.
Wyoming clients can request a supported language per transcription.
In Compose, `CPU_THREADS`, `PUID` and `PGID` set the corresponding container values.
Bind-mounted appdata must be writable by the selected UID/GID.

For a pre-downloaded model, put the native checkpoint files in `/data/model`
and set `MODEL_DOWNLOAD=0`. The expected configuration, tokenizer, architecture,
weight size and official weight SHA-256 are checked before startup.
The source revision is pinned in [model-manifest.json](model-manifest.json);
arbitrary alternative or quantized models are not supported by this image.

## Unraid

Import [unraid/cohere-wyoming.xml](unraid/cohere-wyoming.xml). The template includes
the complete project logo **with its lettering**, ports, CPU/RAM limits and a
separate `/mnt/user/appdata/cohere-wyoming` path. It uses UID99/GID100.

For a new installation, save the XML as
`/boot/config/plugins/dockerMan/templates-user/my-cohere-wyoming.xml`, then use
**Docker → Add Container**, select the `cohere-wyoming` user template and apply
the configuration. Back up an existing template before replacing it.
DockerMan adds `net.unraid.docker.managed=dockerman` when it creates the container.

**Existing CLI/Compose containers:** copying the XML onto the server does not
adopt an already running container into DockerMan; it can still show **3rd Party**.
To move it into DockerMan, save its current configuration and recreate it through
the Unraid template, preserving its model/appdata mount and port mappings.
Stop the previous container before reusing its name and ports. Remove the old
container only after the replacement is healthy; keep the model/appdata files.
The generic Docker/Compose image does not declare itself DockerMan-managed.

For the initial gated download, create a private token file at
`/mnt/user/appdata/cohere-wyoming/hf_token`, readable by UID99/GID100.
The template mounts appdata at `/data` and sets `HF_TOKEN_PATH=/data/hf_token`.
After a successful download the token file can be removed. Never share appdata
or template exports containing credentials.

## Behavior and limits

- Input is buffered until Wyoming `audio-stop`, then transcribed. This is
  utterance-based STT, not incremental live transcription.
- Use **16 kHz mono PCM16** audio. The Wyoming adapter converts incoming PCM
  to that format. The HTTP path supports valid PCM16/16 kHz/mono WAV uploads;
  FFmpeg and compressed audio conversion are not included.
- No voice activity detector, wake-word detection, TTS, intent execution,
  target-speaker separation, recording UI, or noise filtering is included.
- The model is kept resident (`--preload --ttl 0`). Longer recordings need more
  resources; results are limited to 512 generated tokens. Keep requests bounded.
- Accuracy and response time depend on audio, language and CPU. No universal
  real-time or recognition guarantee is made.
- The patched Wyoming handler does not log recognized text. The upstream HTTP
  API and client software have their own behavior; avoid debug logging of
  sensitive requests.
- Keep both ports inside a trusted network; do not expose them to the internet.

## Verification and development

```sh
python3 -m unittest discover -s tests -v
docker build -t cohere-wyoming:local .
docker run --rm --network none --entrypoint python -v "$PWD/tests:/tests:ro" cohere-wyoming:local -m unittest discover -s /tests -v
python3 scripts/smoke_test.py --host YOUR_SERVER
```

The default smoke check only requests Wyoming capabilities. To test recognition
directly, add `--wav /path/to/test.wav` for a local 16 kHz mono PCM16 WAV.
This does not connect to Home Assistant or execute device commands.

CI builds the image and tests model validation, offline starts, source-patch
drift detection and actual installed Wyoming metadata without downloading weights.
Model inference is a separate integration check; personal recordings and
transcripts are excluded from the repository.

Tagged releases publish `ghcr.io/dominik-1980/cohere-wyoming:0.1.1` and
`:latest` with an SBOM and build provenance. See [CHANGELOG](CHANGELOG.md).
Pinned direct runtime versions are in `requirements.txt` and the Dockerfile;
transitive packages and the base image can change on rebuild, so retain the
published image digest when an exact deployment is required.

## Updates and rollback

Save your current image tag/digest and container/template settings before
upgrading. Keep `/data`. Pull the desired version, then recreate the container.
For rollback, select the previous image and saved settings with the same data
mount. No Home Assistant configuration is changed by this image.

## Credits and licensing

Original integration/scripts/documentation: **MIT**.
Agent CLI: **MIT**, copyright Bas Nijholt. Cohere Transcribe model:
**Apache-2.0**, downloaded separately by the user. Wyoming, Transformers,
PyTorch and other dependencies retain their own licenses.

Read [LICENSE](LICENSE), [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md)
and [licenses/](licenses/). The image preserves dependency notices and includes
an inventory at `/app/licenses/python-packages.json`. Names and marks remain
with their respective owners.

