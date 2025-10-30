"""Ingestion service

This module connects to a cryptocurrency exchange (via CCXT or a native SDK)
and publishes normalised market data to Kafka.  It illustrates a simple
producer loop; replace `fetch_market_data` with WebSocket consumption for
higher throughput.
"""

import json
import os
import sys
import time
from typing import Dict, List

from dotenv import load_dotenv
from kafka import KafkaProducer
import ccxt  # type: ignore
from tenacity import retry, wait_fixed, stop_after_attempt


# Load environment variables from .env if present
load_dotenv()


def get_exchange() -> ccxt.Exchange:
    """Initialise a CCXT exchange instance using environment variables."""
    api_key = os.getenv("EXCHANGE_API_KEY")
    secret = os.getenv("EXCHANGE_SECRET")
    # You can customise the exchange here (e.g. binance, kucoin, hyperliquid via SDK)
    exchange = ccxt.binance({
        "apiKey": api_key,
        "secret": secret,
        "enableRateLimit": True,
    })
    return exchange


def normalise_ticker(symbol: str, ticker: Dict) -> Dict:
    """Normalise the raw ticker data into a flat dict suitable for JSON serialisation."""
    return {
        "symbol": symbol,
        "timestamp": ticker["timestamp"],
        "bid": ticker["bid"],
        "ask": ticker["ask"],
        "last": ticker["last"],
        "volume": ticker["baseVolume"],
    }


@retry(wait=wait_fixed(5), stop=stop_after_attempt(5))
def create_producer() -> KafkaProducer:
    """Create a Kafka producer with retries."""
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    return KafkaProducer(
        bootstrap_servers=bootstrap.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
    )


def fetch_market_data(exchange: ccxt.Exchange, symbols: List[str]) -> Dict[str, Dict]:
    """Fetch ticker data for the given symbols from the exchange."""
    data = {}
    for symbol in symbols:
        try:
            ticker = exchange.fetch_ticker(symbol)
            data[symbol] = normalise_ticker(symbol, ticker)
        except Exception as exc:
            print(f"Error fetching ticker for {symbol}: {exc}", file=sys.stderr)
    return data


def main() -> None:
    topic = os.getenv("TOPIC_MARKET_DATA", "market_data")
    symbols_env = os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT")
    symbols = [s.strip().upper() for s in symbols_env.split(",")]

    exchange = get_exchange()
    producer = create_producer()

    print(f"[INGESTION] Starting ingestion for symbols: {symbols}")
    while True:
        market_data = fetch_market_data(exchange, symbols)
        for symbol, payload in market_data.items():
            producer.send(topic, value=payload)
        producer.flush()
        # Sleep for a second – adjust for your latency requirements
        time.sleep(1)


if __name__ == "__main__":
    main()