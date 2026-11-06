# Nano-Agent Screen Recording Demos

This guide provides instructions and narrative scripts for recording the three core hackathon capabilities of **Nano-Agent** using **Maxim AI's Bifrost Gateway**:

1. **Multi-Provider Outage Resilience**: Simulating primary provider failure mid-task with automatic, zero-downtime fallback.
2. **Budget Guardrail & Spending Enforcement**: Setting a strict spending cap and proving proactive agent stoppage.
3. **Air-Gapped Zero-Cloud Privacy Mode**: Demonstrating local Ollama execution with external network blocked and zero data leakage.

---

## 🎬 Quick Start Commands

You can run each demo individually or launch the interactive runner:

```bash
# Interactive Menu (choose 1, 2, 3, or all)
python run_demos.py

# Run Demo 1: Outage Failover
python demo_outage.py

# Run Demo 2: Budget Limit Enforcement
python demo_budget.py

# Run Demo 3: Air-Gapped Privacy Mode
python demo_privacy.py
```

> **Screen Recording Tip**: The scripts feature a built-in `1.0s` delay between steps so the audience can read each phase. If you want to run faster without delays for quick testing, pass `--fast` (e.g. `python demo_outage.py --fast`).

---

## 1. Demo 1: Resilient Outage Failover (`demo_outage.py`)

### What it Demonstrates
- **Initial Setup**: Primary provider is set to `claude-3-5-sonnet` (Anthropic), secondary to `gpt-4o` (OpenAI), and local fallback to `ollama/qwen2.5-coder:7b`.
- **Mid-Task Outage**: On Turn 2 (during diff generation), an upstream `503 Service Unavailable / Connection Timeout` hits the Anthropic endpoint.
- **Failover Sequence**:
  1. `BifrostGatewayClient` intercepts the outage.
  2. Emits failover log: `▲ Bifrost Outage Fallback: Provider 'claude-3-5-sonnet' failed (APIConnectionError). Failing over to Alternative Cloud -> 'gpt-4o'`.
  3. Seamlessly transfers conversation context to `gpt-4o`.
  4. `gpt-4o` produces the proposed unified diff edit.
  5. Pytest verification passes (`1 passed in 0.04s`).
- **Telemetry**: Full `TokenLedger` table displays per-model breakdown and marks `Fallbacks Triggered: claude-3-5-sonnet`.

### Voiceover / Talking Points
> *"Here we see Nano-Agent tackling a bug in `pricing.py`. It starts on Claude 3.5 Sonnet via Bifrost. Mid-task, Claude encounters an upstream 503 outage. Notice how Nano-Agent immediately detects the failure, catches the exception without crashing, and switches to GPT-4o. GPT-4o takes over mid-stream, applies the replacement block diff, and completes the task cleanly. In our TokenLedger summary, we can see both providers logged and the exact failover trace."*

---

## 2. Demo 2: Budget Guardrail Enforcement (`demo_budget.py`)

### What it Demonstrates
- **Initial Setup**: Developer configures `--budget 0.0020` ($0.0020 USD max spend).
- **Turn 1 Execution**: Agent executes initial inspection and repository indexing on `claude-3-5-sonnet`, consuming $0.00248.
- **Budget Breach Detection**:
  1. The `TokenLedger` logs the call cost and detects that total spend ($0.00248) has exceeded the configured budget cap ($0.0020).
  2. The pre-call / post-call budget guardrail halts the engine immediately before any further API dispatches.
  3. Outputs high-visibility alert: `[Budget Guardrail] Spending limit of $0.0020 exceeded! Total spend reached: $0.0025 across 1 calls.`
- **Telemetry**: Outputs `HALTED: BUDGET CAP EXCEEDED`, showing remaining budget at `$0.00000`, stopping runaway loops and preventing unintended API credit consumption.

### Voiceover / Talking Points
> *"To prevent runaway agent loops and unexpected billing, Nano-Agent enforces strict budget limits. Here, we start a multi-file refactoring task with a micro-budget of two tenths of a cent ($0.0020). After Turn 1 completes, our TokenLedger calculates that the spend has reached $0.00248. The budget guardrail immediately halts the agent with a clear warning. The TokenLedger table displays zero remaining allowance, ensuring complete financial safety."*

---

## 3. Demo 3: Air-Gapped Zero-Cloud Privacy Mode (`demo_privacy.py`)

### What it Demonstrates
- **Initial Setup**: Running with `--private` / `--privacy` on proprietary or confidential IP code.
- **Network Diagnostic**: Simulates an air-gapped security boundary where external WAN is offline / blocked (`api.openai.com` and `api.anthropic.com` are blocked; local `localhost:11434` Ollama is ready).
- **Pre-Flight Sanitization**: Any requested cloud models are stripped from the chain. The effective chain contains exclusively: `ollama/qwen2.5-coder:7b`.
- **Local Execution**:
  1. Agent reads `auth.py` and inspects token expiration logic locally.
  2. Local pytest verification runs and passes on `test_auth_check.py`.
  3. Gateway logs `✔ Provider 'ollama/qwen2.5-coder:7b' answered`.
  4. Monetary cost is exactly `$0.00000` (free local hardware compute).
- **Active Defense Guardrail**: Simulates an attempt to inject an unauthorized cloud model (`gpt-4o`) into the private session. The gateway immediately intercepts before socket transmission and throws `PrivacyViolationError`.

### Voiceover / Talking Points
> *"For enterprise teams working on confidential or proprietary codebases, Nano-Agent offers `--private` mode. Notice the air-gap boundary check: cloud endpoints are completely blocked, while local Ollama is active. Nano-Agent automatically purges all cloud providers from its chain. The task runs entirely on local hardware with zero network packets leaving the machine, resulting in a total cost of $0.0000. Finally, we demonstrate our active defense guardrail: even if a prompt or rogue process attempts to invoke a cloud model like GPT-4o, Bifrost intercepts and blocks it before a single byte leaves the machine."*

