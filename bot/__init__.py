"""
Binance Futures Testnet Trading Bot - Core Package.

This package provides a modular, production-quality interface for placing
orders on the Binance USDT-M Futures Testnet.

Modules:
    client          – Binance API client wrapper
    orders          – High-level order placement logic
    validators      – Input validation utilities
    exceptions      – Custom exception hierarchy
    logging_config  – Centralized logging setup
"""

from bot.exceptions import ValidationError, APIError, NetworkError

__all__ = [
    "ValidationError",
    "APIError",
    "NetworkError",
]
