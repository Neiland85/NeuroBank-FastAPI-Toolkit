#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] Installing system tools via apt..."
apt-get update -qq
apt-get install -y -qq build-essential wget
rm -rf /var/lib/apt/lists/*

echo "[devcontainer] Installing Python dependencies for each service..."
for svc in ingestion_service inference_service control_service; do
  if [ -f "/workspace/$svc/requirements.txt" ]; then
    pip install --no-cache-dir -r "/workspace/$svc/requirements.txt"
  fi
done

echo "[devcontainer] Installing additional developer tools..."
# Install GitHub CLI for interacting with GitHub inside the container
type gh >/dev/null 2>&1 || {
  wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
  apt-get update -qq && apt-get install -y -qq gh && rm -rf /var/lib/apt/lists/*
}

echo "[devcontainer] Setup complete."