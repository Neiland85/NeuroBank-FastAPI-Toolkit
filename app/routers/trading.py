import random
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
from fastapi import APIRouter
from pycoingecko import CoinGeckoAPI

router = APIRouter()
cg = CoinGeckoAPI()


# === AGENTE RL SIMPLE (PPO-like) ===
class SimplePPOAgent(nn.Module):
    def __init__(self, input_size=5, hidden_size=64):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.policy_head = nn.Linear(hidden_size, 3)  # LONG, SHORT, HOLD
        self.value_head = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        policy = torch.softmax(self.policy_head(x), dim=-1)
        value = self.value_head(x)
        return policy, value


agent = SimplePPOAgent()
agent.eval()


# === DATOS REALES BTC (Coingecko) + ORDERBOOK MOCK ===
def get_btc_data():
    try:
        data = cg.get_price(ids="bitcoin", vs_currencies="usd", include_24hr_vol="true")
        price = data["bitcoin"]["usd"]
        volume_24h = data["bitcoin"]["usd_24h_vol"]
    except Exception as e:
        print(f"Coingecko fallback: {e}")
        price = 67000.0 + np.random.normal(0, 1000)
        volume_24h = random.uniform(1000, 5000) * 1000

    # Orderbook simulado (5 niveles)
    bids = [
        (price * (1 - 0.0001 * (j + 1)), random.uniform(0.1, 2.0)) for j in range(5)
    ]
    asks = [
        (price * (1 + 0.0001 * (j + 1)), random.uniform(0.1, 2.0)) for j in range(5)
    ]
    imbalance = sum(qty for _, qty in bids) - sum(qty for _, qty in asks)

    return {
        "timestamp": datetime.now().isoformat(),
        "price": round(price, 2),
        "volume_24h": round(volume_24h, 2),
        "imbalance": round(imbalance, 4),
        "bids": bids,
        "asks": asks,
    }


# === ENDPOINT: SEÑAL DE TRADING ===
@router.get("/imbalance")
async def get_imbalance_and_signal():
    tick = get_btc_data()

    # Estado para RL: [imbalance, price_change, volume_norm, spread, momentum]
    state = torch.tensor(
        [
            [
                tick["imbalance"] / 10.0,
                0.001,  # mock delta
                min(tick["volume_24h"] / 1e9, 1.0),
                (tick["asks"][0][0] - tick["bids"][0][0]) / tick["price"],
                random.uniform(-0.01, 0.01),
            ]
        ],
        dtype=torch.float32,
    )

    with torch.no_grad():
        policy, value = agent(state)
        action_idx = policy.argmax().item()
        action_map = {0: "LONG", 1: "SHORT", 2: "HOLD"}
        signal = action_map[action_idx]
        confidence = policy[0][action_idx].item()

    return {
        "timestamp": tick["timestamp"],
        "price": tick["price"],
        "volume_24h": tick["volume_24h"],
        "imbalance": tick["imbalance"],
        "signal": signal,
        "confidence": round(confidence, 4),
        "value_estimate": round(value.item(), 4),
        "orderbook_snapshot": {"bids": tick["bids"][:3], "asks": tick["asks"][:3]},
    }


# === ENDPOINT: ESTADO DEL AGENTE ===
@router.get("/agent/status")
async def agent_status():
    return {
        "agent": "SimplePPOAgent",
        "status": "loaded",
        "input_size": 5,
        "actions": ["LONG", "SHORT", "HOLD"],
        "torch_version": torch.__version__,
    }
