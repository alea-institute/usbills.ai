"""
Basic Solr client for querying the local solr instance.
"""

# standard library imports
import os
from typing import List, Dict, Any, Optional

# third-party imports
import httpx

# Constants
SOLR_HOST = os.environ.get("SOLR_HOST", "localhost")
SOLR_PORT = int(os.environ.get("SOLR_PORT", 8983))
SOLR_PREFIX = os.environ.get("SOLR_PREFIX", "solr")
SOLR_PROTOCOL = os.environ.get("SOLR_PROTOCOL", "http")
SOLR_TIMEOUT = int(os.environ.get("SOLR_TIMEOUT", 30))
SOLR_PASSWORD = os.environ.get("SOLR_PASSWORD", "")


def get_solr_endpoint(host: str, port: int, prefix: str, protocol: str) -> str:
    """Generate the Solr endpoint URL.

    Args:
        host: Solr host
        port: Solr port
        prefix: Solr prefix
        protocol: Protocol (http or https)

    Returns:
        Solr endpoint URL
    """
    return f"{protocol}://{host}:{port}/{prefix}/"


def get_solr_headers(
    password: str = "", accept_mime_type: str = "application/json"
) -> Dict[str, str]:
    """Generate headers for Solr requests.

    Args:
        password: Solr password (default: "")
        accept_mime_type: Accepted MIME type (default: "application/json")

    Returns:
        Headers for Solr requests
    """
    headers = {
        "Accept": accept_mime_type,
        "Content-Type": "application/json",
    }

    if password:
        headers["Authorization"] = f"Basic {password}"

    return headers


def construct_solr_params(**kwargs) -> Dict[str, str]:
    """Construct Solr query parameters.

    Args:
        **kwargs: Arbitrary keyword arguments for Solr parameters

    Returns:
        Solr query parameters
    """
    params = {"wt": "json"}
    for key, value in kwargs.items():
        if isinstance(value, (list, tuple)):
            params[key] = ",".join(map(str, value))
        else:
            params[key] = str(value)
    return params


class SolrClient:
    """Client for interacting with Solr search."""

    def __init__(
        self,
        host: str = SOLR_HOST,
        port: int = SOLR_PORT,
        prefix: str = SOLR_PREFIX,
        protocol: str = SOLR_PROTOCOL,
        timeout: int = SOLR_TIMEOUT,
        password: str = SOLR_PASSWORD,
        client: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize SolrClient.

        Args:
            host: Solr host (default: from env)
            port: Solr port (default: from env)
            prefix: Solr prefix (default: from env)
            protocol: Protocol (default: from env)
            timeout: Request timeout (default: from env)
            password: Solr password (default: from env)
            client: Optional httpx client to use
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.prefix = prefix
        self._solr_url = get_solr_endpoint(
            self.host, self.port, self.prefix, self.protocol
        )
        self._solr_headers = get_solr_headers(password)

        self._client = client or httpx.Client(
            base_url=self._solr_url,
            headers=self._solr_headers,
            timeout=timeout,
            http2=True,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Close the HTTP client connection."""
        if self._client:
            self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a request to Solr.

        Args:
            method: HTTP method
            path: Request path
            params: Query parameters
            data: Request body
            headers: Additional headers

        Returns:
            Solr response

        Raises:
            httpx.HTTPError: If the request fails
        """
        request_headers = self._solr_headers.copy()
        if headers:
            request_headers.update(headers)

        url = f"{self._solr_url}{path.lstrip('/')}"
        response = self._client.request(
            method, url, params=params, json=data, headers=request_headers
        )
        response.raise_for_status()
        return response.json()

    def add_documents(
        self, core: str, documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add documents to Solr index.

        Args:
            core: Solr core name
            documents: Documents to index

        Returns:
            Solr response
        """
        return self._request(
            "POST",
            f"/{core}/update/json/docs",
            data=documents,
            params={"commit": "true"},
        )

    def delete_documents(self, core: str, query: str) -> Dict[str, Any]:
        """Delete documents from Solr index.

        Args:
            core: Solr core name
            query: Query to match documents for deletion

        Returns:
            Solr response
        """
        data = {"delete": {"query": query}}
        return self._request(
            "POST", f"/{core}/update", data=data, params={"commit": "true"}
        )

    def search(self, core: str, query: str, **kwargs) -> Dict[str, Any]:
        """Search documents in Solr index.

        Args:
            core: Solr core name
            query: Search query
            **kwargs: Additional search parameters

        Returns:
            Search results
        """
        params = construct_solr_params(q=query, **kwargs)
        return self._request("GET", f"/{core}/select", params=params)

    def commit(self, core: str) -> Dict[str, Any]:
        """Commit pending changes to Solr index.

        Args:
            core: Solr core name

        Returns:
            Solr response
        """
        return self._request("GET", f"/{core}/update", params={"commit": "true"})

    def optimize(self, core: str) -> Dict[str, Any]:
        """Optimize the Solr index.

        Args:
            core: Solr core name

        Returns:
            Solr response
        """
        return self._request("GET", f"/{core}/update", params={"optimize": "true"})
