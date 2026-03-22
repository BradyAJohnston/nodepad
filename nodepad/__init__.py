import bpy

from . import panel, pref, utils
from .documenter import Documenter
from .style_generator import (
    EnumOption,
    NodeInput,
    StyleNodeInfo,
    extract_style_nodes,
    generate_style_classes_file,
    save_style_data_to_json,
)

CLASSES = panel.CLASSES + pref.CLASSES
__all__ = [
    "utils",
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
