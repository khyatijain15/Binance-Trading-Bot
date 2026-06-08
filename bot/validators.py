"""
Input validators for CLI arguments and order parameters.

Every public function raises :class:`bot.exceptions.ValidationError` on
invalid input so that the caller never has to guess whether the data is
well-formed.
"""

import logging
from typing import Optional

from bot.exceptions import ValidationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Allowed values
# ---------------------------------------------------------------------------
VALID_SIDES: set[str] = {"BUY", "SELL"}
VALID_ORDER_TYPES: set[str] = {"MARKET", "LIMIT", "STOP_LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Return the uppercased symbol or raise on empty input.

    Args:
        symbol: Trading pair symbol (e.g. ``BTCUSDT``).

    Returns:
        The sanitized, uppercased symbol string.

    Raises:
        ValidationError: If *symbol* is empty or whitespace-only.
    """
    if not symbol or not symbol.strip():
        msg = "Symbol must not be empty."
        logger.warning("Validation failed: %s", msg)
        raise ValidationError(msg)
    return symbol.strip().upper()


def validate_side(side: str) -> str:
    """Return the uppercased side or raise if not BUY/SELL.

    Args:
        side: Order side – ``BUY`` or ``SELL``.

    Returns:
        The uppercased side string.

    Raises:
        ValidationError: If *side* is not one of the allowed values.
    """
    side_upper = side.strip().upper()
    if side_upper not in VALID_SIDES:
        msg = f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        logger.warning("Validation failed: %s", msg)
        raise ValidationError(msg)
    return side_upper


def validate_order_type(order_type: str) -> str:
    """Return the uppercased order type or raise on invalid input.

    Args:
        order_type: Order type – ``MARKET``, ``LIMIT``, or ``STOP_LIMIT``.

    Returns:
        The uppercased order type string.

    Raises:
        ValidationError: If *order_type* is not one of the allowed values.
    """
    order_type_upper = order_type.strip().upper()
    if order_type_upper not in VALID_ORDER_TYPES:
        msg = (
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
        logger.warning("Validation failed: %s", msg)
        raise ValidationError(msg)
    return order_type_upper


def validate_quantity(quantity: float) -> float:
    """Return the quantity if positive; raise otherwise.

    Args:
        quantity: Trade quantity (must be > 0).

    Returns:
        The validated quantity.

    Raises:
        ValidationError: If *quantity* is not a positive number.
    """
    if quantity <= 0:
        msg = f"Quantity must be greater than 0. Got: {quantity}"
        logger.warning("Validation failed: %s", msg)
        raise ValidationError(msg)
    return quantity


def validate_price(price: Optional[float], order_type: str) -> Optional[float]:
    """Validate the price for order types that require it.

    LIMIT and STOP_LIMIT orders **must** have a positive price.
    MARKET orders ignore the price argument.

    Args:
        price: Limit price (may be ``None`` for MARKET orders).
        order_type: Already-validated order type string.

    Returns:
        The validated price, or ``None`` for MARKET orders.

    Raises:
        ValidationError: If a price is required but missing or non-positive.
    """
    if order_type in ("LIMIT", "STOP_LIMIT"):
        if price is None or price <= 0:
            msg = f"{order_type} orders require a price greater than 0."
            logger.warning("Validation failed: %s", msg)
            raise ValidationError(msg)
    return price


def validate_stop_price(
    stop_price: Optional[float], order_type: str
) -> Optional[float]:
    """Validate stop_price for STOP_LIMIT orders.

    Args:
        stop_price: The trigger (stop) price.
        order_type: Already-validated order type string.

    Returns:
        The validated stop price, or ``None`` if not required.

    Raises:
        ValidationError: If *order_type* is ``STOP_LIMIT`` and stop_price is
            missing or non-positive.
    """
    if order_type == "STOP_LIMIT":
        if stop_price is None or stop_price <= 0:
            msg = "STOP_LIMIT orders require a --stop-price greater than 0."
            logger.warning("Validation failed: %s", msg)
            raise ValidationError(msg)
    return stop_price


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """Run all validators and return a cleaned parameter dict.

    This is the single entry-point that the order layer should call.

    Returns:
        A dictionary with keys: ``symbol``, ``side``, ``order_type``,
        ``quantity``, ``price``, ``stop_price``.

    Raises:
        ValidationError: On the first validation failure encountered.
    """
    cleaned_symbol = validate_symbol(symbol)
    cleaned_side = validate_side(side)
    cleaned_type = validate_order_type(order_type)
    cleaned_qty = validate_quantity(quantity)
    cleaned_price = validate_price(price, cleaned_type)
    cleaned_stop = validate_stop_price(stop_price, cleaned_type)

    logger.debug(
        "Validation passed – symbol=%s side=%s type=%s qty=%s price=%s stop=%s",
        cleaned_symbol,
        cleaned_side,
        cleaned_type,
        cleaned_qty,
        cleaned_price,
        cleaned_stop,
    )

    return {
        "symbol": cleaned_symbol,
        "side": cleaned_side,
        "order_type": cleaned_type,
        "quantity": cleaned_qty,
        "price": cleaned_price,
        "stop_price": cleaned_stop,
    }
