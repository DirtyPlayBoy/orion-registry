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

## Добавить плагин

1. Опубликуйте `.orionplugin` в своём Release.
2. Добавьте `plugins/<id>/plugin.json` + `versions/<semver>.json`.
3. Обновите `registry/v1/index.json` (или дождитесь CI `tools/build-index`).
4. Откройте PR. Первая заявка — ручная модерация.

См. [POLICY.md](POLICY.md) и [Astra registry design](https://github.com/mihailinl/astra-registry) (вдохновение: digest-pinning без хостинга байтов).
