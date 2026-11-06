"""Test script to dispatch a request through the local Bifrost gateway."""
import os
import sys
from pathlib import Path
from openai import OpenAI, APIConnectionError, APIStatusError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def load_env():
    """Load key-value pairs from .env if present."""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k not in os.environ:
                os.environ[k] = v


def main():
    load_env()

    base_url = os.getenv("BIFROST_BASE_URL", "http://localhost:8080/v1")
    api_key = os.getenv("BIFROST_VIRTUAL_KEY", os.getenv("BIFROST_API_KEY", "sk-bf-nano-agent-secret-key"))
    user_id = os.getenv("AGENT_USER_ID", "test-user-1")

    # Target model: allow CLI arg or default to fallback-managed model
    model = sys.argv[1] if len(sys.argv) > 1 else "claude-3-5-sonnet"

    console.print(
        Panel(
            f"[bold cyan]Gateway URL :[/bold cyan] {base_url}\n"
            f"[bold cyan]Virtual Key :[/bold cyan] {api_key}\n"
            f"[bold cyan]Model Target:[/bold cyan] {model}\n"
            f"[bold cyan]User ID     :[/bold cyan] {user_id}",
            title="[bold green]Bifrost Gateway Probe[/bold green]",
            border_style="green",
        )
    )

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={
            "x-bifrost-user": user_id,
            "x-user-id": user_id,
        },
        timeout=20.0,
    )

    console.print(f"[yellow]Sending test request to model '{model}' through Bifrost...[/yellow]")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Return exactly: 'Bifrost gateway operational.'",
                }
            ],
            temperature=0.0,
            max_tokens=30,
        )

        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else (prompt_tokens + completion_tokens)
        resolved_model = getattr(response, "model", model)

        # Output Table
        table = Table(title="[bold green]✔ Bifrost Response Received[/bold green]", border_style="green")
        table.add_column("Metric", style="bold")
        table.add_column("Value")

        table.add_row("Model Handled", str(resolved_model))
        table.add_row("Prompt Tokens", str(prompt_tokens))
        table.add_row("Completion Tokens", str(completion_tokens))
        table.add_row("Total Tokens", f"[bold]{total_tokens}[/bold]")

        console.print(table)
        console.print(
            Panel(
                content.strip(),
                title="[bold green]Completion Content[/bold green]",
                border_style="green",
            )
        )

    except APIConnectionError as e:
        console.print(
            Panel(
                f"[bold red]Connection Failed:[/bold red] Could not reach Bifrost at [cyan]{base_url}[/cyan].\n\n"
                "[bold yellow]To start Bifrost locally:[/bold yellow]\n"
                "1. Open a new terminal.\n"
                "2. Run: [green]./run_bifrost.ps1[/green] (or [green]npx -y @maximhq/bifrost -app-dir ./bifrost[/green])\n"
                "3. Once listening on port 8080, run this test script again.",
                title="[bold red]Bifrost Offline[/bold red]",
                border_style="red",
            )
        )
        sys.exit(2)

    except APIStatusError as e:
        console.print(
            Panel(
                f"[bold yellow]Gateway Connected, but upstream provider rejected request:[/bold yellow]\n"
                f"HTTP Status: [red]{e.status_code}[/red]\n"
                f"Message: {e.message}\n\n"
                "[dim]Tip: Update your cloud API keys in `.env` or route to Ollama: `python test_bifrost.py ollama/qwen2.5-coder:7b`[/dim]",
                title="[bold yellow]Upstream Provider Error[/bold yellow]",
                border_style="yellow",
            )
        )
        sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Unexpected error: {type(e).__name__}: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

