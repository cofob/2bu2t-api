#!/usr/bin/env bash

export DB_URL="cockroachdb://root@localhost:26257/defaultdb"
export IPFS_URL="http://127.0.0.1:9094"

docker rm -f roach || true
docker run -d --rm \
	--name roach --net host \
	cockroachdb/cockroach:v22.1.7 start-single-node --insecure

docker rm -f ipfs || true
docker run -d --rm \
	--name ipfs -p 5001:5001 \
	ipfs/kubo

docker rm -f ipfs-cluster || true
docker run -d --rm \
	--name ipfs-cluster --net host \
	-e CLUSTER_RESTAPI_HTTPLISTENMULTIADDRESS="/ip4/0.0.0.0/tcp/9094" \
	ipfs/ipfs-cluster

sleep 1

poetry run alembic upgrade head
