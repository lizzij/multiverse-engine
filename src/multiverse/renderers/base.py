"""Renderer protocol. H3 Max is the default provider, not the architecture."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from multiverse.schemas import (
    RendererCapabilities,
    RenderRequest,
    RenderResult,
    SceneSpec,
    Universe,
)


@runtime_checkable
class Renderer(Protocol):
    @property
    def capabilities(self) -> RendererCapabilities: ...

    def is_available(self) -> bool:
        """Cheap credential/config check for `multiverse doctor`."""
        ...

    def estimate_cost(self, request: RenderRequest) -> float | None:
        """Estimated USD for one render; must be surfaced before fan-out (spec §37)."""
        ...

    async def render(
        self, request: RenderRequest, universe: Universe, scene: SceneSpec
    ) -> RenderResult: ...
