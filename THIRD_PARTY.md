# Third-party software and model licensing

The top-level MIT license applies to this project's original integration,
scripts and documentation. It does **not** relicense dependencies, the model,
base operating system, or third-party trademarks.

## Agent CLI and build-time modifications

The runtime is Agent CLI **0.112.0**, copyright 2025 Bas Nijholt, under MIT.
Its complete original license is [preserved](licenses/agent-cli-MIT.txt).
Upstream source tag: `v0.112.0`, Git object
`654b4773ed2c2b0b5048adc8239a8c64f33d6fb0`.
The exact, fail-closed source changes are in [patch_backend.py](patch_backend.py);
modified files carry a change notice. No upstream ownership is claimed.

## Cohere model

[CohereLabs/cohere-transcribe-03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026)
is identified by its publisher as **Apache-2.0**. See the
[official announcement](https://cohere.com/blog/transcribe),
[license text](licenses/Apache-2.0.txt), and [pinned manifest](model-manifest.json).

The image contains neither weights nor a Hugging Face token. First use downloads
only data/tokenizer/weight files from the official repository after the user has
accepted any access conditions. No ungated third-party mirror is selected.
The weights' SHA-256 is verified before loading. Model repository Python is
neither downloaded nor executed. Cached operation is local.

The project's MIT license grants no rights in Cohere's name or corporate logo.
Our [project-specific logo](assets/README.md) is separate; no official
relationship or endorsement is implied.

## Other runtime components

Examples include Transformers and Accelerate (Apache-2.0), Wyoming (MIT),
PyTorch (BSD-style, with its own third-party notices), librosa (ISC), and
python-soundfile (BSD-style) using dynamically linked libsndfile (LGPL).
The image also includes the Python/Debian base image and their dependencies.

Original Python wheel license/notice files and Debian copyright notices are
retained in the image. The build generates `/app/licenses/python-packages.json`
with the **actual installed versions**, license metadata and license-file paths;
it is an inventory, not a claim that all packages share one license.
Debian copyright texts are in `/usr/share/doc/*/copyright`; source packages
corresponding to the installed Debian versions are available from
[Debian Sources](https://sources.debian.org/) and
[Debian Snapshot](https://snapshot.debian.org/). PyPI wheel metadata links to
the upstream source projects. Keep these notices when redistributing.

The publishing workflow attaches a dependency SBOM and provenance to the image.
The OCI license label identifies this integration's license; consult the SBOM
and installed notices for the full image.

