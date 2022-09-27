# API

## Установка

1. Установите `poetry`
2. Введите `poetry install --only main`

## Настройка

| Name          | Description                         | Required                             | Default    | Example                                                |
|---------------|-------------------------------------|--------------------------------------|------------|--------------------------------------------------------|
| DB_URL        | CockroachDB database connection URL | true                                 | --         | `cockroachdb+asyncpg://root@localhost:26257/defaultdb` |
| IPFS_URL      | IPFS cluster RESTAPI endpoint       | true                                 | --         | `http://127.0.0.1:9094`                                |
| IPFS_USERNAME | Basic auth username                 | false                                | none       | `admin`                                                |
| IPFS_PASSWORD | Basic auth password                 | true, if `IPFS_USERNAME` is not none | none       | `p@ssword`                                             |
| LOG_FILE      | Log file path                       | false                                | `logs.txt` | `/absolute/path/log.txt`                               |
| ORIGIN        | Allowed http origin                 | false                                | `*`        | `firesquare.ru`                                        |

## Запуск

Запуск осуществляется через uvicorn, например

```bash
poetry run uvicorn app:app --port 8000
```

## Рабочее окружение

1. Установите все зависимости `poetry install`
2. Добавьте pre-commit хуки `poetry run pre-commit install`

Тесты можно запустить командой `make test`

Применить форматирование можно командой `make format`

## Документация

OpenAPI документацию можно открыть на `/docs` вашего API.

## Лицензия

Лицензия находится в файле LICENSE.
