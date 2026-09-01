"""Lazy universe tree (spec §25, §48–§49).

The tree is semantic and potentially unbounded; renders are materialized
per node. Serializes to/from a run's ``tree.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from multiverse.schemas import NodeStatus, Universe


class UniverseTree(BaseModel):
    root: str = "0"
    nodes: dict[str, Universe] = Field(default_factory=dict)

    @classmethod
    def new(cls, root_premise: str = "original reality") -> "UniverseTree":
        root = Universe(id="0", premise=root_premise, depth=0, status=NodeStatus.READY)
        return cls(root="0", nodes={"0": root})

    def children(self, node_id: str) -> list[Universe]:
        return [n for n in self.nodes.values() if n.parent_id == node_id]

    def add_child(self, parent_id: str, premise: str, divergence: str, **kwargs) -> Universe:
        parent = self.nodes[parent_id]
        child_id = f"{parent_id}.{len(self.children(parent_id)) + 1}"
        child = Universe(
            id=child_id,
            parent_id=parent_id,
            premise=premise,
            divergence=divergence,
            # Semantic state recurses; pixel reference stays the source.
            world_state={**parent.world_state, "divergence": divergence, **kwargs.pop("world_state", {})},
            depth=parent.depth + 1,
            status=NodeStatus.VIRTUAL,
            **kwargs,
        )
        self.nodes[child_id] = child
        return child

    def ancestry(self, node_id: str) -> list[Universe]:
        chain: list[Universe] = []
        current: str | None = node_id
        while current is not None:
            node = self.nodes[current]
            chain.append(node)
            current = node.parent_id
        return list(reversed(chain))

    def save(self, path: Path) -> None:
        # Atomic: concurrent readers (player, rtmp, exports) never see a
        # torn file.
        tmp = path.with_suffix(".tmp")
        tmp.write_text(self.model_dump_json(indent=2))
        tmp.replace(path)

    @classmethod
    def load(cls, path: Path) -> "UniverseTree":
        return cls.model_validate(json.loads(path.read_text()))
