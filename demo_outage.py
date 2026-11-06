"""Demo 1: Resilient Multi-Provider Outage Failover for Screen Recording.

Scenario:
- Primary Provider: claude-3-5-sonnet (via Bifrost)
- Secondary Provider: gpt-4o (via Bifrost)
- Local Fallback: ollama/qwen2.5-coder:7b (via Bifrost)

Mid-task, claude-3-5-sonnet experiences an upstream 503 outage.
BifrostGatewayClient catches the error, logs the failover alert,
switches to gpt-4o without losing context, and completes the task.
"""
import sys
import time
import argparse
from unittest.mock import MagicMock
from openai import APIConnectionError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.config import AgentConfig
from agent.gateway import BifrostGatewayClient
from agent.engine import AgentEngine
from agent.cli import print_banner, print_summary


console = Console()


def make_mock_tool_call(tool_name: str, arguments_dict: dict, call_id: str = "call_outage_1"):
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


def run_outage_demo(delay: float = 1.0):
    console.clear()
    
    # 1. Header Banner
    demo_title = Panel(
        "[bold cyan]DEMO 1: BIFROST MULTI-PROVIDER RESILIENCE & OUTAGE FAILOVER[/bold cyan]\n"
        "[dim]Simulating primary provider failure mid-task with automatic, zero-downtime failover[/dim]",
        border_style="cyan",
        subtitle="[bold yellow]Scenario: Primary Cloud Outage (503 Service Unavailable)[/bold yellow]",
    )
    console.print(demo_title)
    time.sleep(delay)

    # 2. Configuration Setup
    config = AgentConfig(
        privacy_mode=False,
        primary_model="claude-3-5-sonnet",
        fallback_models=["gpt-4o", "ollama/qwen2.5-coder:7b"],
        local_model="ollama/qwen2.5-coder:7b",
        budget_limit_usd=1.00,
        auto_approve=True,
    )
    print_banner(config)
    time.sleep(delay)

    task_desc = "Fix percentage discount bug in benchmark_repo/pricing.py where discount is subtracted directly."
    console.print(f"\n[bold]Incoming Task:[/bold] [italic green]{task_desc}[/italic green]\n")
    time.sleep(delay * 0.8)

    # 3. Setup mock client demonstrating realistic multi-turn failover
    # Turn 1: Primary (claude-3-5-sonnet) inspects repo (succeeds)
    resp_turn1 = make_mock_response(
        content="Inspecting repository signatures. Found calculate_discounted_price in pricing.py.",
        tool_calls=[
            make_mock_tool_call(
                "read_file",
                {"path": "benchmark_repo/pricing.py", "start_line": 50, "end_line": 65},
                call_id="call_inspect_1",
            )
        ],
        prompt_tokens=420,
        completion_tokens=65,
    )

    # Turn 2: Primary (claude-3-5-sonnet) fails with 503 outage!
    # Fallback (gpt-4o) takes over and provides the edit_file tool call
    resp_turn2_fallback = make_mock_response(
        content="Located bug on line 57. Generating replacement block to compute proportional discount.",
        tool_calls=[
            make_mock_tool_call(
                "edit_file",
                {
                    "path": "benchmark_repo/pricing.py",
                    "search_block": "    # BUG: subtracting raw discount_percent instead of percentage of price\n    return price - discount_percent",
                    "replace_block": "    discount_amount = price * (discount_percent / 100.0)\n    return round(price - discount_amount, 2)",
                },
                call_id="call_edit_1",
            )
        ],
        prompt_tokens=510,
        completion_tokens=90,
    )

    # Turn 3: Secondary (gpt-4o) executes pytest check and finishes
    resp_turn3 = make_mock_response(
        content="Ran pytest on benchmark_repo/tests/test_pricing.py. 1 passed in 0.04s. The discount calculation bug has been successfully resolved under the failover provider.",
        tool_calls=None,
        prompt_tokens=480,
        completion_tokens=55,
    )

    call_count = {"claude": 0, "gpt4o": 0}

    def mocked_chat_completion(model, **kwargs):
        if "claude" in model:
            call_count["claude"] += 1
            if call_count["claude"] == 1:
                # Turn 1: Claude answers normally
                time.sleep(delay * 0.5)
                return resp_turn1
            else:
                # Turn 2: Primary provider suddenly crashes / network timeout
                time.sleep(delay * 0.7)
                console.print(
                    Panel(
                        "[bold red]⚡ SIMULATED UPSTREAM OUTAGE DETECTED[/bold red]\n"
                        "[red]Provider: Anthropic / claude-3-5-sonnet\n"
                        "HTTP Status: 503 Service Unavailable (Upstream API Down)[/red]",
                        border_style="red",
                    )
                )
                time.sleep(delay * 0.6)
                raise APIConnectionError(
                    request=MagicMock(),
                    message="Anthropic API 503 Service Unavailable (Upstream gateway timeout)",
                )

        elif "gpt-4o" in model:
            call_count["gpt4o"] += 1
            time.sleep(delay * 0.5)
            if call_count["gpt4o"] == 1:
                return resp_turn2_fallback
            else:
                return resp_turn3

        raise RuntimeError(f"Unexpected model call: {model}")

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mocked_chat_completion

    gateway = BifrostGatewayClient(config=config, custom_client=mock_client)
    engine = AgentEngine(config=config, gateway=gateway)

    # 4. Execute Agent Loop
    console.print("[bold yellow]▶ Starting Agent Execution Loop...[/bold yellow]\n")
    time.sleep(delay * 0.5)

    result = engine.run_task(task_desc)

    # 5. Output Summary
    time.sleep(delay * 0.5)
    print_summary(result)

    # 6. Verification Highlight
    verification_panel = Panel(
        "[bold green]✔ RESILIENCE TEST PASSED[/bold green]\n\n"
        f"• Initial Primary Provider: [cyan]{config.primary_model}[/cyan] (failed on Turn 2)\n"
        f"• Seamless Failover Provider: [cyan]{result.models_used[-1]}[/cyan] (recovered & completed task)\n"
        f"• Task Outcome: [bold green]100% Resolved[/bold green] without human intervention or data loss\n"
        f"• Gateway Fallback Trace: [yellow]{' -> '.join(result.fallbacks_triggered)}[/yellow] -> [bold green]{result.models_used[-1]}[/bold green]",
        title="[bold green]Screen Recording Demo 1 Outcome[/bold green]",
        border_style="green",
    )
    console.print(verification_panel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo 1: Multi-provider outage fallback.")
    parser.add_argument("--fast", action="store_true", help="Run without dramatic screen-recording delays.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between steps (default: 1.0).")
    args = parser.parse_args()

    step_delay = 0.05 if args.fast else args.delay
    run_outage_demo(delay=step_delay)

