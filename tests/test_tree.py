from pathlib import Path

from multiverse.schemas import NodeStatus, SceneSpec
from multiverse.worlds.planner import FIRST_FOUR, plan_first_four
from multiverse.worlds.tree import UniverseTree


def test_first_four_are_curated():
    tree = UniverseTree.new()
    children = plan_first_four(tree, SceneSpec(summary="test scene"))
    assert len(children) == 4
    assert [c.divergence for c in children] == [key for key, _ in FIRST_FOUR]
    assert all(c.parent_id == "0" and c.depth == 1 for c in children)


def test_children_are_virtual_until_materialized():
    tree = UniverseTree.new()
    child = tree.add_child("0", premise="ocean civilization", divergence="ocean")
    assert child.status is NodeStatus.VIRTUAL
    assert child.render_path is None


def test_world_state_recurses():
    tree = UniverseTree.new()
    a = tree.add_child("0", premise="ocean civilization", divergence="ocean")
    b = tree.add_child(a.id, premise="machine ocean", divergence="machines")
    assert b.depth == 2
    assert [n.id for n in tree.ancestry(b.id)] == ["0", a.id, b.id]
    # child inherits parent semantic state plus its own divergence
    assert b.world_state["divergence"] == "machines"


def test_tree_round_trips(tmp_path: Path):
    tree = UniverseTree.new()
    tree.add_child("0", premise="p", divergence="d")
    path = tmp_path / "tree.json"
    tree.save(path)
    loaded = UniverseTree.load(path)
    assert loaded == tree
