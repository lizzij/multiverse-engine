"""fal / MiniMax H3 Max adapter (spec §18).

Endpoints:
- image input:  minimax/h3-max/image-to-video
- video input:  minimax/h3-max/reference-to-video

Auth via FAL_KEY. The fal SDK is imported lazily so core never depends on it.
"""

from __future__ import annotations

import os

from multiverse.schemas import (
    RendererCapabilities,
    RenderRequest,
    RenderResult,
    SceneSpec,
    Universe,
)


class H3MaxRenderer:
    @property
    def capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            name="h3-max",
            supports_image_input=True,
            supports_video_reference=True,
            resolutions=["480p", "768p"],
            max_duration_seconds=5.0,
        )

    def is_available(self) -> bool:
        return bool(os.environ.get("FAL_KEY"))

    def estimate_cost(self, request: RenderRequest) -> float | None:
        # Reference-to-video bills output video plus reference tokens, and
        # rates change; query fal for current pricing rather than hard-coding
        # a dollar amount (spec §37). Until wired up, return None (unknown).
        return None

    async def render(
        self, request: RenderRequest, universe: Universe, scene: SceneSpec
    ) -> RenderResult:
        if not self.is_available():
            raise RuntimeError("H3 Max requires fal.ai — set FAL_KEY (see README: BYOK)")
        raise NotImplementedError("H3 Max rendering lands in Phase 0/2 (see ROADMAP.md)")
