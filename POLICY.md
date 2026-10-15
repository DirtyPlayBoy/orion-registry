# Catalog policy

- Plugins must be useful, documented, and licensed under an OSI-approved SPDX id (prefer MIT / Apache-2.0).
- Reserved id prefixes / names: `orion-stt`, `orion-tts`, `orion-core`, `orion-agent`, `orion-voice`.
- High-risk permissions (`dom_access`, `client`, `send_chat_message`, `set_theme_contribution`) require explicit review.
- No malware, credential theft, or silent data exfiltration.
- Artifact URLs must be HTTPS; digests are mandatory for non-staging releases.
- Staging entries (`"staging": true`) may lack digests and are not installable from the store button.

## Security gate (required)

Every non-staging artifact must pass Orion’s multi-layer scan before CRM approve / CI merge:

1. **SHA-256** pin matches the downloaded bytes  
2. **Archive safety** — no zip-slip, no forbidden binaries (`.exe`, `.dll`, `.bat`, …)  
3. **Python AST heuristics** — block `eval`/`exec`/`os.system`/`ctypes.windll`/`pickle.loads`/…  
4. **Windows Defender** (`MpCmdRun`) when available on the reviewer machine / CI runner  

Orion CRM flow:

1. `Fetch GitHub Release` or submit `.orionplugin` → inbox  
2. Automatic scan (and **Rescan** before Approve)  
3. Approve only if scan is clean → local CRM catalogue overlay  
4. Clients pull updates via **Плагины → CRM / Обновить** (download → scan again → install)

No scanner is perfect; defense-in-depth + human CRM review is mandatory for first submissions.
