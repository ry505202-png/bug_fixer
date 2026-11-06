"""Demo 3: Zero-Cloud Air-Gapped Privacy Mode for Screen Recording.

Scenario:
- The developer runs with --private (or --privacy) for confidential proprietary code.
- External cloud WAN is blocked / disconnected (simulated network isolation).
- The agent strips all cloud models from the fallback chain.
- The task runs 100% locally via Ollama (qwen2.5-coder:7b) without sending a single byte to the cloud.
- Any attempt to route to a cloud provider is actively intercepted and blocked.
"""
import sys
import time
import argparse
from unittest.mock import MagicMock
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agent.config import AgentConfig
from agent.gateway import BifrostGatewayClient, PrivacyViolationError
from agent.engine import AgentEngine
from agent.cli import print_banner, print_summary


console = Console()


def make_mock_tool_call(tool_name: str, arguments_dict: dict, call_id: str = "call_priv_1"):
    import json
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = tool_name
    tc.function.arguments = json.dumps(arguments_dict)
    return tc


def make_mock_response(content: str = "", tool_calls=None, prompt_tokens: int = 200, completion_tokens: int = 50):
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_choice.message.tool_calls = tool_calls
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    mock_resp.usage.prompt_tokens = prompt_tokens
    mock_resp.usage.completion_tokens = completion_tokens
    return mock_resp


def run_privacy_demo(delay: float = 1.0):
    console.clear()

    # 1. Header Banner
    demo_title = Panel(
        "[bold cyan]DEMO 3: ZERO-CLOUD AIR-GAPPED PRIVACY MODE[/bold cyan]\n"
        "[dim]Running --private with cloud network blocked; executing 100% locally on Ollama[/dim]",
        border_style="cyan",
        subtitle="[bold red]Security Level: TOP SECRET / CONFIDENTIAL CODEBASE[/bold red]",
    )
    console.print(demo_title)
    time.sleep(delay)

    # 2. Simulated Network Isolation / Air-Gap Status
    net_table = Table(
        title="[bold yellow]Air-Gap Network Boundary Diagnostic[/bold yellow]",
        border_style="yellow"
    )
    net_table.add_column("Endpoint", style="bold")
    net_table.add_column("Target Host", style="dim")
    net_table.add_column("Connection Status", justify="center")
    net_table.add_column("Privacy Action")

    net_table.add_row(
        "OpenAI API",
        "api.openai.com:443",
        "[bold red]✖ BLOCKED / OFFLINE[/bold red]",
        "[red]Access Denied by Policy[/red]"
    )
    net_table.add_row(
        "Anthropic API",
        "api.anthropic.com:443",
        "[bold red]✖ BLOCKED / OFFLINE[/bold red]",
        "[red]Access Denied by Policy[/red]"
    )
    net_table.add_row(
        "Local Ollama",
        "http://localhost:11434",
        "[bold green]✔ CONNECTED (LOCAL IP)[/bold green]",
        "[green]Permitted (Zero Network Leak)[/green]"
    )
    console.print(net_table)
    time.sleep(delay)

    # 3. Agent Configuration with --private
    config = AgentConfig(
        privacy_mode=True,
        primary_model="claude-3-5-sonnet",      # Intentionally requested cloud model
        fallback_models=["gpt-4o", "ollama/qwen2.5-coder:7b"],
        local_model="ollama/qwen2.5-coder:7b",
        budget_limit_usd=1.00,
        auto_approve=True,
    )

    console.print("\n[bold yellow]Pre-Flight Privacy Filter:[/bold yellow] Stripping all cloud models from chain...")
    effective_chain = config.get_effective_model_chain()
    console.print(f"[bold green]✔ Sanitized Effective Chain:[/bold green] [cyan]{' -> '.join(effective_chain)}[/cyan]\n")
    time.sleep(delay * 0.7)

    print_banner(config)
    time.sleep(delay)

    task_desc = "Inspect proprietary JWT auth token verification in benchmark_repo/auth.py and check TokenExpiredError."
    console.print(f"\n[bold]Incoming Task:[/bold] [italic green]{task_desc}[/italic green]\n")
    time.sleep(delay * 0.8)

    # 4. Setup mock client for local Ollama execution
    resp_turn1 = make_mock_response(
        content="Scanning confidential file benchmark_repo/auth.py locally on Ollama...",
        tool_calls=[
            make_mock_tool_call(
                "read_file",
                {"path": "benchmark_repo/auth.py", "start_line": 1, "end_line": 25},
                call_id="call_priv_read",
            )
        ],
        prompt_tokens=320,
        completion_tokens=45,
    )

    resp_turn2 = make_mock_response(
        content="Local analysis complete. Token verification and TokenExpiredError tested locally against benchmark_repo/tests/test_auth_check.py. All tests pass with zero cloud data transmission.",
        tool_calls=None,
        prompt_tokens=410,
        completion_tokens=60,
    )

    turn_counter = {"count": 0}

    def mocked_chat_completion(model, **kwargs):
        # Strict validation: If ANY cloud model is attempted, raise immediate error!
        if "claude" in model or "gpt" in model:
            raise PrivacyViolationError(
                f"[Privacy Guardrail] Network breach prevented! Attempted dispatch to cloud model '{model}'."
            )

        turn_counter["count"] += 1
        time.sleep(delay * 0.6)
        if turn_counter["count"] == 1:
            return resp_turn1
        return resp_turn2

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = mocked_chat_completion

    gateway = BifrostGatewayClient(config=config, custom_client=mock_client)
    engine = AgentEngine(config=config, gateway=gateway)

    # 5. Run Local Agent Loop
    console.print("[bold yellow]▶ Executing Task Locally via Ollama (Zero External Network Packets)...[/bold yellow]\n")
    time.sleep(delay * 0.5)

    result = engine.run_task(task_desc)

    # 6. Output Summary
    time.sleep(delay * 0.5)
    print_summary(result)
    time.sleep(delay * 0.7)

    # 7. Demonstrate Active Defense Guardrail
    console.print("\n[bold red]⚡ DEMONSTRATING ACTIVE DEFENSE GUARDRAIL:[/bold red]")
    console.print("[dim]Simulating an intentional attempt to inject a cloud model ('gpt-4o') in private mode...[/dim]\n")
    time.sleep(delay * 0.8)

    try:
        gateway.validate_privacy_safety(["gpt-4o"])
    except PrivacyViolationError as pve:
        console.print(
            Panel(
                f"[bold red]✖ CLOUD DISPATCH INTERCEPTED & BLOCKED[/bold red]\n\n"
                f"{pve}\n\n"
                "[bold green]✔ GUARANTEE: Zero bytes transmitted outside localhost.[/bold green]",
                title="[bold red]Bifrost Privacy Guardrail Triggered[/bold red]",
                border_style="red",
            )
        )

    # 8. Final Verification
    time.sleep(delay * 0.5)
    verification_panel = Panel(
        "[bold green]✔ AIR-GAPPED PRIVACY VERIFICATION COMPLETE[/bold green]\n\n"
        "• Network Status:            [bold red]External Cloud Blocked / Offline[/bold red]\n"
        "• Inference Execution:       [bold green]100% Local Ollama (qwen2.5-coder:7b)[/bold green]\n"
        f"• Total Monetary Cost:       [bold green]$0.00000 (Free Local Compute)[/bold green]\n"
        "• External Network Packets:  [bold green]0 Packets / 0 Bytes Leaked[/bold green]\n"
        "• Confidentiality Guarantee: [bold cyan]Proprietary source code remained fully on-device[/bold cyan]",
        title="[bold green]Screen Recording Demo 3 Outcome[/bold green]",
        border_style="green",
    )
    console.print(verification_panel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo 3: Zero-cloud privacy mode.")
    parser.add_argument("--fast", action="store_true", help="Run without dramatic screen-recording delays.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between steps (default: 1.0).")
    args = parser.parse_args()

    step_delay = 0.05 if args.fast else args.delay
    run_privacy_demo(delay=step_delay)

