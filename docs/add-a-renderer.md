# Adding a renderer

Renderers implement the protocol in `src/multiverse/renderers/base.py`:

```python
class Renderer(Protocol):
    @property
    def capabilities(self) -> RendererCapabilities: ...
    def is_available(self) -> bool: ...
    def estimate_cost(self, request: RenderRequest) -> float | None: ...
    async def render(self, request, universe, scene) -> RenderResult: ...
```

Rules:

1. Import your provider SDK **inside the adapter**, never at core import
   time. Declare it as an optional dependency in `pyproject.toml`.
2. `is_available()` must be a cheap credential/config check — it backs
   `multiverse doctor`.
3. `estimate_cost()` must reflect current provider pricing; it is what
   the cost gate surfaces before any fan-out. Return `None` only when the
   cost is genuinely unknowable, never as a shortcut.
4. Compile prompts through `scene/prompts.py` (subclass/parametrize the
   compiler if your provider needs a different format).
5. Register a factory in `renderers/registry.py::_register_builtins`
   (or via an entry point in the future).
6. Add tests using fakes — tests never hit paid APIs.

H3 Max (`h3_max.py`) is the reference implementation.
