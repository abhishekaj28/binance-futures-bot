"""
client.py
---------
Low-level Binance Futures Testnet REST client.

Responsibilities:
  - Build signed requests (HMAC-SHA256)
  - Handle HTTP communication via `requests`
  - Log every outgoing request and incoming response
  - Raise BinanceAPIError on non-2xx responses
"""

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx response or an error payload."""

    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"[HTTP {status_code}] Binance error {code}: {message}")


class BinanceFuturesClient:
    """
    Thin wrapper around the Binance USDT-M Futures REST API.

    Parameters
    ----------
    api_key : str
        Your Binance Futures Testnet API key.
    api_secret : str
        Your Binance Futures Testnet API secret.
    timeout : int
        HTTP request timeout in seconds (default 10).
    """

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceFuturesClient initialised (testnet).")

    # ── Internal helpers ────────────────────────────────────────────────────

    def _timestamp(self) -> int:
        try:
            server_time = self .session.get(
                f"{BASE_URL}/fapi/v1/time", timeout=5
            ).json()["serverTime"]
            return int(server_time)
        except Exception:
            return int(
                time.time() * 1000)
        return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Dict[str, Any]:
        """
        Core HTTP dispatcher.

        Adds timestamp + signature for signed endpoints.
        Logs request parameters and response payload.
        Raises BinanceAPIError on errors.
        """
        params = params or {}

        if signed:
            params["timestamp"] = self._timestamp()
            params["signature"] = self._sign(params)

        url = f"{BASE_URL}{endpoint}"

        logger.debug(
            "REQUEST  method=%s url=%s params=%s",
            method.upper(),
            url,
            {k: v for k, v in params.items() if k != "signature"},  # hide sig in logs
        )

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params, timeout=self.timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except requests.exceptions.ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise ConnectionError(f"Could not reach Binance testnet: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out after %ss: %s", self.timeout, exc)
            raise TimeoutError(f"Request timed out ({self.timeout}s).") from exc

        logger.debug(
            "RESPONSE status=%s body=%s", response.status_code, response.text[:500]
        )

        payload = response.json()

        # Binance returns errors as {"code": <neg int>, "msg": "..."}
        if isinstance(payload, dict) and "code" in payload and payload["code"] != 200:
            if payload["code"] < 0:  # negative code = error
                raise BinanceAPIError(
                    status_code=response.status_code,
                    code=payload["code"],
                    message=payload.get("msg", "Unknown error"),
                )

        if not response.ok:
            raise BinanceAPIError(
                status_code=response.status_code,
                code=payload.get("code", -1),
                message=payload.get("msg", response.text),
            )

        return payload

    # ── Public API methods ──────────────────────────────────────────────────

    def get_server_time(self) -> Dict[str, Any]:
        """Ping the server and return its time. Useful for connectivity checks."""
        return self._request("GET", "/fapi/v1/time")

    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Return exchange trading rules and symbol information."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/fapi/v1/exchangeInfo", params=params)

    def get_account(self) -> Dict[str, Any]:
        """Return account balances and position info (signed)."""
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(self, **kwargs) -> Dict[str, Any]:
        """
        Place a new order on Binance Futures.

        Accepted kwargs mirror the Binance API parameters:
          symbol, side, type, quantity, price, timeInForce,
          stopPrice, reduceOnly, newOrderRespType, etc.

        Returns the full order response dict.
        """
        params = {k: v for k, v in kwargs.items() if v is not None}
        logger.info("Placing order: %s", params)
        return self._request("POST", "/fapi/v1/order", params=params, signed=True)

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an open order by orderId."""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/fapi/v1/order", params=params, signed=True)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Query the status of a single order."""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("GET", "/fapi/v1/order", params=params, signed=True)