import bpy

from . import panel
from bpy.props import CollectionProperty, IntProperty

CLASSES = panel.CLASSES


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.types.Scene.node_group_list_int = IntProperty()


def unregister():
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.node_group_list_int
