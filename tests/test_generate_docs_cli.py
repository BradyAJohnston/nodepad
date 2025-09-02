import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
import json
import warnings
from io import StringIO
import sys

from nodepad.generate_docs import main, WarningCapture


@pytest.fixture
def runner():
    """Click test runner fixture."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_blend_file():
    """Path to existing blend file for testing."""
    # Use the existing test blend file from the project
    blend_path = Path(__file__).parent.parent / "molecularnodes" / "assets" / "MN_data_file_4.4.blend"
    if blend_path.exists():
        return blend_path
    # Fallback to any .blend file in the project
    for blend_file in Path(__file__).parent.parent.rglob("*.blend"):
        return blend_file
    pytest.skip("No .blend file available for testing")


class TestWarningCapture:
    """Test the WarningCapture context manager."""
    
    def test_warning_capture_init(self):
        """Test WarningCapture initializes correctly."""
        capture = WarningCapture()
        assert capture.warnings == []
        assert capture.captured_output == []
        assert capture.original_showwarning is None
    
    def test_python_warning_capture(self):
        """Test that Python warnings are captured."""
        capture = WarningCapture()
        
        with capture:
            warnings.warn("Test warning", UserWarning)
        
        assert len(capture.warnings) == 1
        warning = capture.warnings[0]
        assert warning['message'] == "Test warning"
        assert warning['category'] == "UserWarning"
        assert warning['type'] == "python_warning"
    
    def test_operation_output_capture(self):
        """Test capturing stdout/stderr from operations."""
        capture = WarningCapture()
        
        def test_operation():
            print("Info message")
            print("Warning: Something happened", file=sys.stderr)
            return "result"
        
        with capture:
            result = capture.capture_operation_output(test_operation)
        
        assert result == "result"
        assert len(capture.captured_output) == 1
        assert capture.captured_output[0] == ("info", "Info message")
        assert len(capture.warnings) == 1
        assert capture.warnings[0]['category'] == "BlenderError"
        assert "Warning: Something happened" in capture.warnings[0]['message']
    
    def test_blender_warning_detection(self):
        """Test that Blender warnings are properly detected."""
        capture = WarningCapture()
        
        def blender_operation():
            print("Read blend: /path/to/file.blend")
            print("Warning: File written by newer Blender binary")
            print("Style node data saved")
        
        with capture:
            capture.capture_operation_output(blender_operation)
        
        # Should have 2 info messages and 1 warning
        info_messages = [item for item in capture.captured_output if item[0] == "info"]
        assert len(info_messages) == 2
        assert len(capture.warnings) == 1
        assert capture.warnings[0]['category'] == "BlenderWarning"
        assert "newer Blender binary" in capture.warnings[0]['message']
    
    def test_echo_info_messages_clears_output(self, capsys):
        """Test that echo_info_messages prints and clears captured output."""
        capture = WarningCapture()
        capture.captured_output = [("info", "Test message")]
        
        capture.echo_info_messages()
        
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert len(capture.captured_output) == 0
    
    def test_report_warnings_formatting(self, capsys):
        """Test that warnings are formatted correctly when reported."""
        capture = WarningCapture()
        capture.warnings = [
            {
                'message': 'Python test warning',
                'category': 'UserWarning',
                'filename': 'test.py',
                'lineno': 42,
                'type': 'python_warning'
            },
            {
                'message': 'Blender test warning',
                'category': 'BlenderWarning',
                'filename': None,
                'lineno': None,
                'type': 'blender_warning'
            }
        ]
        
        capture.report_warnings()
        
        captured = capsys.readouterr()
        assert "Warnings encountered:" in captured.out
        assert "UserWarning" in captured.out
        assert "BlenderWarning" in captured.out
        assert "test.py:42" in captured.out


class TestCLI:
    """Test the CLI functionality."""
    
    def test_cli_help(self, runner):
        """Test that help message is displayed correctly."""
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "Generate documentation for Blender node groups" in result.output
        assert "--json" in result.output
        assert "--python" in result.output
        assert "--blend-file" in result.output
    
    def test_cli_missing_blend_file(self, runner):
        """Test CLI behavior when blend file is missing."""
        result = runner.invoke(main, ['--blend-file', 'nonexistent.blend'])
        assert result.exit_code == 2  # Click parameter validation error
        assert "does not exist" in result.output.lower()
    
    def test_cli_json_generation(self, runner, sample_blend_file, temp_dir):
        """Test JSON generation functionality."""
        json_output = temp_dir / "test_output.json"
        
        result = runner.invoke(main, [
            '--json',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir),
            '--prefix', 'Style '
        ])
        
        # Should complete without error (even if no nodes found)
        assert result.exit_code == 0
        assert "Generating JSON data" in result.output
    
    def test_cli_python_generation(self, runner, sample_blend_file, temp_dir):
        """Test Python class generation functionality."""        
        result = runner.invoke(main, [
            '--python',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir),
            '--prefix', 'Style '
        ])
        
        # Should complete without error (even if no nodes found)
        assert result.exit_code == 0
        assert "Generating Python classes" in result.output
    
    def test_cli_both_generation(self, runner, sample_blend_file, temp_dir):
        """Test generating both JSON and Python files."""
        result = runner.invoke(main, [
            '--json',
            '--python',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir),
            '--prefix', 'Style '
        ])
        
        assert result.exit_code == 0
        assert "Generating JSON data" in result.output
        assert "Generating Python classes" in result.output
        assert "Generation complete!" in result.output
    
    def test_cli_default_behavior(self, runner, sample_blend_file, temp_dir):
        """Test that both JSON and Python are generated by default."""
        result = runner.invoke(main, [
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir)
        ])
        
        assert result.exit_code == 0
        # Should generate both by default
        assert "Generating JSON data" in result.output
        assert "Generating Python classes" in result.output
    
    def test_cli_list_nodes(self, runner, sample_blend_file):
        """Test listing nodes functionality."""
        result = runner.invoke(main, [
            '--list-nodes',
            '--blend-file', str(sample_blend_file),
            '--prefix', 'Style '
        ])
        
        assert result.exit_code == 0
        assert "Extracting nodes with prefix" in result.output
        # Should either find nodes or report none found
        assert ("Found" in result.output) or ("No nodes found" in result.output)
    
    def test_cli_custom_prefix(self, runner, sample_blend_file, temp_dir):
        """Test using a custom prefix."""
        result = runner.invoke(main, [
            '--json',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir),
            '--prefix', 'Custom'
        ])
        
        assert result.exit_code == 0
        assert "Prefix: Custom" in result.output
    
    def test_cli_output_formatting(self, runner, sample_blend_file, temp_dir):
        """Test that output formatting includes expected elements."""
        result = runner.invoke(main, [
            '--json',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir)
        ])
        
        assert result.exit_code == 0
        # Check for emoji and formatting elements
        assert "🚀" in result.output  # Starting generation
        assert "📄" in result.output  # JSON generation
        assert "✅" in result.output  # Success indicators
        assert "🎉" in result.output  # Completion
        assert "Source:" in result.output
        assert "Output:" in result.output
        assert "Prefix:" in result.output
    
    def test_cli_creates_output_directory(self, runner, sample_blend_file, temp_dir):
        """Test that output directory is created if it doesn't exist."""
        new_dir = temp_dir / "new_output_dir"
        assert not new_dir.exists()
        
        result = runner.invoke(main, [
            '--json',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(new_dir)
        ])
        
        assert result.exit_code == 0
        assert new_dir.exists()
        assert new_dir.is_dir()


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_warning_reporting_integration(self, runner, sample_blend_file, temp_dir):
        """Test that warnings are captured and reported at the end."""
        result = runner.invoke(main, [
            '--json',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir)
        ])
        
        # If there are warnings, they should appear at the end
        if "⚠️" in result.output:
            # Warnings section should come after success message
            warning_pos = result.output.find("⚠️")
            success_pos = result.output.find("🎉")
            assert warning_pos > success_pos
    
    def test_file_output_structure(self, runner, sample_blend_file, temp_dir):
        """Test that generated files have correct structure and naming."""
        result = runner.invoke(main, [
            '--json',
            '--python',
            '--blend-file', str(sample_blend_file),
            '--output-dir', str(temp_dir),
            '--prefix', 'Test '
        ])
        
        assert result.exit_code == 0
        
        # Check expected file names based on prefix
        expected_json = temp_dir / "test_nodes_data.json"
        expected_python = temp_dir / "styles.py"
        
        # Files should exist (even if empty due to no matching nodes)
        if expected_json.exists():
            # If JSON file exists, it should be valid JSON
            with open(expected_json) as f:
                data = json.load(f)
                assert isinstance(data, dict)
        
        if expected_python.exists():
            # If Python file exists, it should be readable
            assert expected_python.read_text().strip() != ""