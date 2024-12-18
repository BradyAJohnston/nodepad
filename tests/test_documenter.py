import bpy
import nodepad
from nodepad import Documenter
from pathlib import Path
import pytest
from json import load


nodes = [
    "Blend Hair Curves",
    "Displace Hair Curves",
    "Frizz Hair Curves",
    "Roll Hair Curves",
    "Braid Hair Curves",
    "Curve Info",
    "Curve Root",
    "Attach Hair Curves to Surface",
]

DATADIR = Path(bpy.utils.script_paths()[0]).parent / "datafiles/assets/geometry_nodes/"


def test_documenter(snapshot):
    for node_name in nodes:
        bpy.ops.wm.append(
            "EXEC_DEFAULT",
            directory=str(DATADIR / "procedural_hair_node_assets.blend/NodeTree/"),
            filename=node_name,
            use_recursive=True,
        )

        assert snapshot == Documenter(bpy.data.node_groups[node_name]).as_markdown()


def test_documented_with_json(snapshot):
    with open(Path(__file__).parent / "node_info.json") as f:
        extra_json = load(f)

    for node_name in nodes:
        bpy.ops.wm.append(
            "EXEC_DEFAULT",
            directory=str(DATADIR / "procedural_hair_node_assets.blend/NodeTree/"),
            filename=node_name,
            use_recursive=True,
        )

        doc = Documenter(bpy.data.node_groups[node_name])
        without_info = doc.as_markdown()
        doc.lookup_info(extra_json)
        assert without_info != doc.as_markdown()
        assert snapshot == doc.as_markdown()
