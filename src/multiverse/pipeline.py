"""Run orchestration: source → SceneSpec → tree → materialize → compose.

Runs persist under runs/RUN_ID/ (spec §48). Phase 2.
"""

from __future__ import annotations

from pathlib import Path

RUNS_DIR = Path("runs")


def new_run(source_path: Path) -> str:
    raise NotImplementedError("run pipeline lands in Phase 2 (see ROADMAP.md)")
