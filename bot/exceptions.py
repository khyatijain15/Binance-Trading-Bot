"""
Custom exception hierarchy for the trading bot.

All domain-specific exceptions inherit from ``TradingBotError`` so that
callers can catch the entire family with a single ``except`` clause when
needed.
"""


class TradingBotError(Exception):
    """Base exception for every error raised by the trading bot."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class ValidationError(TradingBotError):
    """Raised when user-supplied input fails validation.

    Examples:
        - Empty symbol
        - Negative quantity
        - Missing price for a LIMIT order
    """


class APIError(TradingBotError):
    """Raised when the Binance API returns an application-level error.

    Attributes:
        error_code: The Binance error code (e.g. -1121 for invalid symbol).
    """

    def __init__(self, message: str, error_code: int | None = None) -> None:
        self.error_code = error_code
        super().__init__(message)

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"[Binance {self.error_code}] {self.message}"
        return self.message


class NetworkError(TradingBotError):
    """Raised on connectivity / timeout failures when contacting Binance."""
