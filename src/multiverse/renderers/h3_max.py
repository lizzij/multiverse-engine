"""fal / MiniMax H3 Max adapter (spec §18).

Endpoints:
- text input:   minimax/h3-max/text-to-video   (seed generation)
- image input:  minimax/h3-max/image-to-video
- video input:  minimax/h3-max/reference-to-video

Auth via FAL_KEY. The fal SDK is imported lazily so core never depends on it.
"""

from __future__ import annotations

import os
from pathlib import Path

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


TEXT_TO_VIDEO_ENDPOINT = "minimax/h3-max/text-to-video"
REFERENCE_TO_VIDEO_ENDPOINT = "minimax/h3-max/reference-to-video"
IMAGE_TO_VIDEO_ENDPOINT = "minimax/h3-max/image-to-video"

_RESOLUTIONS = {"480p": "480P", "768p": "768P"}
_ASPECTS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")


def build_seed_payload(
    prompt: str,
    duration: int = 5,
    resolution: str = "768p",
    aspect_ratio: str = "1:1",
    seed: int | None = None,
) -> dict:
    """Validate and build the text-to-video request payload."""
    if resolution.lower() not in _RESOLUTIONS:
        raise ValueError(f"resolution must be one of {sorted(_RESOLUTIONS)}")
    if aspect_ratio not in _ASPECTS:
        raise ValueError(f"aspect_ratio must be one of {_ASPECTS}")
    if not 5 <= duration <= 15:
        raise ValueError("duration must be 5-15 seconds")
    payload: dict = {
        "prompt": prompt,
        "duration": duration,
        "resolution": _RESOLUTIONS[resolution.lower()],
        "aspect_ratio": aspect_ratio,
        "prompt_expansion_mode": "balanced",
    }
    if seed is not None:
        payload["seed"] = seed
    return payload


def generate_seed(
    prompt: str,
    out_path: Path,
    duration: int = 5,
    resolution: str = "768p",
    aspect_ratio: str = "1:1",
    seed: int | None = None,
) -> dict:
    """Generate an original source moment via H3 Max text-to-video.

    Returns metadata: output path, expanded prompt, seed, timings.
    """
    payload = build_seed_payload(prompt, duration, resolution, aspect_ratio, seed)
    result = _subscribe_with_retry(TEXT_TO_VIDEO_ENDPOINT, payload)
    _download(result["video"]["url"], out_path)
    return {
        "output_path": str(out_path),
        "endpoint": TEXT_TO_VIDEO_ENDPOINT,
        "prompt": prompt,
        "expanded_prompt": result.get("expanded_prompt"),
        "requested": payload,
        "file_size_bytes": out_path.stat().st_size,
    }


def upload_media(path: Path) -> str:
    """Upload local media to fal storage; returns a URL usable as a reference input."""
    _require_key()
    import fal_client

    return fal_client.upload_file(str(path))


def render_reference(
    video_urls: str | list[str],
    prompt: str,
    out_path: Path,
    duration: int = 5,
    resolution: str = "768p",
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    image_urls: list[str] | None = None,
) -> dict:
    """Render one universe via reference-to-video.

    ``prompt`` refers to refs by modality and order ("Video 1", "Video 2",
    "Image 1" — see scene/prompts.py). For continuations, pass
    [seed_url, parent_tail_url] plus the parent's last frame as image ref
    (docs/realtime-branching.md §2).
    """
    payload = build_seed_payload(prompt, duration, resolution, aspect_ratio, seed)
    payload["reference_video_urls"] = [video_urls] if isinstance(video_urls, str) else video_urls
    if image_urls:
        payload["reference_image_urls"] = image_urls
    result = _subscribe_with_retry(REFERENCE_TO_VIDEO_ENDPOINT, payload)
    _download(result["video"]["url"], out_path)
    return {
        "output_path": str(out_path),
        "endpoint": REFERENCE_TO_VIDEO_ENDPOINT,
        "expanded_prompt": result.get("expanded_prompt"),
        "requested": payload,
        "file_size_bytes": out_path.stat().st_size,
    }


def render_i2v(
    start_image_url: str,
    prompt: str,
    out_path: Path,
    duration: int = 5,
    resolution: str = "480p",
    end_image_url: str | None = None,
    seed: int | None = None,
    hint: str | None = None,
) -> dict:
    """Live-lane render: continuation conditioned on the parent's final frame.

    ~4s end-to-end at 480p (no reference-video tokenization). `hint` keeps
    requests on the same warm fal runner across a stream.
    """
    if resolution.lower() not in _RESOLUTIONS:
        raise ValueError(f"resolution must be one of {sorted(_RESOLUTIONS)}")
    payload: dict = {
        "prompt": prompt,
        "image_url": start_image_url,
        "duration": duration,
        "resolution": _RESOLUTIONS[resolution.lower()],
        "prompt_expansion_mode": "balanced",
    }
    if end_image_url:
        payload["end_image_url"] = end_image_url
    if seed is not None:
        payload["seed"] = seed
    result = _subscribe_with_retry(IMAGE_TO_VIDEO_ENDPOINT, payload, hint=hint)
    _download(result["video"]["url"], out_path)
    return {
        "output_path": str(out_path),
        "endpoint": IMAGE_TO_VIDEO_ENDPOINT,
        "expanded_prompt": result.get("expanded_prompt"),
        "requested": payload,
        "file_size_bytes": out_path.stat().st_size,
    }


def _require_key() -> None:
    if not os.environ.get("FAL_KEY"):
        raise RuntimeError("H3 Max requires fal.ai — set FAL_KEY (see README: BYOK)")


def _subscribe_with_retry(
    endpoint: str,
    payload: dict,
    attempts: int = 8,
    delay: float = 5.0,
    hint: str | None = None,
    priority: str | None = None,
) -> dict:
    """Submit and wait, retrying only the fal account-lock flap (fal-ai/fal#922).

    Other errors (validation, safety checker, real exhausted balance after
    all retries) propagate immediately. `hint` requests runner session
    affinity; `priority` ("low") yields to normal-priority live work —
    both dropped gracefully if the installed fal client predates them.
    """
    import time

    import fal_client

    _require_key()
    extra: dict = {}
    if hint:
        extra["hint"] = hint
    if priority:
        extra["priority"] = priority
    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            try:
                return fal_client.subscribe(endpoint, arguments=payload, **extra)
            except TypeError:
                return fal_client.subscribe(endpoint, arguments=payload)
        except Exception as exc:
            if "User is locked" not in str(exc):
                raise
            last_exc = exc
            time.sleep(delay)
    raise RuntimeError(f"fal account still locked after {attempts} attempts: {last_exc}")


def _download(url: str, out_path: Path) -> None:
    """Atomic download: consumers already playing out_path never see a
    truncated file, and a failed download leaves the old file intact."""
    import httpx

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(out_path.suffix + ".part")
    with httpx.stream("GET", url, timeout=120, follow_redirects=True) as response:
        response.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    tmp.replace(out_path)
