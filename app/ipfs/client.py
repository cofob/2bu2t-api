"""Module with IPFSClient."""

import aiohttp

from ..exceptions import IPFSException


class IPFSClient:
    """IPFS async HTTP API."""

    def __init__(self, endpoint: str, auth: list[str] | None = None) -> None:
        """Init IPFSClient.

        Examples:
            >>> client = IPFSClient("http://127.0.0.1:9094", ["user", "p@ssword"])

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

    async def _add_formdata(self, data: aiohttp.FormData) -> str:
        """Post formdata to `/add` cluster endpoint.

        Examples:
            >>> data = aiohttp.FormData()
            >>> data.add_field("file", open("example.txt", "rb"))
            >>> cid = await self._add_formdata(data)

        Args:
            data: aiohttp.FormData object.

        Returns:
            str: File CID.
        """
        async with self.session.post(self._get_path("/add?quieter=true"), data=data, **self.req) as response:
            if response.status != 200:
                raise IPFSException()
            cid: str = (await response.json())["cid"]
        return cid

    async def add_file(self, file: str, content_type: str, filename: str | None = None) -> str:
        """Add file to IPFS cluster.

        Examples:
            >>> client.add_file("README.md", "text/plain")
            QmedsYWGvd5DWqwn6Ev5ow5pSgdqDtzsvcDGWQMa1gokEb

        Args:
            file: Path to file that will be added.
            content_type: File content-type.
            filename: Filename.

        Returns:
            str: File CID.
        """
        formdata = aiohttp.FormData()
        formdata.add_field("file", open(file, "rb"), content_type=content_type, filename=filename)
        return await self._add_formdata(formdata)

    async def add_bytes(self, data: bytes, content_type: str, filename: str | None = None) -> str:
        """Add bytes to IPFS cluster.

        Examples:
            >>> client.add_bytes(b"Hello from cofob!", "text/plain")
            QmdkTR6yFkXLh96DtAgBqW2bDGsxYKDTKZSLGgHkP8niyU


        Args:
            data: Bytes that will be added.
            content_type: File content-type.
            filename: Filename.

        Returns:
            str: File CID.
        """
        formdata = aiohttp.FormData()
        formdata.add_field("file", data, content_type=content_type, filename=filename)
        return await self._add_formdata(formdata)
