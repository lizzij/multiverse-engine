"""Renderer registry: name → factory. Providers import lazily."""

from __future__ import annotations

from collections.abc import Callable

from multiverse.renderers.base import Renderer

_FACTORIES: dict[str, Callable[[], Renderer]] = {}


def register(name: str, factory: Callable[[], Renderer]) -> None:
    _FACTORIES[name] = factory


def get(name: str) -> Renderer:
    try:
        return _FACTORIES[name]()
    except KeyError:
        raise KeyError(f"unknown renderer {name!r}; available: {sorted(_FACTORIES)}") from None


def available() -> list[str]:
    return sorted(_FACTORIES)


def _register_builtins() -> None:
    from multiverse.renderers.h3_max import H3MaxRenderer

    register("h3-max", H3MaxRenderer)


_register_builtins()
