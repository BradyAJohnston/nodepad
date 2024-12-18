import bpy
from bpy.types import Panel, Context, UILayout, GeometryNodeTree, UIList


class NODEPAD_UL_NodeTrees(UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        layout.label(text=item.name)
        items_to_doc = item.interface.items_tree
        n_items = len(items_to_doc)
        n_docced = 0
        for doc in items_to_doc:
            if doc.item_type == "PANEL":
                n_items -= 1
            if doc.description != "":
                n_docced += 1
        layout.label(text=f"{n_docced} / {n_items} ({(n_docced/n_items):.0%})")

    def filter_items(self, context, data, property):
        items = getattr(data, property)
        filtered = [self.bitflag_filter_item] * len(items)

        for i, item in enumerate(items):
            if item.name.startswith("."):
                filtered[i] &= ~self.bitflag_filter_item
        ordered = []
        return filtered, ordered


def draw_node_panel(tree: GeometryNodeTree, layout: UILayout, context: Context):
    layout.label(text=tree.name)
    layout.prop(tree, "name")
    layout.prop(tree, "description")
    layout.prop_menu_enum(tree, "color_tag")
    for item in tree.interface.items_tree:
        if item.item_type == "PANEL":
            continue

        if item.item_type != "SOCKET":
            continue

        header, panel = layout.panel(item.name, default_closed=False)
        header.label(text=item.name)
        if panel is None:
            continue
        panel.prop(item, "name")
        row = panel.row()
        panel.prop(item, "description", text="", text_ctxt=item.name)
        if not hasattr(item, "default_value"):
            continue
        row = panel.row()
        row.prop_menu_enum(item, "socket_type", text=item.socket_type)
        if hasattr(item, "subtype"):
            row.prop_menu_enum(item, "subtype")
        # row.split(factor=0.1)

        # row = panel.row()
        if hasattr(item, "min_value"):
            row = row.row(align=True)
            row.column().prop(item, "min_value", text="")
            row.column().prop(item, "default_value", text="")
            row.column().prop(item, "max_value", text="")
        else:
            row.prop(item, "default_value", text="")


def panel_func(layout: UILayout, context: Context):
    layout.label(text="Nodes")
    trees = bpy.data.node_groups
    names = [tree.name for tree in trees]
    names.sort()
    for tree in [trees[name] for name in names if not name.startswith(".")]:
        draw_node_panel(tree, layout, context)


# Update function to populate the list
def update_node_group_list(context):
    scene = context.scene
    scene.node_group_list.clear()

    for ng in bpy.data.node_groups:
        item = scene.node_group_list.add()
        item.name = ng.name


# update_node_group_list()


class NN_PT_Node_Pad(Panel):
    bl_label = "NodePad"
    bl_idname = "NODE_PT_nn_Node_Pad"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context: Context):
        layout = self.layout
        layout.template_list(
            "NODEPAD_UL_NodeTrees",
            "a_panel_name",
            bpy.data,
            "node_groups",
            context.scene,
            "node_group_list_int",
        )
        draw_node_panel(
            bpy.data.node_groups[context.scene.node_group_list_int], layout, context
        )


CLASSES = [NN_PT_Node_Pad, NODEPAD_UL_NodeTrees]
