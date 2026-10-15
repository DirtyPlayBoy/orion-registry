# Catalog policy

- Plugins must be useful, documented, and licensed under an OSI-approved SPDX id (prefer MIT / Apache-2.0).
- Reserved id prefixes / names: `orion-stt`, `orion-tts`, `orion-core`, `orion-agent`, `orion-voice`.
- High-risk permissions (`dom_access`, `client`, `send_chat_message`, `set_theme_contribution`) require explicit review.
- No malware, credential theft, or silent data exfiltration.
- Artifact URLs must be HTTPS; digests are mandatory for non-staging releases.
- Staging entries (`"staging": true`) may lack digests and are not installable from the store button.
