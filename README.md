# API

## Установка

1. Установите `poetry`
2. Введите `poetry install --only main`

## Настройка

Для запуска необходима 1 переменная окружения:
 - DB_URL: URL для подключения к базе данных (CockroachDB), например `cockroachdb+asyncpg://root@localhost:26257/defaultdb`

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
