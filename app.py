#!/usr/bin/env python3
"""Flask web UI for the Binance Futures testnet trading bot."""

from __future__ import annotations

import logging
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from bot.client import BinanceTestnetClient
from bot.exceptions import APIError, NetworkError, TradingBotError, ValidationError
from bot.logging_config import setup_logging
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order
from bot.validators import validate_order_params


load_dotenv()
setup_logging(console=False)
logger = logging.getLogger("app")

app = Flask(__name__)



@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/order", methods=["POST"])
def place_order() -> tuple[Any, int]:
    data = request.get_json(silent=True) or {}

    symbol = data.get("symbol", "")
    side = data.get("side", "")
    order_type = data.get("type", "")
    quantity = data.get("quantity", 0)
    price = data.get("price")
    stop_price = data.get("stop_price")


    if not price:
        price = None
    if not stop_price:
        stop_price = None

    try:
        validate_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=float(quantity),
            price=float(price) if price else None,
            stop_price=float(stop_price) if stop_price else None,
        )


        client = BinanceTestnetClient()

        if order_type.upper() == "MARKET":
            resp = place_market_order(client, symbol, side, float(quantity))
        elif order_type.upper() == "LIMIT":
            resp = place_limit_order(client, symbol, side, float(quantity), float(price))
        elif order_type.upper() == "STOP_LIMIT":
            resp = place_stop_limit_order(
                client, symbol, side, float(quantity), float(price), float(stop_price)
            )
        else:
            raise ValidationError(f"Unsupported order type: {order_type}")

        logger.info("Order placed via UI: %s", resp)
        return jsonify({"success": True, "data": {k: v for k, v in resp.items() if k != "raw"}}), 200

    except ValidationError as exc:
        logger.warning("UI validation error: %s", exc)
        return jsonify({"success": False, "error": str(exc), "type": "validation"}), 400

    except APIError as exc:
        logger.error("UI API error: %s", exc)
        return jsonify({"success": False, "error": str(exc), "type": "api"}), 502

    except NetworkError as exc:
        logger.error("UI network error: %s", exc)
        return jsonify({"success": False, "error": str(exc), "type": "network"}), 503

    except TradingBotError as exc:
        logger.error("UI bot error: %s", exc)
        return jsonify({"success": False, "error": str(exc), "type": "bot"}), 500

    except Exception as exc:
        logger.critical("UI unexpected error: %s", exc, exc_info=True)
        return jsonify({"success": False, "error": "Unexpected server error.", "type": "unknown"}), 500


@app.route("/api/logs", methods=["GET"])
def get_logs() -> tuple[Any, int]:
    n = request.args.get("n", 50, type=int)
    try:
        with open("logs/trading.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
        return jsonify({"lines": lines[-n:]}), 200
    except FileNotFoundError:
        return jsonify({"lines": []}), 200



if __name__ == "__main__":
    print("\n  🚀 Trading Bot UI running at: http://localhost:5050\n")
    app.run(debug=True, host="0.0.0.0", port=5050)
