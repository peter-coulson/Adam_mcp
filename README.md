# adam-mcp

FreeCAD MCP Server - A Model Context Protocol server for programmatic CAD operations using FreeCAD.

## Project Status

**Setup Complete** - Ready for MCP server implementation

## Features (Planned)

- Full FreeCAD Python API integration
- MCP server for AI-driven CAD operations
- Export to multiple formats (STEP, STL, OBJ, etc.)
- Pydantic models for type-safe CAD operations

## Installation

### 1. Install FreeCAD

**macOS:**
```bash
brew install freecad
```

**Linux:**
```bash
sudo apt-get install freecad  # Ubuntu/Debian
# or equivalent for your distribution
```

### 2. Clone and Setup Python Environment

```bash
git clone <your-repo-url>
cd adam_mcp
uv sync
```

### 3. Activate Virtual Environment

```bash
source .venv/bin/activate
```

## How It Works

The project uses an **explicit environment configuration** approach:

- **freecad_env.py**: Explicit setup script that configures FreeCAD paths
- Clean, visible configuration (no hidden site-packages modifications)
- Call `setup_freecad_environment()` before importing FreeCAD

## Testing the Setup

Run the environment setup script to verify FreeCAD integration:

```bash
source .venv/bin/activate
python freecad_env.py
```

You should see:
```
✓ FreeCAD environment configured
✓ FreeCAD imported successfully
✓ Created test box
✓ Setup test passed!
```

## Viewing CAD Files

### FreeCAD GUI (Recommended)
```bash
open -a FreeCAD output.FCStd
# or
open -a FreeCAD output.step
```

The FreeCAD GUI provides full interactive viewing:
- Rotate, pan, zoom
- Click on faces, edges, vertices
- Measure distances and angles
- Inspect properties

## Project Structure

```
adam_mcp/
├── src/
│   └── adam_mcp/
│       └── __init__.py         # Main package
├── .venv/                      # UV virtual environment
├── freecad_env.py              # Explicit FreeCAD environment setup
├── .env                        # Environment variables
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Dependencies

- **FreeCAD 1.0.2** (installed via Homebrew) - CAD kernel
- **fastmcp >= 1.0.0** - MCP server framework
- **pydantic >= 2.0.0** - JSON validation and data models
- **python-dotenv >= 1.0.0** - Environment variable management
