"""Demo 2: Budget Guardrail and Spending Limit Enforcement for Screen Recording.

Scenario:
- The developer sets a strict micro-budget: --budget 0.0020 ($0.0020 USD max spend).
- The agent performs initial inspection in Turn 1.
- In Turn 2, the agent reaches the spending limit.
- The pre-call / post-call budget guardrail triggers immediately, preventing
  runaway token loops and halting the agent with a clear, readable explanation.
"""
import sys
import time
import argparse
from unittest.mock import MagicMock
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.config import AgentConfig
from agent.gateway import BifrostGatewayClient
from agent.engine import AgentEngine
from agent.cli import print_banner, print_summary


console = Console()


def make_mock_tool_call(tool_name: str, arguments_dict: dict, call_id: str = "call_budget_1"):
    import json
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(arguments_dict)
    return tc


def make_mock_response(content: str = "", tool_calls=None, prompt_tokens: int = 150, completion_tokens: int = 40):
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_choice.message.tool_calls = tool_calls
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_resp.usage.prompt_tokens = prompt_tokens
    mock_resp.usage.completion_tokens = completion_tokens
    return mock_resp


def run_budget_demo(budget_limit: float = 0.0020, delay: float = 1.0):
    console.clear()

    # 1. Header Banner
    demo_title = Panel(
        "[bold cyan]DEMO 2: BIFROST SPENDING LIMIT & BUDGET GUARD ENFORCEMENT[/bold cyan]\n"
        f"[dim]Setting a strict micro-budget (${budget_limit:.4f}) and demonstrating proactive stoppage[/dim]",
        border_style="cyan",
        subtitle=f"[bold yellow]Scenario: Spending Limit Reached (${budget_limit:.4f} USD)[/bold yellow]",
    )
    console.print(demo_title)
    time.sleep(delay)

    # 2. Configuration Setup
    config = AgentConfig(
        privacy_mode=False,
        primary_model="claude-3-5-sonnet",
        fallback_models=["gpt-4o-mini"],
        budget_limit_usd=budget_limit,
        auto_approve=True,
    )
    print_banner(config)
    time.sleep(delay)

    task_desc = "Audit all repository files and perform multi-file refactoring on auth, pricing, and analytics."
    console.print(f"\n[bold]Incoming Task:[/bold] [italic yellow]{task_desc}[/italic yellow]\n")
    time.sleep(delay * 0.8)

    # 3. Setup mock client demonstrating initial consumption then budget breach
    # Turn 1: Uses 420 prompt tokens + 70 completion tokens on claude-3-5-sonnet
    # Cost = (420/1M)*$3.00 + (70/1M)*$15.00 = $0.00126 + $0.00105 = $0.00231
    # This immediately breaches the $0.0020 budget or exhausts headroom!
    resp_turn1 = make_mock_response(
        content="Analyzing repository AST map and file skeletons across all modules...",
        tool_calls=[
            make_mock_tool_call(
                "read_file",
                {"path": "benchmark_repo/auth.py", "start_line": 1, "end_line": 30},
                call_id="call_inspect_auth",
            )
        ],
        prompt_tokens=450,
        completion_tokens=75,
    )

    resp_turn2 = make_mock_response(
        content="Proceeding to deep refactoring across secondary modules...",
        tool_calls=None,
        prompt_tokens=400,
        completion_tokens=50,
    )

    turn_counter = {"count": 0}

    def mocked_chat_completion(model, **kwargs):
        turn_counter["count"] += 1
        time.sleep(delay * 0.5)
        if turn_counter["count"] == 1:
            return resp_turn1
        return resp_turn2

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mocked_chat_completion

    gateway = BifrostGatewayClient(config=config, custom_client=mock_client)
    engine = AgentEngine(config=config, gateway=gateway)

    # 4. Execute Agent Loop
    console.print(f"[bold yellow]▶ Starting Agent Execution Loop with budget cap ${budget_limit:.4f}...[/bold yellow]\n")
    time.sleep(delay * 0.5)

    result = engine.run_task(task_desc)

    # 5. Output Summary
    time.sleep(delay * 0.5)
    print_summary(result)

    # 6. Verification Highlight
    verification_panel = Panel(
        "[bold red]🛑 BUDGET GUARDRAIL ACTIVE[/bold red]\n\n"
        f"• Configured Safety Budget: [bold yellow]${budget_limit:.4f}[/bold yellow]\n"
        f"• Incurred Cost on Turn 1:  [bold red]${result.cost_tracker.total_cost_usd:.5f}[/bold red]\n"
        f"• Enforcement Mechanism:    [bold cyan]Pre-call / Post-call Budget Guard[/bold cyan]\n"
        f"• Stoppage Reason:          [bold red]{result.stopped_reason.upper()}[/bold red]\n"
        "• Protection Guarantee:     [bold green]Prevented runaway agent loops and unintended API billing[/bold green]",
        title="[bold green]Screen Recording Demo 2 Outcome[/bold green]",
        border_style="red",
    )
    console.print(verification_panel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo 2: Budget limit enforcement.")
    parser.add_argument("--budget", type=float, default=0.0020, help="Micro-budget limit in USD (default: 0.0020).")
    parser.add_argument("--fast", action="store_true", help="Run without dramatic screen-recording delays.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between steps (default: 1.0).")
    args = parser.parse_args()

    step_delay = 0.05 if args.fast else args.delay
    run_budget_demo(budget_limit=args.budget, delay=step_delay)

