FROM python:slim

RUN apt-get update && \
		apt-get install curl -y && \
		curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY ./poetry.lock ./pyproject.toml ./

RUN /root/.local/bin/poetry install --only main

COPY . .

EXPOSE 8000

CMD /root/.local/bin/poetry run alembic upgrade head && \
		/root/.local/bin/poetry run uvicorn app:app --port 8000 --host 0.0.0.0
