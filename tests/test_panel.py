import pytest
from unittest.mock import Mock, MagicMock, patch
from nodepad.panel import draw_node_panel, panel_func, update_node_group_list


class MockItem:
    def __init__(self, item_type="SOCKET", description="", name="test_item"):
        self.item_type = item_type
        self.description = description
        self.name = name


class MockInterface:
    def __init__(self, items=None):
        self.items_tree = items or []


class MockNodeGroup:
    def __init__(self, name="TestNode", description="Test description", items=None):
        self.name = name
        self.description = description
        self.color_tag = "NONE"
        self.interface = MockInterface(items or [])


class MockContext:
    def __init__(self):
        self.scene = Mock()


class MockLayout:
    def __init__(self):
        self.label = Mock()
        self.prop = Mock()
        self.prop_menu_enum = Mock()
        self.panel = Mock(return_value=(Mock(), Mock()))
        self.row = Mock()
        self.column = Mock()
        self.template_list = Mock()


class MockSocket:
    def __init__(self, name="test_socket", socket_type="VALUE", default_value=1.0,
                 has_default=True, has_minmax=False, min_value=0.0, max_value=1.0,
                 subtype=None, description=""):
        self.name = name
        self.socket_type = socket_type
        self.description = description
        self.item_type = "SOCKET"
        
        if has_default:
            self.default_value = default_value
        
        if has_minmax:
            self.min_value = min_value
            self.max_value = max_value
            
        if subtype:
            self.subtype = subtype


# UI List tests removed due to Blender dependency constraints


@patch('bpy.data')
def test_draw_node_panel_basic(mock_bpy_data):
    """Test basic draw_node_panel functionality"""
    # Create mock node group with simple sockets
    items = [
        MockSocket("Input1", "NodeSocketFloat", 1.0),
        MockSocket("Input2", "NodeSocketInt", 5),
    ]
    tree = MockNodeGroup("TestTree", "Test description", items)
    
    layout = MockLayout()
    context = MockContext()
    
    # Call draw_node_panel
    draw_node_panel(tree, layout, context)
    
    # Verify basic properties are set
    layout.label.assert_any_call(text="TestTree")
    layout.prop.assert_any_call(tree, "name")
    layout.prop.assert_any_call(tree, "description")
    layout.prop_menu_enum.assert_any_call(tree, "color_tag")


@patch('bpy.data')
def test_draw_node_panel_with_panels(mock_bpy_data):
    """Test draw_node_panel with panel items that should be skipped"""
    items = [
        MockItem("PANEL", "Panel description", "Panel1"),
        MockSocket("Input1", "NodeSocketFloat", 1.0),
    ]
    tree = MockNodeGroup("TestTree", "Test description", items)
    
    layout = MockLayout()
    context = MockContext()
    
    # Call draw_node_panel
    draw_node_panel(tree, layout, context)
    
    # Verify that only socket items create panels
    # Panel items should be skipped, so only one socket should create a panel
    assert layout.panel.call_count == 1


@patch('bpy.data')
def test_draw_node_panel_socket_with_minmax(mock_bpy_data):
    """Test draw_node_panel with socket that has min/max values"""
    socket_with_minmax = MockSocket("RangedInput", "NodeSocketFloat", 2.0, 
                                   has_minmax=True, min_value=0.0, max_value=10.0)
    # Add hasattr behavior
    socket_with_minmax.min_value = 0.0
    socket_with_minmax.max_value = 10.0
    
    items = [socket_with_minmax]
    tree = MockNodeGroup("TestTree", "Test description", items)
    
    layout = MockLayout()
    context = MockContext()
    
    # Mock the panel return
    header_mock = Mock()
    panel_mock = Mock()
    panel_mock.row = Mock(return_value=Mock())
    panel_mock.row.return_value.row = Mock(return_value=Mock())
    panel_mock.row.return_value.row.return_value.column = Mock()
    panel_mock.prop = Mock()
    layout.panel.return_value = (header_mock, panel_mock)
    
    # Call draw_node_panel
    draw_node_panel(tree, layout, context)
    
    # Verify panel was created
    layout.panel.assert_called_with("RangedInput", default_closed=False)


@patch('bpy.data')
def test_draw_node_panel_no_panel(mock_bpy_data):
    """Test draw_node_panel when panel is None"""
    items = [MockSocket("Input1", "NodeSocketFloat", 1.0)]
    tree = MockNodeGroup("TestTree", "Test description", items)
    
    layout = MockLayout()
    context = MockContext()
    
    # Mock panel return as None
    header_mock = Mock()
    layout.panel.return_value = (header_mock, None)
    
    # Call draw_node_panel - should handle None panel gracefully
    draw_node_panel(tree, layout, context)
    
    # Should still create the panel attempt
    layout.panel.assert_called_with("Input1", default_closed=False)


# bpy.data patching tests removed due to read-only constraints


# UI List zero items test removed due to Blender dependency constraints


def test_draw_node_panel_non_socket_item():
    """Test draw_node_panel with non-socket items"""
    items = [
        MockItem("OTHER", "Other description", "Other1"),  # Not a socket, not a panel
        MockSocket("Input1", "NodeSocketFloat", 1.0),
    ]
    tree = MockNodeGroup("TestTree", "Test description", items)
    
    layout = MockLayout()
    context = MockContext()
    
    # Call draw_node_panel
    draw_node_panel(tree, layout, context)
    
    # Should only create panel for socket items
    assert layout.panel.call_count == 1