"""Multiverse CLI.

Every command has a deterministic noninteractive --json mode (spec §42).
`multiverse source.mp4` is shorthand for `multiverse live source.mp4`.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

import typer
from rich.console import Console

from multiverse import __version__
from multiverse.renderers import registry

cli = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

_COMMANDS = {"doctor", "seed", "live", "generate", "branch", "export",
             "inspect", "status", "--help"}


def app() -> None:
    """Entry point. Rewrites `multiverse <file>` into `multiverse live <file>`."""
    if len(sys.argv) > 1 and sys.argv[1] not in _COMMANDS and Path(sys.argv[1]).exists():
        sys.argv.insert(1, "live")
    cli()


def _emit(payload: dict, json_output: bool, human: str) -> None:
    if json_output:
        print(json.dumps(payload, indent=2))
    else:
        console.print(human)


def _load_manifest(run_dir: Path) -> dict:
    manifest = run_dir / "manifest.json"
    if not manifest.exists():
        console.print(f"[red]no manifest in {run_dir}[/red]")
        raise typer.Exit(1)
    return json.loads(manifest.read_text())


@cli.command()
def doctor(json_output: bool = typer.Option(False, "--json")) -> None:
    """Check media tools, credentials, and renderers."""
    ffmpeg = shutil.which("ffmpeg") is not None
    fal = bool(os.environ.get("FAL_KEY"))
    renderers = {name: registry.get(name).is_available() for name in registry.available()}
    planner = (
        "gemini" if os.environ.get("GEMINI_API_KEY")
        else "anthropic-api" if os.environ.get("ANTHROPIC_API_KEY")
        else "claude-cli" if shutil.which("claude") else None
    )
    ready = ffmpeg and any(renderers.values())
    report = {
        "version": __version__,
        "ready": ready,
        "ffmpeg": ffmpeg,
        "fal": fal,
        "planner": planner,
        "renderers": renderers,
        "recommended_renderer": "h3-max" if renderers.get("h3-max") else None,
    }
    if json_output:
        print(json.dumps(report, indent=2))
        raise typer.Exit(0 if ready else 1)
    console.print("[bold]Multiverse Doctor[/bold]\n")
    console.print(f"{'✓' if ffmpeg else '✗'} ffmpeg")
    console.print(f"{'✓' if fal else '○'} fal.ai (FAL_KEY)")
    console.print(f"{'✓' if planner else '✗'} storyboard planner ({planner or 'none'})")
    for name, ok in renderers.items():
        console.print(f"{'✓' if ok else '○'} renderer {name}")
    console.print()
    if ready:
        console.print("[bold green]Ready to split reality.[/bold green]")
    else:
        console.print("[yellow]Not ready.[/yellow] Set FAL_KEY, or install ffmpeg.")
    raise typer.Exit(0 if ready else 1)


@cli.command()
def seed(
    prompt: str,
    out: Path = typer.Option(Path("seed.mp4"), "--out"),
    duration: int = typer.Option(5, "--duration", help="5-15 seconds"),
    resolution: str = typer.Option("768p", "--resolution", help="480p | 768p"),
    aspect: str = typer.Option("1:1", "--aspect"),
    seed_value: int | None = typer.Option(None, "--seed"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Generate an original source moment via H3 Max text-to-video.

    A generated seed is fully synthetic — no copyright exposure — and can be
    branched like any other source. Billed to your fal account.
    """
    from multiverse.renderers.h3_max import generate_seed

    try:
        meta = generate_seed(
            prompt, out, duration=duration, resolution=resolution,
            aspect_ratio=aspect, seed=seed_value,
        )
    except Exception as exc:  # provider errors (auth, balance, validation) → clean message
        _emit({"error": "seed_failed", "message": str(exc)}, json_output,
              f"[red]{exc}[/red]")
        raise typer.Exit(1) from None
    _emit(meta, json_output,
          f"[green]✓[/green] seed written to [bold]{meta['output_path']}[/bold]\n"
          f"  next: [dim]multiverse live {meta['output_path']}[/dim]")


def _run_engine(seed_path: Path, run_dir: Path, json_output: bool, **kwargs) -> None:
    from multiverse.realtime.live import run_live

    if not json_output:
        console.print(f"run dir: [bold]{run_dir}[/bold]")
        console.print(
            f"player:  http://localhost:8642/web/player.html?run={run_dir}"
            "   (serve with: uv run python scripts/serve.py)"
        )
    engine = run_live(seed_path, run_dir, **kwargs)
    summary = {
        "run": str(run_dir),
        "renders_ok": engine.pool.completed,
        "renders_failed": engine.pool.failed,
        "cycles": engine.cycle_log,
    }
    _emit(summary, json_output,
          f"[green]done[/green]: {engine.pool.completed} ok, {engine.pool.failed} failed")


@cli.command()
def live(
    source: Path,
    cycles: int = typer.Option(2, "--cycles", help="dive cycles (~14 renders each)"),
    depth: int = typer.Option(3, "--depth"),
    branches: int = typer.Option(2, "--branches"),
    duration: int = typer.Option(5, "--duration"),
    resolution: str = typer.Option("480p", "--resolution"),
    run_dir: Path | None = typer.Option(None, "--run-dir", help="resume/extend an existing run"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Run the live branching engine on SOURCE (1→2→4→8 → dive → repeat)."""
    run_dir = run_dir or Path("runs") / f"stream-{time.strftime('%Y%m%d-%H%M%S')}"
    _run_engine(source, run_dir, json_output, cycles=cycles, depth=depth,
                branches=branches, duration=duration, resolution=resolution)


@cli.command()
def generate(
    source: Path,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Analyze SOURCE and branch it once (a single non-interactive cycle)."""
    run_dir = Path("runs") / f"gen-{time.strftime('%Y%m%d-%H%M%S')}"
    _run_engine(source, run_dir, json_output, cycles=1)


@cli.command()
def branch(
    run_dir: Path,
    node: str = typer.Option(..., "--node", help="node id to continue the story from"),
    cycles: int = typer.Option(1, "--cycles"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Branch an existing run from NODE (branch-the-winner, spec §31)."""
    manifest = _load_manifest(run_dir)
    if manifest["nodes"].get(node, {}).get("status") != "ready":
        _emit({"error": "bad_node", "node": node}, json_output,
              f"[red]node {node} is not READY in this run[/red]")
        raise typer.Exit(1)
    seed_path = run_dir / "renders" / "0.mp4"
    _run_engine(seed_path, run_dir, json_output, cycles=cycles,
                depth=manifest["depth"], branches=manifest["branches"],
                duration=manifest["duration"],
                resolution=manifest.get("resolution", "480p"),
                start_root=node)


@cli.command()
def status(run_dir: Path, json_output: bool = typer.Option(False, "--json")) -> None:
    """Render/cycle status of a run."""
    manifest = _load_manifest(run_dir)
    counts: dict[str, int] = {}
    for n in manifest["nodes"].values():
        counts[n["status"]] = counts.get(n["status"], 0) + 1
    payload = {
        "run": str(run_dir),
        "generated_at": manifest.get("generated_at"),
        "nodes": counts,
        "cycles": manifest["cycles"],
    }
    _emit(payload, json_output,
          "  ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
          + f"\ncycles: {len(manifest['cycles'])}")


@cli.command()
def inspect(run_dir: Path, json_output: bool = typer.Option(False, "--json")) -> None:
    """Print the universe tree of a run."""
    manifest = _load_manifest(run_dir)
    if json_output:
        print(json.dumps(manifest["nodes"], indent=2))
        return
    for nid in sorted(manifest["nodes"]):
        n = manifest["nodes"][nid]
        indent = "  " * nid.count(".")
        console.print(f"{indent}[bold]{nid}[/bold] [{n['status']}] {n['premise'][:70]}")


@cli.command()
def export(
    run_dir: Path,
    preset: str = typer.Option("story", "--preset", help="story | participate"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Export a finished run as a social artifact."""
    from multiverse.compose import export as compose_export

    try:
        if preset == "story":
            out = compose_export.export_story(run_dir)
        elif preset == "participate":
            out = compose_export.export_participate(run_dir)
        else:
            raise ValueError(f"unknown preset {preset!r} (use: story | participate)")
    except Exception as exc:
        _emit({"error": "export_failed", "message": str(exc)}, json_output,
              f"[red]{exc}[/red]")
        raise typer.Exit(1) from None
    _emit({"preset": preset, "output": str(out)}, json_output,
          f"[green]✓[/green] {preset} export: [bold]{out}[/bold]")


if __name__ == "__main__":
    app()
