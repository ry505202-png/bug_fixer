# Bifrost Local Gateway Setup Guide

This guide explains how to run **Maxim AI's Bifrost Gateway** locally to route requests for Nano-Agent with two cloud providers, Ollama fallback, and a virtual key budget cap.

---

## 1. Architecture & Configuration Files

Bifrost is configured in file-only mode via [`bifrost/config.json`](file:///c:/Users/hp/OneDrive/Desktop/c%20language/solo/bifrost/config.json) based on the authoritative `https://www.getbifrost.ai/schema`.

### Config Summary:
- **Cloud Providers**:
  - `anthropic` mapped to `env.ANTHROPIC_API_KEY`
  - `openai` mapped to `env.OPENAI_API_KEY`
- **Local Fallback Provider**:
  - `ollama` mapped to `http://localhost:11434` (requires no API key)
- **Governance & Virtual Key**:
  - ID: `vk-nano-agent`
  - Value: `env.BIFROST_VIRTUAL_KEY`
  - Budget Guardrail: Hard limit of **\$5.00** reset monthly (`"reset_duration": "1M"`)
  - Permitted Providers: `anthropic`, `openai`, `ollama`
- **Fallback Chain (`routing_rules`)**:
  - Primary target: `anthropic/claude-3-5-sonnet`
  - Automatic fallback 1: `openai/gpt-4o-mini`
  - Automatic fallback 2: `ollama/qwen2.5-coder:7b`

---

## 2. Environment Setup

Configure your API keys in `.env` (or copy from `.env.example`):

```bash
# Cloud Providers
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
OPENAI_API_KEY=sk-proj-your-real-key-here

# Local Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Bifrost Security
BIFROST_ENCRYPTION_KEY=0123456789abcdef0123456789abcdef
BIFROST_VIRTUAL_KEY=sk-bf-nano-agent-secret-key
BIFROST_BASE_URL=http://localhost:8080/v1
```

---

## 3. Launching Bifrost

### Option A: Using the Provided PowerShell Script (Windows)
```powershell
./run_bifrost.ps1
```

### Option B: Using the Bash Script (Linux/macOS)
```bash
chmod +x run_bifrost.sh
./run_bifrost.sh
```

### Option C: Direct npx Command
```bash
npx -y @maximhq/bifrost -app-dir ./bifrost
```

### Option D: Docker
```bash
docker run -p 8080:8080 \
  -v $(pwd)/bifrost:/app/data \
  --env-file .env \
  maximhq/bifrost
```

Once running:
- **API Gateway**: `http://localhost:8080/v1`
- **Bifrost Web Dashboard**: `http://localhost:8080`

---

## 4. Testing the Gateway Connection

To verify that the gateway is accepting requests and reporting token usage:

```bash
python test_bifrost.py
```

To test a specific model or local Ollama directly:
```bash
# Test local Ollama through Bifrost
python test_bifrost.py ollama/qwen2.5-coder:7b

# Test OpenAI secondary through Bifrost
python test_bifrost.py gpt-4o-mini
```

---

## 5. Running the Nano-Agent via Bifrost

Once Bifrost is running, Nano-Agent automatically routes all dev tasks through it:

```bash
# Cloud task with automatic outage fallback through Bifrost
python -m agent.cli "Fix calculation in math_utils.py" --budget 0.50

# Confidential mode (Ollama only, zero cloud calls)
python -m agent.cli "Refactor proprietary algorithm" --privacy
```

