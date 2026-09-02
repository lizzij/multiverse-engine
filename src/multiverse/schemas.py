"""Core data models: SceneSpec, Universe, tree nodes, render results.

See docs/spec.md §14–§16, §49.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Subject(BaseModel):
    id: str
    description: str = ""
    motion: str = ""


class Environment(BaseModel):
    description: str = ""
    era: str = ""
    setting: str = ""


class Action(BaseModel):
    description: str = ""
    timing_notes: str = ""


class Camera(BaseModel):
    shot: str = ""
    movement: str = ""
    framing: str = ""


class SceneSpec(BaseModel):
    """Structured understanding of the source moment.

    ``invariants`` must survive every branch; ``mutable_dimensions`` are
    what a divergence is allowed to change.
    """

    summary: str
    subjects: list[Subject] = Field(default_factory=list)
    environment: Environment = Field(default_factory=Environment)
    action: Action = Field(default_factory=Action)
    camera: Camera = Field(default_factory=Camera)
    invariants: list[str] = Field(default_factory=list)
    mutable_dimensions: list[str] = Field(default_factory=list)


class NodeStatus(StrEnum):
    PLANNED = "planned"
    QUEUED = "queued"
    RENDERING = "rendering"
    READY = "ready"
    FAILED = "failed"
    VIRTUAL = "virtual"


class Universe(BaseModel):
    """One node in the universe tree.

    Children inherit ``world_state`` plus one new ``divergence``, but the
    pixel reference for rendering is always the original source media,
    never a rendered parent (spec §17).
    """

    id: str
    parent_id: str | None = None
    premise: str = ""
    divergence: str = ""
    world_state: dict = Field(default_factory=dict)
    visible_consequences: list[str] = Field(default_factory=list)
    depth: int = 0
    status: NodeStatus = NodeStatus.VIRTUAL
    render_path: str | None = None


class RendererCapabilities(BaseModel):
    name: str
    supports_image_input: bool = False
    supports_video_reference: bool = False
    resolutions: list[str] = Field(default_factory=list)
    max_duration_seconds: float = 5.0


class RenderRequest(BaseModel):
    source_path: str
    universe_id: str
    resolution: str = "768p"
    duration_seconds: float = 5.0
    seed: int | None = None


class RenderResult(BaseModel):
    universe_id: str
    output_path: str
    duration_seconds: float
    fps: float
    provider: str
    cost_usd: float | None = None
