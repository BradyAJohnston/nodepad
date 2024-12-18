import bpy

from . import panel
from . import pref
from bpy.props import IntProperty

CLASSES = panel.CLASSES + pref.CLASSES

from .documenter import Documenter

__all__ = [
    "Documenter",
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    # del bpy.types.Scene.node_group_list_int
