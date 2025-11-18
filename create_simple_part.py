#!/usr/bin/env python3
"""
Create a simple test part for testing CAD tools.
"""

from pathlib import Path

from adam_mcp.freecad_env import setup_freecad_environment

setup_freecad_environment()

import FreeCAD  # noqa: E402


def create_simple_bracket() -> None:
    """Create a simple bracket part."""
    # Create new document
    doc = FreeCAD.newDocument("SimpleBracket")

    # Create base box
    box = doc.addObject("Part::Box", "BaseBlock")
    box.Length = 50.0
    box.Width = 30.0
    box.Height = 10.0

    # Create mounting hole cylinder
    cylinder = doc.addObject("Part::Cylinder", "MountingHole")
    cylinder.Radius = 4.0
    cylinder.Height = 10.0
    cylinder.Placement.Base = FreeCAD.Vector(10, 15, 0)

    # Cut hole from box
    cut = doc.addObject("Part::Cut", "BracketWithHole")
    cut.Base = box
    cut.Tool = cylinder

    # Recompute
    doc.recompute()

    # Save file
    output_path = Path.home() / "freecad_projects" / "test_samples" / "simple_bracket.FCStd"
    doc.saveAs(str(output_path))

    print(f"✓ Created simple bracket: {output_path}")
    print(f"  Objects: {[obj.Name for obj in doc.Objects]}")


if __name__ == "__main__":
    create_simple_bracket()
