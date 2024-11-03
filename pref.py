import bpy
from bpy.types import AddonPreferences
from . import __package__


class NoodleNotesPreferences(AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        self.layout.label(text="Hello world!")
