from bpy.types import AddonPreferences
from . import __package__


class MN_PT_NodePadPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        self.layout.label(text="test")


CLASSES = [MN_PT_NodePadPreferences]
