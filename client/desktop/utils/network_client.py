# -*- coding: utf-8 -*-
"""
HTTP network client.

Thin wrapper around ``requests.Session`` with:
- Configurable base URL, timeout, and retry count.
- Automatic Bearer-token injection.
- Structured error handling that always raises ``NetworkError``.

Author : AHDUNYI
Version: 9.0.0
"""

from typing import Any, Dict, Optional
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class NetworkError(Exception):
    """Raised by NetworkClient for any non-2xx response or connection failure.

    Attributes:
        status_code: HTTP status code, or 0 for connection-level errors.
        detail: Human-readable error message from the response body.
    """

    def __init__(self, message: str, status_code: int = 0, detail: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class NetworkClient:
    """Reusable HTTP client backed by a persistent requests.Session.

    Args:
        base_url: Server origin, e.g. ``http://127.0.0.1:8000``.
        timeout: Request timeout in seconds.  Default 10.
        retries: Number of automatic retries on connection errors.  Default 2.
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 10,
        retries: int = 2,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = self._build_session(retries)
        self._token: Optional[str] = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_token(self, token: str) -> None:
        """Set the Bearer token used for authenticated requests."""
        self._token = token
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        logger.debug("Bearer token updated.")

    def clear_token(self) -> None:
        """Remove the Bearer token (e.g. on logout)."""
        self._token = None
        self._session.headers.pop("Authorization", None)

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a GET request.

        Args:
            path: URL path relative to base_url.
            params: Optional query-string parameters.

        Returns:
            Parsed JSON body.

        Raises:
            NetworkError: On any non-2xx response or connection failure.
        """
        return self._request("GET", path, params=params)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """Send a POST request with a JSON body.

        Args:
            path: URL path relative to base_url.
            json: Optional request body (will be JSON-encoded).

        Returns:
            Parsed JSON body.

        Raises:
            NetworkError: On any non-2xx response or connection failure.
        """
        return self._request("POST", path, json=json)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            resp = self._session.request(
                method, url, timeout=self._timeout, **kwargs
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError as exc:
            raise NetworkError(
                f"Cannot connect to {self._base_url}", status_code=0
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise NetworkError(
                f"Request timed out ({self._timeout}s)", status_code=0
            ) from exc
        except requests.exceptions.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else 0
            try:
                detail = exc.response.json().get("detail", "")  # type: ignore[union-attr]
            except Exception:  # pylint: disable=broad-except
                detail = ""
            raise NetworkError(
                f"HTTP {code}: {exc}", status_code=code, detail=detail
            ) from exc
        except Exception as exc:  # pylint: disable=broad-except
            raise NetworkError(f"Unexpected error: {exc}") from exc

    @staticmethod
    def _build_session(retries: int) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        retry_cfg = Retry(
            total=retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_cfg)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_network_client(
    base_url: str,
    timeout: int = 10,
    token: Optional[str] = None,
) -> NetworkClient:
    """Create and optionally authenticate a NetworkClient.

    Args:
        base_url: Server origin URL.
        timeout: Request timeout in seconds.
        token: Optional Bearer token to set immediately.

    Returns:
        Configured NetworkClient instance.
    """
    client = NetworkClient(base_url, timeout=timeout)
    if token:
        client.set_token(token)
    return client
