"""Inference service

Consumes normalised market data from Kafka, feeds it into a trading model and
publishes trade signals to another Kafka topic.  Replace the simple
threshold‑based logic with your own AI models (LSTM, Transformer, RL, etc.).
Optionally compute explainability (e.g. SHAP) and attach it to the signal for
compliance with MiCA/AI Act.
"""

import json
import os
import sys
from collections import deque
from typing import Dict, List

from dotenv import load_dotenv
from kafka import KafkaConsumer, KafkaProducer
import numpy as np
from tenacity import retry, wait_fixed, stop_after_attempt


load_dotenv()


@retry(wait=wait_fixed(5), stop=stop_after_attempt(5))
def create_consumer(topic: str) -> KafkaConsumer:
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap.split(","),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="inference_service",
    )


@retry(wait=wait_fixed(5), stop=stop_after_attempt(5))
def create_producer() -> KafkaProducer:
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    return KafkaProducer(
        bootstrap_servers=bootstrap.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,
    )


class SimpleMomentumModel:
    """A placeholder trading model that uses price momentum to generate signals.

    It keeps a sliding window of the last `window_size` prices.  If the current
    price is greater than the oldest price by a threshold, it signals a buy; if
    lower by a threshold, a sell; otherwise, hold.
    """

    def __init__(self, window_size: int = 5, threshold: float = 0.001) -> None:
        self.window_size = window_size
        self.threshold = threshold
        self.prices: deque[float] = deque(maxlen=window_size)

    def update(self, price: float) -> int:
        self.prices.append(price)
        if len(self.prices) < self.window_size:
            return 0  # insufficient data
        first = self.prices[0]
        last = self.prices[-1]
        diff = (last - first) / first
        if diff > self.threshold:
            return 1  # buy
        elif diff < -self.threshold:
            return -1  # sell
        return 0  # hold


def main() -> None:
    input_topic = os.getenv("TOPIC_MARKET_DATA", "market_data")
    output_topic = os.getenv("TOPIC_TRADE_SIGNALS", "trade_signals")
    consumer = create_consumer(input_topic)
    producer = create_producer()
    model = SimpleMomentumModel()
    print(f"[INFERENCE] Listening on topic {input_topic}")
    for msg in consumer:
        data: Dict = msg.value
        symbol = data["symbol"]
        price = float(data["last"])
        signal = model.update(price)
        signal_message = {
            "symbol": symbol,
            "timestamp": data["timestamp"],
            "signal": signal,
            "price": price,
        }
        # TODO: compute SHAP/LIME explanations and add to message if using complex models
        producer.send(output_topic, value=signal_message)
        producer.flush()
        print(f"[INFERENCE] {symbol} price={price:.2f} signal={signal}")


if __name__ == "__main__":
    main()