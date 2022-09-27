from os import environ

import pytest

from app.ipfs import IPFSClient

client = IPFSClient(environ["IPFS_URL"])


@pytest.mark.asyncio
async def test_add_bytes() -> None:
    async with client as session:
        cid = await session.add_bytes(b"test", "text/plain")
        assert cid == "QmRf22bZar3WKmojipms22PkXH1MZGmvsqzQtuSvQE3uhm"


@pytest.mark.asyncio
async def test_add_file() -> None:
    async with client as session:
        cid = await session.add_file("dummy.txt", "text/plain")
        assert cid == "QmRJaHfsTiD5JfhGju8EUKATgKYPn4jgexTipVLCTKEg6j"


@pytest.mark.asyncio
async def test_remove_cid() -> None:
    async with client as session:
        await session.remove("QmRJaHfsTiD5JfhGju8EUKATgKYPn4jgexTipVLCTKEg6j")
        await session.remove("bafybeidlkbnqjddmsowjmbvrfrt7b54qqjxwrlmtvmdfpah5qqo72rvxvm")
