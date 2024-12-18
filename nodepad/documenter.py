import bpy
import pathlib
import sys

from .interface import InterfaceGroup, InterfaceItem
from . import markdown
from typing import List

TOP_FOLDER = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(TOP_FOLDER))


class Title(str):
    def as_markdown(self, level: int = 2) -> str:
        return "{} {}".format("#" * level, self)


class Video(str):
    def as_markdown(self, text="") -> str:
        string = self
        if not string.endswith(".mp4"):
            string += ".mp4"
        return f"![{text}]({string})\n"


class Description(str):
    def as_markdown(self) -> str:
        if self == "":
            return ""
        return "\n{}\n".format(self)


class Videos(list):
    def as_markdown(self) -> str:
        return "\n".join([x.as_markdown() for x in self])


class Documenter:
    def __init__(self, tree: bpy.types.NodeTree) -> None:
        self.tree = tree
        self.level: int = 2
        self.title: Title = Title(tree.name)
        self.items = [InterfaceItem(x) for x in tree.interface.items_tree]
        self.inputs = InterfaceGroup([x for x in self.items if x.is_input])
        self.outputs = InterfaceGroup(
            [x for x in self.items if x.is_output], is_output=True
        )
        self.level = 2
        self._description: Description = Description(tree.description)
        self._links: list[str] = []
        self._video_links: list[Video] = []

    @property
    def name(self) -> str:
        return self.tree.name

    @property
    def description(self) -> Description:
        return self._description

    @property
    def videos(self) -> Videos:
        return Videos([x for x in self._video_links])

    def lookup_info(self, extra_json: dict) -> None:
        try:
            for link in extra_json[self.name]["videos"]:
                self._video_links.append(Video(link))
        except KeyError:
            pass

    def collect_items(self):
        items = [
            self.title.as_markdown(level=self.level),
            self.description.as_markdown(),
            self.videos.as_markdown(),
            self.outputs.as_markdown("Outputs"),
            self.inputs.as_markdown("Inputs"),
        ]
        return [item for item in items if item is not None]

    def as_markdown(self) -> str:
        text = "\n"
        text += "\n".join(self.collect_items())
        return text


class TreeDocumenter(Documenter):
    def __init__(self, tree: bpy.types.NodeTree) -> None:
        super().__init__(tree=tree)
