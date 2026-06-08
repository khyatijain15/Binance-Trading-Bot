"""
High-level order placement logic.

This module sits between the CLI and the low-level
:class:`bot.client.BinanceTestnetClient`.  It validates inputs, delegates
to the correct client method, and returns a normalised response.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from bot.client import BinanceTestnetClient
from bot.validators import validate_order_params

logger = logging.getLogger(__name__)


def place_market_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: float,
) -> dict[str, Any]:
    """Validate and place a MARKET order.

    Args:
        client: An initialised Binance testnet client.
        symbol: Trading pair (e.g. ``BTCUSDT``).
        side: ``BUY`` or ``SELL``.
        quantity: Trade quantity (> 0).

    Returns:
        Normalised order response dict.

    Raises:
        ValidationError: If any parameter is invalid.
        APIError: On Binance application-level errors.
        NetworkError: On connectivity issues.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        quantity=quantity,
    )
    logger.info(
        "Dispatching MARKET order – %s %s %s",
        params["side"],
        params["quantity"],
        params["symbol"],
    )
    return client.place_market_order(
        symbol=params["symbol"],
        side=params["side"],
        quantity=params["quantity"],
    )


def place_limit_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
) -> dict[str, Any]:
    """Validate and place a LIMIT order.

    Args:
        client: An initialised Binance testnet client.
        symbol: Trading pair.
        side: ``BUY`` or ``SELL``.
        quantity: Trade quantity (> 0).
        price: Limit price (> 0).

    Returns:
        Normalised order response dict.

    Raises:
        ValidationError: If any parameter is invalid.
        APIError: On Binance application-level errors.
        NetworkError: On connectivity issues.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price,
    )
    logger.info(
        "Dispatching LIMIT order – %s %s %s @ %s",
        params["side"],
        params["quantity"],
        params["symbol"],
        params["price"],
    )
    return client.place_limit_order(
        symbol=params["symbol"],
        side=params["side"],
        quantity=params["quantity"],
        price=params["price"],
    )


def place_stop_limit_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict[str, Any]:
    """Validate and place a STOP_LIMIT order.

    The order becomes an active LIMIT order when the market price hits
    *stop_price*.

    Args:
        client: An initialised Binance testnet client.
        symbol: Trading pair.
        side: ``BUY`` or ``SELL``.
        quantity: Trade quantity (> 0).
        price: Limit price (> 0).
        stop_price: The trigger price (> 0).

    Returns:
        Normalised order response dict.

    Raises:
        ValidationError: If any parameter is invalid.
        APIError: On Binance application-level errors.
        NetworkError: On connectivity issues.
    """
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="STOP_LIMIT",
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )
    logger.info(
        "Dispatching STOP_LIMIT order – %s %s %s @ %s (stop %s)",
        params["side"],
        params["quantity"],
        params["symbol"],
        params["price"],
        params["stop_price"],
    )
    return client.place_stop_limit_order(
        symbol=params["symbol"],
        side=params["side"],
        quantity=params["quantity"],
        price=params["price"],
        stop_price=params["stop_price"],
    )
