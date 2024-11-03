from bpy.types import AddonPreferences
from . import __package__


class NN_PT_NoodleNotesPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        self.layout.label(text="test")


CLASSES = [NN_PT_NoodleNotesPreferences]
