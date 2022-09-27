"""Module with IPFSClient."""

from typing import Tuple

import aiohttp

from ..exceptions import InvalidCIDException, IPFSException


class IPFSClient:
    """IPFS async HTTP API."""

    def __init__(self, endpoint: str, auth: Tuple[str, str] | None = None) -> None:
        """IPFS async HTTP API.

        Examples:
            >>> client = IPFSClient("http://127.0.0.1:9094", ("user", "p@ssword"))

        Args:
            endpoint: REST API url.
            auth: List containing basic auth [user, password].
        """
        self.session: aiohttp.ClientSession
        self.endpoint = endpoint
        self.auth = None
        if auth is not None:
            self.auth = aiohttp.BasicAuth(*auth)
        self.req = {"auth": self.auth}

    async def __aenter__(self) -> "IPFSClient":
        """With enter point."""
        self.session = await aiohttp.ClientSession().__aenter__()
        return self

    async def __aexit__(self, *exc) -> None:  # type: ignore
        """With exit point."""
        await self.session.__aexit__(*exc)
        del self.session

    @staticmethod
    def check_cid(cid: str) -> None:
        """Check if CID valid.

        Raises:
            InvalidCIDException: When CID invalid.
        """
        if len(cid) not in [46, 59]:
            raise InvalidCIDException()
        if not cid.isascii():
            raise InvalidCIDException()
        if cid.find(" ") != -1:
            raise InvalidCIDException()

    def _get_path(self, path: str) -> str:
        """Get endpoint path.

        Examples:
            >>> client._get_path("/add")
            http://127.0.0.1:9094/add

        Args:
            path: Endpoint path.

        Returns:
            str: Absolute endpoint path with host.
        """
        return self.endpoint + path

    async def _add_formdata(self, data: aiohttp.FormData, name: str | None = None) -> str:
        """Post formdata to `/add` cluster endpoint.

        Examples:
            >>> data = aiohttp.FormData()
            >>> data.add_field("file", open("example.txt", "rb"))
            >>> cid = await self._add_formdata(data)

        Args:
            data: aiohttp.FormData object.
            name: Pin name.

        Returns:
            str: File CID.
        """
        params = {"quieter": "true"}
        if name is not None:
            params["name"] = name
        async with self.session.post(self._get_path("/add"), params=params, data=data, **self.req) as response:
            if response.status != 200:
                raise IPFSException(detail="Cannot pin file")
            cid: str = (await response.json())["cid"]
        return cid

    async def add_file(self, file: str, content_type: str, filename: str | None = None, name: str | None = None) -> str:
        """Add file to IPFS cluster.

        Examples:
            >>> await client.add_file("README.md", "text/plain")
            QmedsYWGvd5DWqwn6Ev5ow5pSgdqDtzsvcDGWQMa1gokEb

        Args:
            file: Path to file that will be added.
            content_type: File content-type.
            filename: Filename.
            name: Pin name.

        Returns:
            str: File CID.
        """
        formdata = aiohttp.FormData()
        formdata.add_field("file", open(file, "rb"), content_type=content_type, filename=filename)
        return await self._add_formdata(formdata, name=name)

    async def add_bytes(
        self, data: bytes, content_type: str, filename: str | None = None, name: str | None = None
    ) -> str:
        """Add bytes to IPFS cluster.

        Examples:
            >>> await client.add_bytes(b"Hello from cofob!", "text/plain")
            QmdkTR6yFkXLh96DtAgBqW2bDGsxYKDTKZSLGgHkP8niyU

        Args:
            data: Bytes that will be added.
            content_type: File content-type.
            filename: Filename.
            name: Pin name.

        Returns:
            str: File CID.
        """
        formdata = aiohttp.FormData()
        formdata.add_field("file", data, content_type=content_type, filename=filename)
        return await self._add_formdata(formdata, name=name)

    async def remove(self, cid: str) -> None:
        """Remove CID from cluster.

        Examples:
            >>> await client.remove("QmRf22bZar3WKmojipms22PkXH1MZGmvsqzQtuSvQE3uhm")

        Args:
            cid: CID to remove.
        """
        self.check_cid(cid)
        async with self.session.delete(self._get_path(f"/pins/ipfs/{cid}"), **self.req) as response:
            if response.status not in [200, 404]:
                raise IPFSException(detail=f"Cannot remove CID {cid}")
