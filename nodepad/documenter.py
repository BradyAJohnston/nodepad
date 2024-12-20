import bpy
import pathlib
import sys

from .interface import InterfaceGroup, InterfaceSocket

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
    """
    A class to document a Blender NodeTree.

    Parameters
    ----------
    tree : bpy.types.NodeTree
        The Blender NodeTree to document.

    Attributes
    ----------
    tree : bpy.types.NodeTree
        The Blender NodeTree being documented.
    level : int
        The markdown heading level for the title.
    title : Title
        The title of the NodeTree.
    items : list of InterfaceItem
        The items in the NodeTree's interface.
    inputs : InterfaceGroup
        The input items in the NodeTree's interface.
    outputs : InterfaceGroup
        The output items in the NodeTree's interface.

    Properties
    ----------
    name : str
        The name of the NodeTree.
    description : Description
        The description of the NodeTree.
    videos : Videos
        The videos related to the NodeTree.

    """

    def __init__(self, tree: bpy.types.NodeTree) -> None:
        self.tree = tree
        self.level: int = 2
        self.title: Title = Title(tree.name)
        self.items = [InterfaceSocket(x) for x in tree.interface.items_tree]
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

    @description.setter
    def description(self, value: str) -> None:
        self._description = Description(value)

    @property
    def videos(self) -> Videos:
        return Videos([x for x in self._video_links])

    def lookup_info(self, extra_json: dict) -> None:
        """
        Populate the video and other additional data from the extra_json dictionary.

        Matches up additional information that isn't currently stored on the nodes themselves

        Parameters
        ----------
        extra_json : dict
            A dictionary containing additional JSON data. It is expected to have a structure where
            `extra_json[self.name]["videos"]` is a list of video links.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        KeyError
            If `self.name` or `"videos"` key is not found in `extra_json`, the exception is caught and ignored.
        """
        try:
            for link in extra_json[self.name]["videos"]:
                self._video_links.append(Video(link))
        except KeyError:
            pass

    def collect_items(self):
        """
        Collects and returns a list of markdown-formatted items.

        This method gathers various attributes of the object, converts them to
        markdown format, and returns a list of these items. Only non-None items
        are included in the returned list.

        Returns
        -------
        list of str
            A list of markdown-formatted strings representing the title,
            description, videos, outputs, and inputs of the object.
        """
        items = [
            self.title.as_markdown(level=self.level),
            self.description.as_markdown(),
            self.videos.as_markdown(),
            self.outputs.as_markdown("Outputs"),
            self.inputs.as_markdown("Inputs"),
        ]
        return [item for item in items if item is not None]

    def as_markdown(self) -> str:
        """
        Convert collected items to a markdown formatted string.

        Returns
        -------
        str
            A string containing the collected items formatted as markdown.
        """
        text = "\n"
        text += "\n".join(self.collect_items())
        return text


class TreeDocumenter(Documenter):
    def __init__(self, tree: bpy.types.NodeTree) -> None:
        super().__init__(tree=tree)
