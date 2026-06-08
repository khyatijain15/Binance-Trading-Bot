"""
Binance Futures Testnet client wrapper.

Encapsulates all interactions with the Binance API through the
``python-binance`` library.  Every public method returns a **normalised
response dict** so that the rest of the application is insulated from the
raw API surface.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import ConnectionError, ReadTimeout, Timeout

from bot.exceptions import APIError, NetworkError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Testnet base URL
# ---------------------------------------------------------------------------
TESTNET_BASE_URL: str = "https://testnet.binancefuture.com"


class BinanceTestnetClient:
    """Thin wrapper around the ``python-binance`` ``Client``.

    Responsibilities
    ----------------
    * Initialise a **Futures Testnet** connection using env-var credentials.
    * Expose typed helpers for MARKET, LIMIT, and STOP_LIMIT orders.
    * Translate Binance/network exceptions into the bot's own hierarchy.
    * Return normalised response dicts.
    """

    def __init__(self) -> None:
        """Create the client from environment variables.

        Raises:
            APIError: If ``BINANCE_API_KEY`` or ``BINANCE_API_SECRET`` are
                not set in the environment.
        """
        api_key: str | None = os.getenv("BINANCE_API_KEY")
        api_secret: str | None = os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            raise APIError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set as "
                "environment variables. See .env.example for reference."
            )

        self._client = Client(api_key, api_secret, testnet=True)

        logger.info("Binance Futures Testnet client initialised.")

    # ------------------------------------------------------------------
    # Public order methods
    # ------------------------------------------------------------------

    def place_market_order(
        self, symbol: str, side: str, quantity: float
    ) -> dict[str, Any]:
        """Place a MARKET order on the Futures Testnet.

        Args:
            symbol: Trading pair (e.g. ``BTCUSDT``).
            side: ``BUY`` or ``SELL``.
            quantity: Trade quantity.

        Returns:
            Normalised order response dict.
        """
        logger.info(
            "Placing MARKET order: symbol=%s side=%s qty=%s",
            symbol,
            side,
            quantity,
        )
        return self._execute_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
    ) -> dict[str, Any]:
        """Place a LIMIT order (GTC) on the Futures Testnet.

        Args:
            symbol: Trading pair.
            side: ``BUY`` or ``SELL``.
            quantity: Trade quantity.
            price: Limit price.

        Returns:
            Normalised order response dict.
        """
        logger.info(
            "Placing LIMIT order: symbol=%s side=%s qty=%s price=%s",
            symbol,
            side,
            quantity,
            price,
        )
        return self._execute_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce="GTC",
        )

    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
    ) -> dict[str, Any]:
        """Place a STOP-LIMIT order on the Futures Testnet.

        The order becomes an active LIMIT order once the market price reaches
        *stop_price*.

        Args:
            symbol: Trading pair.
            side: ``BUY`` or ``SELL``.
            quantity: Trade quantity.
            price: Limit price (after stop triggers).
            stop_price: The trigger (stop) price.

        Returns:
            Normalised order response dict.
        """
        logger.info(
            "Placing STOP_LIMIT order: symbol=%s side=%s qty=%s "
            "price=%s stop=%s",
            symbol,
            side,
            quantity,
            price,
            stop_price,
        )
        return self._execute_order(
            symbol=symbol,
            side=side,
            type="STOP",
            quantity=quantity,
            price=price,
            stopPrice=stop_price,
            timeInForce="GTC",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_order(self, **kwargs: Any) -> dict[str, Any]:
        """Send an order to the Binance Futures API and normalise the result.

        All keyword arguments are forwarded to
        ``Client.futures_create_order``.

        Returns:
            Normalised response dict with keys: ``order_id``, ``symbol``,
            ``side``, ``type``, ``status``, ``executed_qty``,
            ``average_price``, ``raw``.

        Raises:
            APIError: On Binance application-level errors.
            NetworkError: On connectivity / timeout issues.
        """
        try:
            raw: dict[str, Any] = self._client.futures_create_order(**kwargs)
            logger.debug("Raw API response: %s", raw)
            return self._normalise(raw)

        except BinanceAPIException as exc:
            logger.error("Binance API error: %s (code %s)", exc.message, exc.code)
            raise APIError(exc.message, error_code=exc.code) from exc

        except BinanceRequestException as exc:
            logger.error("Binance request error: %s", exc)
            raise NetworkError(f"Request to Binance failed: {exc}") from exc

        except (ConnectionError, Timeout, ReadTimeout) as exc:
            logger.error("Network error: %s", exc)
            raise NetworkError(
                f"Network error while contacting Binance: {exc}"
            ) from exc

    @staticmethod
    def _normalise(raw: dict[str, Any]) -> dict[str, Any]:
        """Convert the raw Binance response into a clean, flat dict.

        Args:
            raw: The JSON dict returned by the Binance API.

        Returns:
            A normalised dict suitable for display / logging.
        """
        # Compute average price from fills if available
        fills = raw.get("fills", [])
        if fills:
            total_qty = sum(float(f["qty"]) for f in fills)
            total_cost = sum(float(f["price"]) * float(f["qty"]) for f in fills)
            avg_price = total_cost / total_qty if total_qty else 0.0
        else:
            avg_price = float(raw.get("avgPrice", raw.get("price", 0)))

        # Algo orders (STOP, STOP_MARKET, etc.) return different field names
        order_id = raw.get("orderId") or raw.get("algoId")
        order_type = raw.get("type") or raw.get("orderType")
        status = raw.get("status") or raw.get("algoStatus")
        executed_qty = raw.get("executedQty", raw.get("quantity", "0"))

        return {
            "order_id": order_id,
            "symbol": raw.get("symbol"),
            "side": raw.get("side"),
            "type": order_type,
            "status": status,
            "executed_qty": executed_qty,
            "average_price": f"{avg_price:.8f}",
            "raw": raw,
        }
