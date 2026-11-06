#!/usr/bin/env bash
# Bash Script to Launch Bifrost Gateway with Configured Providers & Governance

set -e

APP_DIR="${1:-./bifrost}"

echo -e "\033[36m==========================================================\033[0m"
echo -e "\033[32m   Starting Maxim AI Bifrost LLM Gateway                  \033[0m"
echo -e "\033[36m==========================================================\033[0m"

# Load .env file if present
if [ -f ".env" ]; then
    echo -e "\033[33m[Info] Loading environment variables from .env...\033[0m"
    set -a
    source .env
    set +a
fi

# Set defaults if unset
export BIFROST_ENCRYPTION_KEY="${BIFROST_ENCRYPTION_KEY:-0123456789abcdef0123456789abcdef}"
export BIFROST_VIRTUAL_KEY="${BIFROST_VIRTUAL_KEY:-sk-bf-nano-agent-secret-key}"

echo -e "\033[36m[Config] App Directory : $APP_DIR\033[0m"
echo -e "\033[36m[Config] Virtual Key   : $BIFROST_VIRTUAL_KEY\033[0m"
echo -e "\033[32m[Info] Executing npx -y @maximhq/bifrost -app-dir $APP_DIR...\033[0m"
echo -e "\033[90m[Note] Web UI will be accessible at http://localhost:8080\033[0m"

npx -y @maximhq/bifrost -app-dir "$APP_DIR"

