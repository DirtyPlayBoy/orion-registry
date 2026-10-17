# orion-registry — карта для ИИ

Source of truth: `plugins/<id>/plugin.json` + `versions/<semver>.json`.
Generated: `registry/v1/index.json` via `python tools/build-index.py`.
Always run `python tools/validate.py` before commit.
Do not put `.orionplugin` binaries here. Do not hand-edit digests in index.
Client URL: `https://raw.githubusercontent.com/DirtyPlayBoy/orion-registry/main/registry/v1/index.json`
