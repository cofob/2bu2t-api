#!/usr/bin/env bash

export DB_URL="cockroachdb+asyncpg://root@localhost:26257/defaultdb"

docker rm -f roach || true
docker run -d --rm \
	--name roach --net host --hostname roach \
	cockroachdb/cockroach:v22.1.7 start-single-node --insecure

sleep 3

poetry run alembic upgrade head
