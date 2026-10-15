# orion-registry

Каталог плагинов Orion. Байты лежат на GitHub Release автора; здесь только pin:

`id` · `version` · `download URL` · `SHA-256`

## URL, который читает Orion

```
https://raw.githubusercontent.com/DirtyPlayBoy/orion-registry/main/registry/v1/index.json
```

## Структура

```
plugins/<id>/plugin.json              identity
plugins/<id>/versions/<semver>.json   one release
registry/v1/index.json                generated catalogue
policy/                               reserved ids, rules
schema/                               JSON Schema
```

## Добавить плагин (рекомендуемый путь)

Из репозитория плагина (см. [OrionPlugins CLI](https://github.com/DirtyPlayBoy/OrionPlugins)):

```bash
python cli/orion_plugin.py pack .
python cli/orion_plugin.py submit . --repo Owner/Name
```

Скопируйте `submit/plugins/<id>/` сюда, затем:

```bash
python tools/build-index.py
python tools/validate.py
```

Откройте PR. Первая заявка — ручная модерация.

См. [POLICY.md](POLICY.md). Дизайн pin-by-digest вдохновлён [astra-registry](https://github.com/mihailinl/astra-registry).
