"""
FreeCAD Environment Setup
Configure Python path and environment for FreeCAD integration
"""

import sys
import os

# FreeCAD paths
FREECAD_LIB = "/Applications/FreeCAD.app/Contents/Resources/lib"
FREECAD_MOD = "/Applications/FreeCAD.app/Contents/Resources/Mod"
FREECAD_EXT = "/Applications/FreeCAD.app/Contents/Resources/Ext"
FREECAD_FRAMEWORKS = "/Applications/FreeCAD.app/Contents/Frameworks"

def setup_freecad_environment():
    """
    Explicitly configure Python environment for FreeCAD
    Call this before importing FreeCAD modules
    """
    # Add FreeCAD to Python path
    paths_to_add = [FREECAD_LIB, FREECAD_MOD, FREECAD_EXT]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Set environment variables for dynamic library loading
    os.environ.setdefault("DYLD_LIBRARY_PATH", FREECAD_LIB)
    os.environ.setdefault("DYLD_FRAMEWORK_PATH", FREECAD_FRAMEWORKS)

    print("✓ FreeCAD environment configured")
    print(f"  - Library path: {FREECAD_LIB}")
    print(f"  - Modules path: {FREECAD_MOD}")
    print(f"  - Extensions path: {FREECAD_EXT}")


if __name__ == "__main__":
    setup_freecad_environment()

    # Test FreeCAD import
    try:
        import FreeCAD
        import Part
        print(f"\n✓ FreeCAD imported successfully")
        print(f"  Version: {'.'.join(FreeCAD.Version()[:3])}")
        print(f"  Build: {FreeCAD.Version()[3]}")

        # Create a simple test object
        doc = FreeCAD.newDocument("Test")
        box = Part.makeBox(10, 10, 10)
        print(f"\n✓ Created test box")
        print(f"  Volume: {box.Volume}")

        FreeCAD.closeDocument("Test")
        print("\n✓ Setup test passed!")

    except ImportError as e:
        print(f"\n✗ Failed to import FreeCAD: {e}")
        sys.exit(1)
