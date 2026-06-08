#!/usr/bin/env python3
"""CLI entry point for the Binance Futures testnet trading bot."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from bot.client import BinanceTestnetClient
from bot.exceptions import APIError, NetworkError, TradingBotError, ValidationError
from bot.logging_config import setup_logging
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order
from bot.validators import validate_order_params



class C:

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GREY = "\033[90m"

    # Background
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"



BOX_WIDTH = 52


def box_top() -> str:
    return f"{C.CYAN}╔{'═' * BOX_WIDTH}╗{C.RESET}"


def box_bottom() -> str:
    return f"{C.CYAN}╚{'═' * BOX_WIDTH}╝{C.RESET}"


def box_divider() -> str:
    return f"{C.CYAN}╠{'═' * BOX_WIDTH}╣{C.RESET}"


def box_line(content: str, raw_len: int | None = None) -> str:
    visible = raw_len if raw_len is not None else len(content)
    padding = BOX_WIDTH - visible
    return f"{C.CYAN}║{C.RESET}{content}{' ' * max(padding, 0)}{C.CYAN}║{C.RESET}"


def box_empty() -> str:
    return box_line("", 0)



BANNER = r"""
   ╔╗ ╦╔╗╔╔═╗╔╗╔╔═╗╔═╗  ╔╗ ╔═╗╔╦╗
   ╠╩╗║║║║╠═╣║║║║  ║╣   ╠╩╗║ ║ ║
   ╚═╝╩╝╚╝╩ ╩╝╚╝╚═╝╚═╝  ╚═╝╚═╝ ╩
"""


def print_banner() -> None:
    for line in BANNER.strip().splitlines():
        print(f"  {C.CYAN}{C.BOLD}{line}{C.RESET}")
    print(f"  {C.DIM}{C.CYAN}{'─' * 40}{C.RESET}")
    print(
        f"  {C.DIM}Futures Testnet Trading Bot  •  "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}"
    )
    print()


def side_badge(side: str) -> tuple[str, int]:
    if side.upper() == "BUY":
        badge = f"{C.BOLD}{C.GREEN} ▲ BUY  {C.RESET}"
        return badge, 8
    badge = f"{C.BOLD}{C.RED} ▼ SELL {C.RESET}"
    return badge, 8


def type_badge(order_type: str) -> tuple[str, int]:
    colours = {
        "MARKET": C.MAGENTA,
        "LIMIT": C.BLUE,
        "STOP_LIMIT": C.YELLOW,
        "STOP": C.YELLOW,
    }
    colour = colours.get(order_type.upper(), C.WHITE)
    text = f" {order_type} "
    badge = f"{C.BOLD}{colour}{text}{C.RESET}"
    return badge, len(text)


def status_badge(status: str) -> tuple[str, int]:
    status_upper = (status or "UNKNOWN").upper()
    if status_upper in ("FILLED", "NEW"):
        badge = f"{C.BOLD}{C.GREEN}{status_upper}{C.RESET}"
    elif status_upper in ("PARTIALLY_FILLED",):
        badge = f"{C.BOLD}{C.YELLOW}{status_upper}{C.RESET}"
    else:
        badge = f"{C.BOLD}{C.RED}{status_upper}{C.RESET}"
    return badge, len(status_upper)


def print_order_request(args: argparse.Namespace) -> None:
    side_b, side_len = side_badge(args.side)
    type_b, type_len = type_badge(args.type)

    print(box_top())
    title = f"  {C.BOLD}{C.WHITE}📋  ORDER REQUEST{C.RESET}"
    print(box_line(title, 19))
    print(box_divider())


    sym_text = f"  {C.DIM}Symbol{C.RESET}       {C.BOLD}{C.WHITE}{args.symbol}{C.RESET}"
    print(box_line(sym_text, 14 + len(args.symbol)))


    side_text = f"  {C.DIM}Side{C.RESET}         {side_b}"
    print(box_line(side_text, 14 + side_len))


    type_text = f"  {C.DIM}Type{C.RESET}         {type_b}"
    print(box_line(type_text, 14 + type_len))


    qty_str = f"{args.quantity}"
    qty_text = f"  {C.DIM}Quantity{C.RESET}      {C.YELLOW}{qty_str}{C.RESET}"
    print(box_line(qty_text, 14 + len(qty_str)))


    if args.price is not None:
        price_str = f"{args.price}"
        price_text = f"  {C.DIM}Price{C.RESET}        {C.CYAN}{price_str}{C.RESET}"
        print(box_line(price_text, 14 + len(price_str)))


    if args.stop_price is not None:
        stop_str = f"{args.stop_price}"
        stop_text = f"  {C.DIM}Stop Price{C.RESET}   {C.CYAN}{stop_str}{C.RESET}"
        print(box_line(stop_text, 14 + len(stop_str)))

    print(box_bottom())
    print()


def print_order_response(response: dict[str, Any]) -> None:
    side_b, side_len = side_badge(response.get("side", ""))
    type_b, type_len = type_badge(response.get("type", ""))
    stat_b, stat_len = status_badge(response.get("status", ""))

    print(box_top())
    title = f"  {C.BOLD}{C.WHITE}📊  ORDER RESPONSE{C.RESET}"
    print(box_line(title, 20))
    print(box_divider())


    oid = str(response["order_id"])
    print(box_line(f"  {C.DIM}Order ID{C.RESET}     {C.BOLD}{C.WHITE}{oid}{C.RESET}", 14 + len(oid)))


    sym = response["symbol"]
    print(box_line(f"  {C.DIM}Symbol{C.RESET}       {C.BOLD}{C.WHITE}{sym}{C.RESET}", 14 + len(sym)))


    print(box_line(f"  {C.DIM}Side{C.RESET}         {side_b}", 14 + side_len))

    print(box_line(f"  {C.DIM}Type{C.RESET}         {type_b}", 14 + type_len))


    print(box_line(f"  {C.DIM}Status{C.RESET}       {stat_b}", 14 + stat_len))

    print(box_divider())


    eq = response["executed_qty"]
    print(box_line(f"  {C.DIM}Exec. Qty{C.RESET}    {C.YELLOW}{eq}{C.RESET}", 14 + len(eq)))


    ap = response["average_price"]
    print(box_line(f"  {C.DIM}Avg. Price{C.RESET}   {C.CYAN}{ap}{C.RESET}", 14 + len(ap)))

    print(box_bottom())
    print()
    print(f"  {C.BOLD}{C.GREEN}✅ SUCCESS{C.RESET}{C.GREEN} — Order placed successfully.{C.RESET}")
    print()


def print_failure(reason: str) -> None:
    w = BOX_WIDTH
    print(f"\n{C.RED}╔{'═' * w}╗{C.RESET}")
    title = f"  {C.BOLD}{C.RED}❌  ORDER FAILED{C.RESET}"
    print(f"{C.RED}║{C.RESET}{title}{' ' * (w - 18)}{C.RED}║{C.RESET}")
    print(f"{C.RED}╠{'═' * w}╣{C.RESET}")


    max_text = w - 4
    words = reason.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) <= max_text:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines:
        content = f"  {C.WHITE}{line}{C.RESET}"
        print(f"{C.RED}║{C.RESET}{content}{' ' * (w - len(line) - 2)}{C.RED}║{C.RESET}")

    print(f"{C.RED}╚{'═' * w}╝{C.RESET}\n")


def print_processing() -> None:
    print(f"  {C.DIM}{C.CYAN}⏳ Connecting to Binance Futures Testnet...{C.RESET}")



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Binance Futures Testnet Trading Bot – Place orders via CLI.",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair symbol (e.g. BTCUSDT).",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=["MARKET", "LIMIT", "STOP_LIMIT"],
        help="Order type: MARKET, LIMIT, or STOP_LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        type=float,
        required=True,
        help="Order quantity (must be > 0).",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        help="Limit price (required for LIMIT and STOP_LIMIT orders).",
    )
    parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        dest="stop_price",
        help="Stop (trigger) price (required for STOP_LIMIT orders).",
    )
    return parser



def main() -> None:

    load_dotenv()


    setup_logging(console=False)
    logger = logging.getLogger("cli")

    parser = build_parser()
    args = parser.parse_args()


    print_banner()
    print_order_request(args)

    try:

        validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )


        print_processing()
        client = BinanceTestnetClient()


        order_type = args.type.upper()

        if order_type == "MARKET":
            response = place_market_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
            )
        elif order_type == "LIMIT":
            response = place_limit_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price,
            )
        elif order_type == "STOP_LIMIT":
            response = place_stop_limit_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price,
                stop_price=args.stop_price,
            )
        else:
            raise ValidationError(f"Unsupported order type: {order_type}")


        logger.info("Order placed: %s", response)
        print()
        print_order_response(response)

    except ValidationError as exc:
        logger.warning("Validation error: %s", exc)
        print_failure(str(exc))
        sys.exit(1)

    except APIError as exc:
        logger.error("API error: %s", exc)
        print_failure(str(exc))
        sys.exit(1)

    except NetworkError as exc:
        logger.error("Network error: %s", exc)
        print_failure(str(exc))
        sys.exit(1)

    except TradingBotError as exc:
        logger.error("Trading bot error: %s", exc)
        print_failure(str(exc))
        sys.exit(1)

    except KeyboardInterrupt:
        print(f"\n\n  {C.YELLOW}⚠ Operation cancelled by user.{C.RESET}\n")
        sys.exit(130)

    except Exception as exc:
        logger.critical("Unexpected error: %s", exc, exc_info=True)
        print_failure("An unexpected error occurred. Check logs/trading.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
