# Security

Use only on a trusted local network. Neither Wyoming nor the upstream HTTP API
authenticates clients. Both endpoints accept resource-intensive audio requests;
the adapter buffers an utterance in memory. Do not expose the ports publicly.

The image runs without root, with dropped capabilities and a read-only root
filesystem in Compose. Keep appdata and token files private. Hugging Face
credentials are read at runtime and never included in build arguments or Git.
Do not post tokens, personal audio, transcripts or appdata in issues.

For a suspected security problem, use GitHub's private vulnerability reporting
when enabled, or contact the maintainer privately through their GitHub profile.
Public issues are suitable for ordinary bugs with sanitized logs.

