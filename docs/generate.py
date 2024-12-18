import bpy
from nodepad import Documenter
from pathlib import Path


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


with open("example.qmd", "w") as f:
    f.write("# Example Docs")
    for node_name in nodes:
        bpy.ops.wm.append(
            "EXEC_DEFAULT",
            directory=str(DATADIR / "procedural_hair_node_assets.blend/NodeTree/"),
            filename=node_name,
            use_recursive=True,
        )

        f.write(Documenter(bpy.data.node_groups[node_name]).as_markdown())
