"""Multiverse CLI.

Every command has a deterministic noninteractive --json mode (spec §42).
`multiverse source.mp4` is shorthand for `multiverse generate source.mp4`.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console

from multiverse import __version__
from multiverse.renderers import registry

cli = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

_COMMANDS = {"doctor", "generate", "branch", "export", "inspect", "status", "--help", "--version"}


def app() -> None:
    """Entry point. Rewrites `multiverse <file>` into `multiverse generate <file>`."""
    if len(sys.argv) > 1 and sys.argv[1] not in _COMMANDS and Path(sys.argv[1]).exists():
        sys.argv.insert(1, "generate")
    cli()


@cli.command()
def doctor(json_output: bool = typer.Option(False, "--json")) -> None:
    """Check media tools, credentials, and renderers."""
    ffmpeg = shutil.which("ffmpeg") is not None
    fal = bool(os.environ.get("FAL_KEY"))
    renderers = {name: registry.get(name).is_available() for name in registry.available()}
    ready = ffmpeg and any(renderers.values())
    report = {
        "version": __version__,
        "ready": ready,
        "ffmpeg": ffmpeg,
        "fal": fal,
        "renderers": renderers,
        "recommended_renderer": "h3-max" if renderers.get("h3-max") else None,
    }
    if json_output:
        print(json.dumps(report, indent=2))
        raise typer.Exit(0 if ready else 1)

    console.print("[bold]Multiverse Doctor[/bold]\n")
    console.print("Media")
    console.print(f"{'✓' if ffmpeg else '✗'} ffmpeg\n")
    console.print("Cloud")
    console.print(f"{'✓' if fal else '○'} fal.ai (FAL_KEY)\n")
    console.print("Renderers")
    for name, ok in renderers.items():
        console.print(f"{'✓' if ok else '○'} {name}" + ("      Recommended" if name == "h3-max" and ok else ""))
    console.print()
    if ready:
        console.print("[bold green]Ready to split reality.[/bold green]")
    else:
        console.print("[yellow]Not ready.[/yellow] Set FAL_KEY to enable H3 Max, or install ffmpeg.")
    raise typer.Exit(0 if ready else 1)


@cli.command()
def generate(
    source: Path,
    renderer: str = typer.Option("h3-max", "--renderer"),
    branches: int = typer.Option(4, "--branches"),
    resolution: str = typer.Option("768p", "--resolution"),
    seed: int | None = typer.Option(None, "--seed"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Analyze SOURCE and branch it into parallel realities."""
    _not_implemented("generate", json_output)


@cli.command()
def branch(
    run_id: str,
    node: str = typer.Option(..., "--node"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Branch NODE of an existing run into four children."""
    _not_implemented("branch", json_output)


@cli.command()
def export(
    run_id: str,
    preset: str = typer.Option("hero", "--preset", help="hero | participate"),
    root: str = typer.Option("0", "--root"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Export a run as a social artifact."""
    _not_implemented("export", json_output)


@cli.command()
def status(run_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    """Show render status for a run."""
    _not_implemented("status", json_output)


@cli.command()
def inspect(run_id: str, json_output: bool = typer.Option(False, "--json")) -> None:
    """Print the universe tree for a run."""
    _not_implemented("inspect", json_output)


def _not_implemented(command: str, json_output: bool) -> None:
    msg = f"`multiverse {command}` lands in Phase 2 (see ROADMAP.md)"
    if json_output:
        print(json.dumps({"error": "not_implemented", "command": command, "message": msg}))
    else:
        console.print(f"[yellow]{msg}[/yellow]")
    raise typer.Exit(2)


if __name__ == "__main__":
    app()
