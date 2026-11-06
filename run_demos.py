"""Interactive Master Launcher for the 3 Screen Recording Demos.

Usage:
  python run_demos.py          # Launches interactive menu (1, 2, 3, or All)
  python run_demos.py --all    # Runs Demo 1, Demo 2, Demo 3 sequentially
  python run_demos.py --fast   # Quick run without recording pauses
"""
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from demo_outage import run_outage_demo
from demo_budget import run_budget_demo
from demo_privacy import run_privacy_demo


console = Console()


def print_menu():
    menu_content = (
        "[bold cyan]NANO-AGENT SCREEN RECORDING DEMO SUITE[/bold cyan]\n\n"
        "[bold green]1.[/bold green] [bold white]Outage Failover[/bold white]       - Kill primary provider mid-task -> Bifrost failover to secondary\n"
        "[bold yellow]2.[/bold yellow] [bold white]Budget Guard[/bold white]          - Set tiny spending limit ($0.0020) -> Agent halts cleanly\n"
        "[bold red]3.[/bold red] [bold white]Air-Gapped Privacy[/bold white]    - Run --private with network blocked -> 100% local Ollama execution\n"
        "[bold magenta]4.[/bold magenta] [bold white]Run All in Sequence[/bold white]   - Executes Demos 1, 2, and 3 back-to-back\n"
        "[bold dim]q.[/bold dim] [dim]Quit[/dim]"
    )
    console.print(Panel(menu_content, title="[bold green]Maxim AI Hackathon Demos[/bold green]", border_style="cyan"))


def main():
    parser = argparse.ArgumentParser(description="Run Nano-Agent Screen Recording Demos.")
    parser.add_argument("--demo", choices=["1", "2", "3", "all"], help="Directly specify demo to run.")
    parser.add_argument("--all", action="store_true", help="Run all 3 demos sequentially.")
    parser.add_argument("--fast", action="store_true", help="Run without screen recording delays.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between steps.")
    args = parser.parse_args()

    step_delay = 0.05 if args.fast else args.delay

    if args.all or args.demo == "all":
        console.print("\n[bold cyan]>>> Running Demo 1: Resilient Outage Failover[/bold cyan]")
        run_outage_demo(delay=step_delay)
        console.print("\n[bold yellow]Press Enter to proceed to Demo 2...[/bold yellow]")
        if not args.fast:
            input()
        console.print("\n[bold cyan]>>> Running Demo 2: Budget Guardrail[/bold cyan]")
        run_budget_demo(budget_limit=0.0020, delay=step_delay)
        console.print("\n[bold yellow]Press Enter to proceed to Demo 3...[/bold yellow]")
        if not args.fast:
            input()
        console.print("\n[bold cyan]>>> Running Demo 3: Air-Gapped Privacy[/bold cyan]")
        run_privacy_demo(delay=step_delay)
        return

    if args.demo == "1":
        run_outage_demo(delay=step_delay)
        return
    elif args.demo == "2":
        run_budget_demo(budget_limit=0.0020, delay=step_delay)
        return
    elif args.demo == "3":
        run_privacy_demo(delay=step_delay)
        return

    # Interactive prompt
    print_menu()
    choice = Prompt.ask("\n[bold cyan]Select demo to execute[/bold cyan]", choices=["1", "2", "3", "4", "q"], default="1")

    if choice == "1":
        run_outage_demo(delay=step_delay)
    elif choice == "2":
        run_budget_demo(budget_limit=0.0020, delay=step_delay)
    elif choice == "3":
        run_privacy_demo(delay=step_delay)
    elif choice == "4":
        run_outage_demo(delay=step_delay)
        console.print("\n[bold yellow]Press Enter to proceed to Demo 2...[/bold yellow]")
        input()
        run_budget_demo(budget_limit=0.0020, delay=step_delay)
        console.print("\n[bold yellow]Press Enter to proceed to Demo 3...[/bold yellow]")
        input()
        run_privacy_demo(delay=step_delay)
    else:
        console.print("[dim]Exited.[/dim]")


if __name__ == "__main__":
    main()

