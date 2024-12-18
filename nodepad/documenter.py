import bpy
import pathlib
import sys

from .interface import InterfaceGroup, InterfaceItem
from . import markdown
from typing import List

TOP_FOLDER = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(TOP_FOLDER))


class Documenter:
    def __init__(self, tree: bpy.types.NodeTree) -> None:
        self.tree = tree
        self.items = [InterfaceItem(x) for x in tree.interface.items_tree]
        self.inputs = InterfaceGroup([x for x in self.items if x.is_input])
        self.outputs = InterfaceGroup(
            [x for x in self.items if x.is_output], is_output=True
        )
        self.level = 2
        self._links: list[str] = []

    @property
    def name(self) -> str:
        return self.tree.name

    def title(self) -> str:
        return f"## {self.tree.name.removesuffix('_')}"

    def description(self) -> str:
        return self.tree.description

    def videos(self) -> str | None:
        links = self._links

        if links is None:
            return None
        if len(links) == 0:
            return None

        for x in links:
            if x is None:
                return None

        if isinstance(links, str):
            links = [links]

        if not all([isinstance(x, str) for x in links]):
            raise ValueError(f"All url values must be strings: {links=}")

        videos = "\n\n".join(
            [markdown.Video(x).as_markdown() for x in links if x is not None]
        )

        return "\n\n" + videos + "\n\n"

    def lookup_info(self, extra_json: dict) -> None:
        try:
            self._links = extra_json[self.name]["videos"]
        except KeyError:
            pass

    def collect_items(self):
        items = [
            self.title(),
            self.description(),
            self.videos(),
            self.outputs.as_markdown("Outputs"),
            self.inputs.as_markdown("Inputs"),
        ]
        return [item for item in items if item is not None]

    def as_markdown(self) -> str:
        text = "\n"
        text += "\n\n".join(self.collect_items())
        return text


class TreeDocumenter(Documenter):
    def __init__(self, tree: bpy.types.NodeTree) -> None:
        super().__init__(tree=tree)
