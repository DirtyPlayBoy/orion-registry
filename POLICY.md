# Catalog policy

## Требования к плагину

- Полезный, документированный, лицензия OSI-approved SPDX (предпочтительно MIT / Apache-2.0).
- Reserved id: `orion-stt`, `orion-tts`, `orion-core`, `orion-agent`, `orion-voice` (см. `policy/reserved-ids.json`).
- High-risk permissions (`dom_access`, `client`, `send_chat_message`, `set_theme_contribution`) — явный review.
- Запрещены malware, кража credentials, скрытая эксфильтрация данных.
- Artifact URL только HTTPS; для non-staging обязателен SHA-256.
- Staging (`"staging": true`) может быть без digest и **не ставится** кнопкой store.

## Security gate (обязательно)

Каждый non-staging артефакт проходит multi-layer scan до CRM Approve / merge в CI:

1. **SHA-256** pin совпадает с байтами
2. **Archive safety** — no zip-slip, no forbidden binaries (`.exe`, `.dll`, `.bat`, …)
3. **Python AST heuristics** — block `eval` / `exec` / `os.system` / `ctypes.windll` / `pickle.loads` / …
4. **Windows Defender** (`MpCmdRun`), когда доступен на машине ревьюера / CI runner

## Orion CRM flow

1. `Fetch GitHub Release` или submit `.orionplugin` / ссылка на repo → inbox  
2. Automatic scan (+ **Rescan** перед Approve)  
3. Approve только если scan clean → local CRM catalogue overlay  
4. Клиенты обновляются через **Плагины → CRM / Обновить** (download → scan again → install)

Ни один сканер не идеален: defense-in-depth + human CRM review обязательны для первых заявок.

## Публичный каталог (этот репозиторий)

- Source of truth: `plugins/<id>/plugin.json` + `versions/<semver>.json`
- `registry/v1/index.json` **только** через `python tools/build-index.py`
- PR без валидного `validate.py` не принимается
- Официальные examples pin’ятся на Release tags `examples-v*` в [OrionPlugins](https://github.com/DirtyPlayBoy/OrionPlugins)
