# Changelog

## 0.1.1 — 2026-10-26

- Fix PyTorch's cache initialization for numeric container UIDs, including
  Unraid UID99/GID100, with an explicit user name and writable Torch cache path.
- CI now imports the native Transformers model classes under both default
  UID1000 and Unraid UID99 with a read-only root filesystem.
- First recommended release; supersedes the initial 0.1.0 image.

## 0.1.0 — 2026-10-26

- Initial public CoHere-Wyoming community release.
- Agent CLI 0.112.0 with native Transformers Cohere detection and accurate
  Wyoming model/language metadata; remote repository Python disabled.
- CPU float32 inference; German default; resident model and 14 language codes.
- Pinned official Cohere model revision and verified weight SHA-256.
- Official gated download using a user-provided token file; offline cache mode.
- Container logo with original lettering, Docker Compose and Unraid template.
- English/German documentation and separate project/dependency/model licenses.
- Model-free CI, image SBOM/provenance and direct Wyoming smoke-test utility.

