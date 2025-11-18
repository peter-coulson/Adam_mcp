#!/usr/bin/env python3
"""
Test script for CAD operation tools.

Tests list_objects and get_object_details on sample FreeCAD files.
"""

from pathlib import Path

# Setup FreeCAD environment first
from adam_mcp.freecad_env import setup_freecad_environment

setup_freecad_environment()

# Now import tools (must be after setup_freecad_environment)
from adam_mcp.tools.cad_operations import (  # noqa: E402
    get_object_details,
    list_objects,
)
from adam_mcp.tools.document import open_document  # noqa: E402


def test_file(file_path: str) -> None:
    """Test CAD tools on a specific file."""
    print(f"\n{'='*80}")
    print(f"Testing: {Path(file_path).name}")
    print(f"{'='*80}\n")

    # Open the document
    print("Opening document...")
    doc_info = open_document(file_path)
    print(f"✓ Opened: {doc_info.name}")
    print(f"  Object count: {doc_info.object_count}")
    print(f"  Objects: {doc_info.objects}\n")

    # Test list_objects
    print("Testing list_objects()...")
    obj_list = list_objects()
    print(f"✓ Found {obj_list.count} objects:\n")

    for obj in obj_list.objects:
        print(f"  - {obj.name} ({obj.type})")
        print(f"    Label: {obj.label}")
        if obj.depends_on:
            print(f"    Depends on: {obj.depends_on}")
        print()

    # Test get_object_details on first 3 objects (or all if less than 3)
    if obj_list.count > 0:
        test_names = [obj.name for obj in obj_list.objects[:3]]
        print(f"\nTesting get_object_details({test_names})...")

        details = get_object_details(test_names)
        print(f"✓ Retrieved details for {len(details.objects)} objects:\n")

        for obj_detail in details.objects:
            print(f"  {obj_detail.name} ({obj_detail.type}):")
            print(f"    Label: {obj_detail.label}")
            print(f"    Properties: {len(obj_detail.properties)}")
            print(f"    Depends on: {obj_detail.depends_on}")
            print(f"    Depended by: {obj_detail.depended_by}")

            # Show first few properties
            print("    Key properties:")
            for prop in obj_detail.properties[:5]:
                print(f"      - {prop.name}: {prop.value} ({prop.type})")
            if len(obj_detail.properties) > 5:
                print(f"      ... and {len(obj_detail.properties) - 5} more")
            print()

        if details.not_found:
            print(f"  Not found: {details.not_found}\n")


def main() -> None:
    """Run tests on all sample files."""
    samples_dir = Path.home() / "freecad_projects" / "test_samples"

    if not samples_dir.exists():
        print(f"Error: Sample directory not found: {samples_dir}")
        return

    # Find all .FCStd files
    fcstd_files = list(samples_dir.glob("*.FCStd"))

    if not fcstd_files:
        print(f"Error: No .FCStd files found in {samples_dir}")
        return

    print(f"Found {len(fcstd_files)} test files:")
    for f in fcstd_files:
        print(f"  - {f.name}")

    # Test each file
    for file_path in fcstd_files:
        try:
            test_file(str(file_path))
        except Exception as e:
            print(f"\n❌ Error testing {file_path.name}: {e}\n")


if __name__ == "__main__":
    main()
