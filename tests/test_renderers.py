import pytest

from multiverse.renderers import registry
from multiverse.renderers.base import Renderer
from multiverse.renderers.h3_max import build_seed_payload
from multiverse.scene.prompts import compile_prompt
from multiverse.schemas import SceneSpec, Universe


def test_h3_max_is_registered():
    assert "h3-max" in registry.available()
    renderer = registry.get("h3-max")
    assert isinstance(renderer, Renderer)
    caps = renderer.capabilities
    assert caps.supports_video_reference
    assert "768p" in caps.resolutions


def test_prompt_compiler_preserves_and_diverges():
    scene = SceneSpec(summary="two characters arguing in a garage")
    universe = Universe(
        id="0.1",
        parent_id="0",
        premise="AI-controlled aquatic civilization",
        visible_consequences=["robotic aquatic transit"],
    )
    prompt = compile_prompt(scene, universe, registry.get("h3-max").capabilities)
    assert "Preserve" in prompt
    assert universe.premise in prompt
    assert "robotic aquatic transit" in prompt
    assert "No cuts." in prompt


def test_seed_payload_maps_resolution_and_defaults():
    payload = build_seed_payload("two inventors argue in a garage")
    assert payload["resolution"] == "768P"
    assert payload["aspect_ratio"] == "1:1"
    assert payload["duration"] == 5
    assert payload["prompt_expansion_mode"] == "balanced"
    assert "seed" not in payload


def test_seed_payload_rejects_bad_inputs():
    with pytest.raises(ValueError):
        build_seed_payload("x", resolution="1080p")
    with pytest.raises(ValueError):
        build_seed_payload("x", aspect_ratio="2:1")
    with pytest.raises(ValueError):
        build_seed_payload("x", duration=30)
