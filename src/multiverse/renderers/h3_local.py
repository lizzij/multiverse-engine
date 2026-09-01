"""Local H3 renderer via a vLLM-Omni OpenAI-compatible server (experimental).

MiniMax H3-Base ships open weights (FL2VA: text + first/last-frame
conditioning; Ref2VA: reference-based) under the MiniMax Community
License, and vLLM-Omni ≥0.26 serves them at an OpenAI-compatible
`/v1/videos`. Point H3_LOCAL_URL at such a server (e.g.
http://localhost:8000) for BYOK-free local generation.

Status: adapter written against the published vLLM-Omni recipe; not yet
validated against a live deployment — expect to adjust field names.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from multiverse.schemas import (
    RendererCapabilities,
    RenderRequest,
    RenderResult,
    SceneSpec,
    Universe,
)


class H3LocalRenderer:
    def __init__(self) -> None:
        self.base_url = os.environ.get("H3_LOCAL_URL", "").rstrip("/")

    @property
    def capabilities(self) -> RendererCapabilities:
        return RendererCapabilities(
            name="h3-local",
            supports_image_input=True,      # FL2VA first/last-frame conditioning
            supports_video_reference=True,  # Ref2VA checkpoint
            resolutions=["480p", "768p"],
            max_duration_seconds=5.0,
        )

    def is_available(self) -> bool:
        if not self.base_url:
            return False
        try:
            import httpx

            return httpx.get(f"{self.base_url}/v1/models", timeout=2).status_code == 200
        except Exception:
            return False

    def estimate_cost(self, request: RenderRequest) -> float | None:
        return 0.0  # local compute

    def generate(
        self,
        prompt: str,
        out_path: Path,
        first_frame_url: str | None = None,
        last_frame_url: str | None = None,
        duration: int = 5,
        timeout: float = 600.0,
    ) -> dict:
        """FL2VA generation through the OpenAI-style async videos API."""
        if not self.is_available():
            raise RuntimeError("h3-local requires H3_LOCAL_URL pointing at a vLLM-Omni server")
        import httpx

        body: dict = {"model": "MiniMax-H3", "prompt": prompt, "seconds": duration}
        if first_frame_url:
            body["first_frame"] = first_frame_url
        if last_frame_url:
            body["last_frame"] = last_frame_url
        with httpx.Client(base_url=self.base_url, timeout=30) as client:
            job = client.post("/v1/videos", json=body).raise_for_status().json()
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                status = client.get(f"/v1/videos/{job['id']}").raise_for_status().json()
                if status.get("status") in ("completed", "succeeded"):
                    content = client.get(f"/v1/videos/{job['id']}/content", timeout=120)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_bytes(content.raise_for_status().content)
                    return {"output_path": str(out_path), "endpoint": "h3-local/v1/videos"}
                if status.get("status") in ("failed", "cancelled"):
                    raise RuntimeError(f"h3-local job failed: {status}")
                time.sleep(1.0)
        raise TimeoutError("h3-local generation timed out")

    async def render(
        self, request: RenderRequest, universe: Universe, scene: SceneSpec
    ) -> RenderResult:
        raise NotImplementedError("use generate(); pipeline wiring lands with the local lane")
