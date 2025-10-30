"""Control service

Listens for trading signals from the inference service, applies basic
risk‑management rules and executes orders on the configured exchange.
This implementation uses CCXT for exchange connectivity; replace with a
native SDK (e.g. hyperliquid) for production trading.
"""

import json
import os
import sys
from typing import Dict

from dotenv import load_dotenv
from kafka import KafkaConsumer
import ccxt  # type: ignore
from tenacity import retry, wait_fixed, stop_after_attempt

load_dotenv()


def get_exchange() -> ccxt.Exchange:
    api_key = os.getenv("EXCHANGE_API_KEY")
    secret = os.getenv("EXCHANGE_SECRET")
    exchange = ccxt.binance({
        "apiKey": api_key,
        "secret": secret,
        "enableRateLimit": True,
    })
    return exchange


@retry(wait=wait_fixed(5), stop=stop_after_attempt(5))
def create_consumer(topic: str) -> KafkaConsumer:
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap.split(","),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="control_service",
    )


def calculate_position_size(balance: float, risk_fraction: float) -> float:
    """Calculate position size based on available balance and risk fraction."""
    return balance * risk_fraction


def place_order(exchange: ccxt.Exchange, symbol: str, signal: int, amount: float) -> None:
    """Place a market order on the exchange.  For a real system you should
    implement advanced order types, slippage checks and error handling."""
    side = "buy" if signal == 1 else "sell"
    try:
        # Use market order for simplicity
        order = exchange.create_market_order(symbol, side, amount)
        print(f"[CONTROL] Executed {side} {amount:.6f} {symbol} -> {order}")
    except Exception as exc:
        print(f"[CONTROL] Error placing order: {exc}", file=sys.stderr)


def main() -> None:
    topic = os.getenv("TOPIC_TRADE_SIGNALS", "trade_signals")
    consumer = create_consumer(topic)
    exchange = get_exchange()
    symbol_quote = os.getenv("DEFAULT_SYMBOL", "BTC/USDT")
    risk_fraction = float(os.getenv("RISK_FRACTION", "0.01"))  # risk 1% of balance per trade
    print(f"[CONTROL] Listening on topic {topic}")
    for msg in consumer:
        data: Dict = msg.value
        signal = int(data.get("signal", 0))
        if signal == 0:
            continue  # no action
        symbol = data.get("symbol", symbol_quote)
        # Query balance
        try:
            balance_info = exchange.fetch_balance()
            base = symbol.split("/")[0]
            free_balance = balance_info[base]["free"]
        except Exception as exc:
            print(f"[CONTROL] Error fetching balance: {exc}", file=sys.stderr)
            continue
        # Determine position size
        amount = calculate_position_size(free_balance, risk_fraction)
        if amount <= 0:
            print("[CONTROL] No balance available to trade.")
            continue
        # Place order
        place_order(exchange, symbol, signal, amount)


if __name__ == "__main__":
    main()