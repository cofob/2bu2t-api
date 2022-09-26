# API

# TODO:
 - IPFS cluster authorization

## Установка

1. Установите `poetry`
2. Введите `poetry install --only main`

## Настройка

Для запуска необходима 1 переменная окружения:
 - DB_URL: URL для подключения к базе данных (CockroachDB), например `cockroachdb://root@localhost:26257/defaultdb?sslmode=disable`

## Запуск

Запуск осуществляется через uvicorn, например

```bash
poetry run uvicorn app:app --port 8000
```

## Документация

OpenAPI документацию можно открыть на `/docs` вашего API.
