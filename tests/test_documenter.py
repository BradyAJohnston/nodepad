import bpy
import nodepad
from nodepad import Documenter
from pathlib import Path
import pytest
from json import load

import nodepad.format


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

DATADIR = nodepad.utils.DATADIR_GN


def test_documenter(snapshot):
    for node_name in nodes:
        nodepad.utils.append_default_asset_node(node_name)
        assert snapshot == Documenter(bpy.data.node_groups[node_name]).as_markdown()


def test_documented_with_json(snapshot):
    with open(Path(__file__).parent / "node_info.json") as f:
        extra_json = load(f)

    for node_name in nodes:
        nodepad.utils.append_default_asset_node(node_name)
        doc = Documenter(bpy.data.node_groups[node_name])
        without_info = doc.as_markdown()
        doc.lookup_info(extra_json)
        assert without_info != doc.as_markdown()
        assert snapshot == doc.as_markdown()


def test_format():
    assert nodepad.format.add_type("test", "Test") == "test::Test"
