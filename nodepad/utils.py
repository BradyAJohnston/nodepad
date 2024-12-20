import bpy
from pathlib import Path

DATADIR_GN = (
    Path(bpy.utils.script_paths()[0]).parent / "datafiles/assets/geometry_nodes/"
)


def append_default_asset_node(
    node_name: str, blendfile: str = "procedural_hair_node_assets.blend"
):
    bpy.ops.wm.append(
        "EXEC_DEFAULT",
        directory=str(DATADIR_GN / f"{blendfile}/NodeTree/"),
        filename=node_name,
        use_recursive=True,
    )
