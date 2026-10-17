# orion-registry

Официальный каталог плагинов [Orion](https://github.com/DirtyPlayBoy/ORION).

Байты плагина лежат на **GitHub Release** автора. В этом репозитории только pin:

`id` · `version` · `download URL` · `SHA-256`

## URL, который читает Orion

```
https://raw.githubusercontent.com/DirtyPlayBoy/orion-registry/main/registry/v1/index.json
```

Клиент: вкладка **Плагины** → каталог / CRM / обновления.

## Структура

```
plugins/<id>/plugin.json              identity (name, license, repo, caps)
plugins/<id>/versions/<semver>.json   one release pin (url + sha256)
registry/v1/index.json                generated catalogue (do not hand-edit)
policy/                               reserved ids, rules
schema/                               JSON Schema
tools/                                build-index · validate · security-scan
```

## Добавить плагин

### Через приложение Orion (рекомендуется)

1. **Плагины → CRM** (режим модератора)
2. Ссылка на GitHub-репозиторий + поля модерации
3. Download → security scan → Approve
4. Для публичного каталога — PR сюда с `plugins/<id>/` (см. ниже)

### PR в этот репозиторий

Из репозитория плагина ([OrionPlugins CLI](https://github.com/DirtyPlayBoy/OrionPlugins)):

```bash
python cli/orion_plugin.py pack .
python cli/orion_plugin.py submit . --repo Owner/Name
```

Скопируйте `submit/plugins/<id>/` в этот репозиторий, затем:

```bash
python tools/build-index.py
python tools/validate.py
```

Откройте PR. Первая заявка — ручная модерация ([POLICY.md](POLICY.md)).

### Формат version pin

```json
{
  "version": "0.1.0",
  "staging": false,
  "download_url": "https://github.com/Owner/Repo/releases/download/v0.1.0/my-plugin-0.1.0-windows-x64.orionplugin",
  "sha256": "<64 hex>",
  "release": {
    "kind": "github_release",
    "repository": "Owner/Repo",
    "tag": "v0.1.0"
  }
}
```

Staging (`"staging": true`) может быть без digest — в store не ставится.

## Инструменты

| Команда | Назначение |
|---------|------------|
| `python tools/build-index.py` | Пересобрать `registry/v1/index.json` |
| `python tools/validate.py` | Проверить listings + index + бренд-scrub |
| `python tools/security-scan.py <path.orionplugin>` | Локальный multi-layer scan |

## Связанные репозитории

- [ORION](https://github.com/DirtyPlayBoy/ORION) — приложение
- [OrionPlugins](https://github.com/DirtyPlayBoy/OrionPlugins) — SDK / CLI / examples

См. [POLICY.md](POLICY.md) и [CONTRIBUTING.md](CONTRIBUTING.md).
