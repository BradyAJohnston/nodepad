import bpy

from . import panel
from . import pref
from bpy.props import IntProperty

CLASSES = panel.CLASSES + pref.CLASSES

from .documenter import Documenter
from .utils import DATADIR_GN
from .style_generator import (
    extract_style_nodes,
    generate_style_classes_file,
    save_style_data_to_json,
    StyleNodeInfo,
    NodeInput,
    EnumOption,
)

__all__ = [
    "Documenter",
    "extract_style_nodes",
    "generate_style_classes_file",
    "save_style_data_to_json",
    "StyleNodeInfo",
    "NodeInput", 
    "EnumOption",
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    # del bpy.types.Scene.node_group_list_int
