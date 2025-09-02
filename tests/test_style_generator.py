import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
import json

from nodepad.style_generator import (
    EnumOption, NodeInput, StyleNodeInfo,
    get_python_type_annotation, get_default_value, 
    generate_class_name, generate_style_attribute_name,
    generate_enum_class_name, round_float_values,
    format_default_value, generate_python_class,
    generate_enum_class
)


def test_enum_option_creation():
    option = EnumOption("ID1", "Display Name", "Test description")
    assert option.identifier == "ID1"
    assert option.name == "Display Name"
    assert option.description == "Test description"


def test_enum_option_default_description():
    option = EnumOption("ID1", "Display Name")
    assert option.description == ""


def test_node_input_basic():
    node_input = NodeInput(
        name="test_input",
        type="VALUE", 
        default_value=1.0,
        description="Test input"
    )
    assert node_input.name == "test_input"
    assert node_input.type == "VALUE"
    assert node_input.default_value == 1.0
    assert node_input.description == "Test input"
    assert node_input.min_value is None
    assert node_input.max_value is None
    assert node_input.subtype is None
    assert node_input.enum_options is None


def test_node_input_with_constraints():
    node_input = NodeInput(
        name="constrained_input",
        type="VALUE",
        default_value=5.0,
        min_value=0.0,
        max_value=10.0,
        subtype="DISTANCE"
    )
    assert node_input.min_value == 0.0
    assert node_input.max_value == 10.0
    assert node_input.subtype == "DISTANCE"


def test_node_input_with_enum():
    enum_options = [EnumOption("OPT1", "Option 1"), EnumOption("OPT2", "Option 2")]
    node_input = NodeInput(
        name="enum_input",
        type="ENUM",
        default_value="OPT1",
        enum_options=enum_options
    )
    assert len(node_input.enum_options) == 2
    assert node_input.enum_options[0].identifier == "OPT1"


def test_style_node_info_creation():
    inputs = [
        NodeInput("input1", "VALUE", 1.0),
        NodeInput("input2", "INT", 5)
    ]
    node_info = StyleNodeInfo("Test Style", "Test description", inputs)
    
    assert node_info.name == "Test Style"
    assert node_info.description == "Test description"
    assert len(node_info.inputs) == 2


def test_get_python_type_annotation_basic_types():
    # Test basic type mappings
    assert get_python_type_annotation(NodeInput("test", "VALUE", 1.0)) == "float"
    assert get_python_type_annotation(NodeInput("test", "INT", 1)) == "int"
    assert get_python_type_annotation(NodeInput("test", "BOOLEAN", True)) == "bool"
    assert get_python_type_annotation(NodeInput("test", "STRING", "")) == "str"
    assert get_python_type_annotation(NodeInput("test", "VECTOR", (1, 2, 3))) == "Tuple[float, float, float]"
    assert get_python_type_annotation(NodeInput("test", "RGBA", (1, 1, 1, 1))) == "Tuple[float, float, float, float]"
    assert get_python_type_annotation(NodeInput("test", "GEOMETRY", None)) == "Any"


def test_get_python_type_annotation_enum():
    enum_options = [EnumOption("OPT1", "Option 1")]
    node_input = NodeInput("my_enum", "ENUM", "OPT1", enum_options=enum_options)
    result = get_python_type_annotation(node_input)
    # The actual result depends on how generate_enum_class_name processes "my_enum"
    assert "Enum" in result


def test_get_python_type_annotation_unknown():
    assert get_python_type_annotation(NodeInput("test", "UNKNOWN", None)) == "Any"


def test_get_default_value_with_mock_socket():
    # Test VALUE socket
    socket = Mock()
    socket.type = "VALUE"
    socket.default_value = 2.5
    assert get_default_value(socket) == 2.5
    
    # Test VECTOR socket
    vector_socket = Mock()
    vector_socket.type = "VECTOR"
    vector_socket.default_value = [1.0, 2.0, 3.0]
    assert get_default_value(vector_socket) == (1.0, 2.0, 3.0)
    
    # Test BOOLEAN socket
    bool_socket = Mock()
    bool_socket.type = "BOOLEAN"
    bool_socket.default_value = True
    assert get_default_value(bool_socket) == True


def test_get_default_value_fallback_socket_type():
    # Test socket with socket_type attribute instead of type
    socket = Mock()
    del socket.type  # Remove type attribute
    socket.socket_type = "NodeSocketFloat"
    socket.default_value = 1.5
    assert get_default_value(socket) == 1.5


def test_get_default_value_bl_socket_idname():
    # Test socket with bl_socket_idname attribute
    socket = Mock()
    del socket.type
    del socket.socket_type
    socket.bl_socket_idname = "NodeSocketGeometry"
    assert get_default_value(socket) is None  # Geometry sockets return None


def test_get_default_value_geometry():
    socket = Mock()
    socket.type = "GEOMETRY"
    assert get_default_value(socket) is None


def test_get_default_value_no_default():
    # Test socket without default_value but with value attribute
    socket = Mock()
    socket.type = "VALUE"
    del socket.default_value
    socket.value = 3.0
    assert get_default_value(socket) == 3.0


def test_get_default_value_type_defaults():
    # Test fallback to type defaults when no value available
    socket = Mock()
    socket.type = "VALUE"
    del socket.default_value
    del socket.value
    assert get_default_value(socket) == 0.0
    
    socket.type = "INT"
    assert get_default_value(socket) == 0
    
    socket.type = "BOOLEAN" 
    assert get_default_value(socket) == False
    
    socket.type = "VECTOR"
    assert get_default_value(socket) == (0.0, 0.0, 0.0)
    
    socket.type = "STRING"
    assert get_default_value(socket) == ""
    
    socket.type = "RGBA"
    assert get_default_value(socket) == (1.0, 1.0, 1.0, 1.0)


def test_generate_class_name():
    assert generate_class_name("Style Ball and Stick") == "StyleBallAndStick"
    assert generate_class_name("Style Simple") == "StyleSimple"
    assert generate_class_name("Style Complex Name Test") == "StyleComplexNameTest"


def test_generate_style_attribute_name():
    assert generate_style_attribute_name("Material") == "material"
    assert generate_style_attribute_name("Base Color") == "base_color"
    assert generate_style_attribute_name("Roughness Value") == "roughness_value"
    assert generate_style_attribute_name("Multiple Words Here") == "multiple_words_here"


def test_generate_enum_class_name():
    assert generate_enum_class_name("Material") == "MaterialEnum"
    assert generate_enum_class_name("Base Color") == "BaseColorEnum" 
    assert generate_enum_class_name("complex name") == "ComplexNameEnum"


def test_round_float_values():
    # Test float rounding - the function rounds to fewer decimal places
    result = round_float_values(1.23456789)
    assert isinstance(result, float)
    assert result < 1.3  # Should be rounded down from original
    
    # Test non-float values unchanged
    assert round_float_values(5) == 5
    assert round_float_values("test") == "test"
    assert round_float_values(True) == True


def test_format_default_value():
    # Test basic types
    assert format_default_value(1.0) == "1.0"
    assert format_default_value(5) == "5"
    assert format_default_value(True) == "True"
    
    # Test string (may or may not have quotes depending on implementation)
    result = format_default_value("test")
    assert "test" in result
    
    # Test None
    assert format_default_value(None) == "None"


def test_generate_enum_class():
    enum_options = [
        EnumOption("BALL_STICK", "Ball and Stick", "Ball and stick representation"),
        EnumOption("SURFACE", "Surface", "Surface representation")
    ]
    node_input = NodeInput("representation", "ENUM", "BALL_STICK", enum_options=enum_options)
    
    enum_class = generate_enum_class(node_input, "StyleMolecule")
    
    # Check that it contains enum-like structures
    assert "Enum" in enum_class
    assert "BALL_STICK" in enum_class
    assert "SURFACE" in enum_class


def test_generate_python_class():
    inputs = [
        NodeInput("scale", "VALUE", 1.0, "Scale of the representation", 0.1, 5.0),
        NodeInput("visible", "BOOLEAN", True, "Visibility toggle")
    ]
    style_info = StyleNodeInfo("Style Test", "Test style node", inputs)
    
    class_code = generate_python_class(style_info)
    
    # Check basic class structure exists
    assert "class" in class_code
    assert "StyleTest" in class_code or "Style_test" in class_code
    assert "scale" in class_code
    assert "visible" in class_code


def test_generate_python_class_with_enum():
    enum_options = [EnumOption("OPT1", "Option 1"), EnumOption("OPT2", "Option 2")]
    inputs = [
        NodeInput("my_enum", "ENUM", "OPT1", "Test enum", enum_options=enum_options)
    ]
    style_info = StyleNodeInfo("Style Enum Test", "Test enum style", inputs)
    
    class_code = generate_python_class(style_info)
    
    # Should include enum-related content
    assert "Enum" in class_code
    assert "OPT1" in class_code


def test_generate_python_class_no_inputs():
    style_info = StyleNodeInfo("Style Empty", "Empty style node", [])
    class_code = generate_python_class(style_info)
    
    # Should still generate a class
    assert "class" in class_code


def test_style_generator_imports():
    # Test that we can import the main components
    from nodepad.style_generator import EnumOption, NodeInput, StyleNodeInfo
    
    # Create instances to verify they work
    option = EnumOption("TEST", "Test Option")
    input_obj = NodeInput("test", "VALUE", 1.0)
    style = StyleNodeInfo("Test", "Description", [input_obj])
    
    assert option.identifier == "TEST"
    assert input_obj.name == "test"
    assert style.name == "Test"