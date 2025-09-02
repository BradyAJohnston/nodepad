#!/usr/bin/env python3
"""
Style Node Documentation Generator Script

This script generates documentation for Blender node groups, particularly Style nodes.
It can generate both JSON data files and Python class files.

This script will:
1. Load a specified Blender file
2. Extract information from node groups with a specified prefix
3. Generate either JSON data or Python class files (or both)

Originally from MolecularNodes, moved to nodepad for broader use.
"""

import click
import warnings
from pathlib import Path
from io import StringIO
import sys

from .style_generator import (
    extract_style_nodes,
    generate_style_classes_file,
    save_style_data_to_json,
)


class WarningCapture:
    """Context manager to capture warnings, with selective stdout/stderr capture for operations."""

    def __init__(self):
        self.warnings = []
        self.captured_output = []
        self.original_showwarning = None

    def __enter__(self):
        # Only capture Python warnings initially
        self.original_showwarning = warnings.showwarning
        warnings.showwarning = self._capture_warning
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        warnings.showwarning = self.original_showwarning

    def _capture_warning(
        self, message, category, filename, lineno, file=None, line=None
    ):
        self.warnings.append(
            {
                "message": str(message),
                "category": category.__name__,
                "filename": filename,
                "lineno": lineno,
                "type": "python_warning",
            }
        )

    def capture_operation_output(self, operation_func, *args, **kwargs):
        """Capture stdout/stderr during a specific operation and return any result."""
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()

        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture

            # Run the operation
            result = operation_func(*args, **kwargs)

            # Process captured output
            self._process_captured_streams(stdout_capture, stderr_capture)

            return result

        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def _process_captured_streams(self, stdout_capture, stderr_capture):
        """Process captured stdout/stderr for warnings and informational messages."""
        stdout_content = stdout_capture.getvalue()
        stderr_content = stderr_capture.getvalue()

        # Process stdout
        for line in stdout_content.split("\n"):
            line = line.strip()
            if line:
                if "warning" in line.lower() or "warn" in line.lower():
                    self.warnings.append(
                        {
                            "message": line,
                            "category": "BlenderWarning",
                            "filename": None,
                            "lineno": None,
                            "type": "blender_warning",
                        }
                    )
                else:
                    # Non-warning output (like "Read blend:", "Generated X classes")
                    self.captured_output.append(("info", line))

        # Process stderr
        for line in stderr_content.split("\n"):
            line = line.strip()
            if line:
                self.warnings.append(
                    {
                        "message": line,
                        "category": "BlenderError",
                        "filename": None,
                        "lineno": None,
                        "type": "blender_error",
                    }
                )

    def echo_info_messages(self):
        """Echo captured informational messages immediately and clear them."""
        for msg_type, message in self.captured_output:
            if msg_type == "info":
                click.echo(f"   {click.style(message, fg='bright_black')}")
        # Clear the captured output so it doesn't repeat
        self.captured_output.clear()

    def report_warnings(self):
        """Report all captured warnings with nice formatting."""
        if not self.warnings:
            return

        click.echo()
        click.echo(click.style("⚠️  Warnings encountered:", fg="yellow", bold=True))

        for warning in self.warnings:
            if warning["type"] == "python_warning":
                click.echo(
                    f"  • {click.style(warning['category'], fg='yellow')}: {warning['message']}"
                )
                if warning["filename"] and warning["lineno"]:
                    click.echo(
                        f"    {click.style('Location:', fg='bright_black')} {warning['filename']}:{warning['lineno']}"
                    )
            else:
                # Blender warnings/errors
                click.echo(
                    f"  • {click.style(warning['category'], fg='yellow')}: {warning['message']}"
                )

        click.echo()


@click.command()
@click.option("--json", "generate_json", is_flag=True, help="Generate JSON data file")
@click.option(
    "--python", "generate_python", is_flag=True, help="Generate Python class file"
)
@click.option(
    "--output-dir",
    type=click.Path(exists=False, path_type=Path),
    default=".",
    help="Output directory",
    show_default=True,
)
@click.option(
    "--blend-file",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the Blender file to extract from",
)
@click.option(
    "--prefix",
    default="Style ",
    help="Node name prefix to filter by",
    show_default=True,
)
@click.option(
    "--list-nodes",
    is_flag=True,
    help="Just list available nodes with the specified prefix",
)
def main(generate_json, generate_python, output_dir, blend_file, prefix, list_nodes):
    """Generate documentation for Blender node groups."""

    # Default to both if neither specified
    if not generate_json and not generate_python and not list_nodes:
        generate_json = True
        generate_python = True

    output_dir.mkdir(exist_ok=True)

    with WarningCapture() as warning_capture:
        try:
            if list_nodes:
                click.echo(
                    click.style(
                        f"🔍 Extracting nodes with prefix '{prefix}' from:", fg="blue"
                    )
                )
                click.echo(f"   {blend_file}")

                style_nodes = warning_capture.capture_operation_output(
                    extract_style_nodes, blend_file, prefix
                )
                warning_capture.echo_info_messages()

                if style_nodes:
                    click.echo(
                        click.style(
                            f"\n✅ Found {len(style_nodes)} nodes:",
                            fg="green",
                            bold=True,
                        )
                    )
                    for name, info in style_nodes.items():
                        click.echo(
                            f"  • {click.style(name, fg='cyan')} ({len(info.inputs)} inputs)"
                        )
                        if info.description:
                            click.echo(
                                f"    {click.style('Description:', fg='yellow')} {info.description}"
                            )
                else:
                    click.echo(
                        click.style(
                            f"\n⚠️  No nodes found with prefix '{prefix}'", fg="yellow"
                        )
                    )

                # Report warnings at the end
                warning_capture.report_warnings()
                return

            click.echo(
                click.style(
                    "🚀 Starting documentation generation...", fg="blue", bold=True
                )
            )
            click.echo(f"   Source: {blend_file}")
            click.echo(f"   Output: {output_dir}")
            click.echo(f"   Prefix: {prefix}")
            click.echo()

            if generate_json:
                json_path = (
                    output_dir
                    / f"{prefix.strip().lower().replace(' ', '_')}_nodes_data.json"
                )
                click.echo(click.style("📄 Generating JSON data...", fg="blue"))
                warning_capture.capture_operation_output(
                    save_style_data_to_json, json_path, blend_file, prefix
                )
                warning_capture.echo_info_messages()
                click.echo(
                    f"   ✅ JSON saved to: {click.style(str(json_path), fg='green')}"
                )

            if generate_python:
                py_path = output_dir / "styles.py"
                click.echo()
                click.echo(click.style("🐍 Generating Python classes...", fg="blue"))
                warning_capture.capture_operation_output(
                    generate_style_classes_file, py_path, blend_file, prefix
                )
                warning_capture.echo_info_messages()
                click.echo(
                    f"   ✅ Python classes saved to: {click.style(str(py_path), fg='green')}"
                )

            click.echo()
            click.echo(click.style("🎉 Generation complete!", fg="green", bold=True))

            # Report warnings at the end after success message
            warning_capture.report_warnings()

        except Exception as e:
            click.echo()
            click.echo(click.style("❌ Error occurred:", fg="red", bold=True), err=True)
            click.echo(click.style(f"   {e}", fg="red"), err=True)

            # Report warnings even when there's an error
            warning_capture.report_warnings()
            raise click.Abort()


if __name__ == "__main__":
    main()
