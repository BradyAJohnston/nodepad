from typing import List, Union
from bpy.types import (
    NodeTreeInterfaceSocketBool,
    NodeTreeInterfaceSocketColor,
    NodeTreeInterfaceSocketFloat,
    NodeTreeInterfaceSocketInt,
    NodeTreeInterfaceSocketMatrix,
    NodeTreeInterfaceSocketMenu,
    NodeTreeInterfaceSocketRotation,
    NodeTreeInterfaceSocketString,
    NodeTreeInterfaceSocketVector,
)

import bpy
from . import markdown
from . import format


class InterfaceSocket:
    def __init__(
        self,
        item: Union[
            NodeTreeInterfaceSocketBool,
            NodeTreeInterfaceSocketColor,
            NodeTreeInterfaceSocketFloat,
            NodeTreeInterfaceSocketInt,
            NodeTreeInterfaceSocketMatrix,
            NodeTreeInterfaceSocketMenu,
            NodeTreeInterfaceSocketRotation,
            NodeTreeInterfaceSocketString,
            NodeTreeInterfaceSocketVector,
        ],
        round_length: int = 3,
    ) -> None:
        self.item = item
        self.round_length: int = round_length

    @property
    def is_socket(self) -> bool:
        return self.item.item_type == "SOCKET"

    @property
    def is_panel(self) -> bool:
        return self.item.item_type == "PANEL"

    @property
    def is_input(self) -> bool:
        if self.is_panel:
            return False
        return self.item.in_out == "INPUT"

    @property
    def is_output(self) -> bool:
        if self.is_panel:
            return False
        return self.item.in_out == "OUTPUT"

    @property
    def type(self) -> str:
        if self.is_panel:
            return "PANEL"
        return self.item.socket_type.replace("NodeSocket", "")

    @property
    def is_vector(self) -> bool:
        return self.type in ["Vector", "Color", "Rotation", "Matrix"]

    def __len__(self) -> int:
        if self.type == "PANEL":
            return 0
        elif self.type in ["Vector", "Rotation"]:
            return 3
        elif self.type == "Color":
            return 4
        elif self.type == "Matrix":
            return 16
        else:
            return 1

    @property
    def _default(self) -> Union[str, float, int, list]:
        if isinstance(self.item, NodeTreeInterfaceSocketVector):
            return [round(x, self.round_length) for x in self.item.default_value]

        if isinstance(self.item, NodeTreeInterfaceSocketColor):
            return [round(x, self.round_length) for x in self.item.default_value]

        if isinstance(self.item, NodeTreeInterfaceSocketFloat):
            return round(self.item.default_value, self.round_length)

        if isinstance(self.item, NodeTreeInterfaceSocketInt):
            return str(self.item.default_value)

        if isinstance(self.item, NodeTreeInterfaceSocketString):
            return self.item.default_value

        if isinstance(self.item, NodeTreeInterfaceSocketBool):
            return self.item.default_value

        if isinstance(self.item, NodeTreeInterfaceSocketRotation):
            values = [round(x, self.round_length) for x in self.item.default_value]
            return "Euler({}, {}, {}), 'XYZ')".format(*values)

        if isinstance(self.item, NodeTreeInterfaceSocketMatrix):
            return "Identity([4x4])"

        if isinstance(self.item, NodeTreeInterfaceSocketMenu):
            options = list([x.name for x in self.item.node.inputs])[1:]
            return "{} [{}]".format(self.item.default_value, ", ".join(options))

        else:
            return "_None_"

    @property
    def default(self) -> str:
        try:
            if hasattr(self.item, "devault_value"):
                if self.item.default_input != "VALUE":
                    return self.item.default_input.title()

            return str(self._default)
        except AttributeError:
            return "_None_"

    @property
    def default_typed(self) -> str:
        default = self.default

        if default in ["Index", "Position", "ID", "Normal"]:
            return format.add_type(default, "Input")

        if default == "_None_":
            return "_None_"

        return format.add_type(default, self.type)

    @property
    def socket(self) -> str:
        return "{}::{}".format(self.name, self.type)

    @property
    def name(self) -> str:
        return self.item.name

    @property
    def min_value(self) -> str:
        if (
            isinstance(self.item, NodeTreeInterfaceSocketInt)
            or isinstance(self.item, NodeTreeInterfaceSocketFloat)
            or isinstance(self.item, NodeTreeInterfaceSocketVector)
        ):
            return str(round(self.item.min_value, self.round_length))
        else:
            return "_None_"

    @property
    def max_value(self) -> str:
        if (
            isinstance(self.item, NodeTreeInterfaceSocketInt)
            or isinstance(self.item, NodeTreeInterfaceSocketFloat)
            or isinstance(self.item, NodeTreeInterfaceSocketVector)
        ):
            return str(round(self.item.max_value, self.round_length))
        else:
            return "_None_"

    @property
    def description(self) -> str:
        return self.item.description

    def max_length(self) -> int:
        info_to_test: List[str] = [
            self.description,
            self.min_value,
            self.max_value,
            self.default,
            self.type,
        ]
        return max([len(x) for x in info_to_test if x is not None])


class InterfaceGroup:
    def __init__(self, items: List[InterfaceSocket], is_output: bool = False) -> None:
        self.items: List[InterfaceSocket] = items
        self._is_output: bool = is_output
        self.lengths: dict = {attr: self.get_length(attr) for attr in self.attributes}

    @property
    def attributes(self) -> List[str]:
        if self._is_output:
            return ["description", "socket"]
        else:
            return ["socket", "default", "description"]

    def sep(self) -> str:
        string = ""
        for attribute in self.attributes:
            lines = "-" * self.lengths[attribute]
            if attribute == "default":
                string += ":{}:|".format(lines)
            elif attribute == "socket" and self._is_output:
                string += "{}:|".format(lines)
            else:
                string += "{}|".format(lines)

        return "|" + string + "\n"

    def get_length(self, name: str) -> int:
        strings: List[str] = [str(getattr(x, name)) for x in self.items]
        return max([len(x) for x in strings + [name]])

    def __len__(self) -> int:
        return len(self.items)

    def get_padded_attr(self, item: InterfaceSocket, attribute: str) -> str:
        string = getattr(item, attribute)

        if attribute in ["type", "name", "socket"]:
            string = f"`{string}`"

        return string.ljust(self.lengths[attribute])

    def item_to_line(self, item: InterfaceSocket) -> str:
        joined: str = "|".join(
            [self.get_padded_attr(item, attr) for attr in self.attributes]
        )
        return "|" + joined + "|"

    def top_line(self) -> str:
        joined: str = "|".join(
            [attr.title().ljust(self.lengths[attr]) for attr in self.attributes]
        )
        return "|" + joined + "|\n"

    def body(self) -> str:
        return "\n".join([self.item_to_line(x) for x in self.items])

    def tail(self) -> str:
        col_widths: list[int] = [10, 15, 80]
        if self._is_output:
            col_widths = [90, 10]

        widths_str = (
            "{"
            + 'tbl-colwidths="[{}]"'.format(", ".join([str(x) for x in col_widths]))
            + "}"
        )

        return "\n\n: {}".format(widths_str)

    def as_markdown(self, title: str = "", level: int = 3) -> str:
        body: str = self.body()
        if not body:
            return ""
        hashes: str = "#" * level
        lines: str = f"{hashes} {title}\n\n"
        for x in [
            self.top_line(),
            self.sep(),
            self.body(),
            self.tail(),
            "\n",
        ]:
            lines += x

        return lines

    def __repr__(self) -> str:
        return self.as_markdown()
