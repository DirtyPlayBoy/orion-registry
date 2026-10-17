# Contributing to orion-registry

## Быстрый чеклист PR

1. Добавьте `plugins/<id>/plugin.json` и `plugins/<id>/versions/<semver>.json`
2. `python tools/build-index.py`
3. `python tools/validate.py` → OK
4. (Опционально) `python tools/security-scan.py path/to/file.orionplugin --sha256 <digest>`
5. Откройте PR в `main`

## Не делайте

- Не правьте digests вручную в `registry/v1/index.json`
- Не коммитьте бинарники / `.orionplugin` в этот репозиторий
- Не используйте reserved id из `policy/reserved-ids.json`
- Не добавляйте сторонние product-бренды в docs/metadata

## Версии

Имя файла = semver = поле `version` внутри JSON.

При нескольких версиях index берёт **наивысшую non-staging**; если все staging — последнюю по semver.
