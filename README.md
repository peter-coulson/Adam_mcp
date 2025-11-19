# adam-mcp

**MCP server for creating and editing industrial CAD parts in FreeCAD.**

Built in 8 hours to demonstrate conversational CAD via Model Context Protocol.

## What It Does

Create and modify mechanical parts using natural language in Claude Code:

```
"Create a simple washer - 20mm outer diameter, 11mm hole, 3mm thick"
```

Claude will create sketches, extrude geometry, and open FreeCAD GUI for preview.

**Core capabilities:** Cylinders, sketches (circles/polygons), extrusion (pad/pocket), threads, property modification

**Example parts:** Stepped spindle shafts, washers, bolt heads with metric threads

See `PROMPTS.md` for detailed demo workflows.

## Current Operations

**7 Core CAD Operations:**
- Cylinders, sketches, circles, polygons, extrusion (pad/pocket), threads, modify properties

**17 Supporting Tools:**
- Document management, project discovery, object inspection, GUI preview

See full tool list in "Using the MCP Server" section below.

## Quick Start

After installation (see below), use Claude Code to create CAD parts with natural language:

```
# In Claude Code with adam-mcp server enabled:

"Create a simple washer - 20mm outer diameter, 11mm hole, 3mm thick"
```

Claude will:
1. Open FreeCAD GUI for preview
2. Create a sketch with two circles (outer and hole)
3. Extrude the sketch to create the 3D washer
4. Open the result in FreeCAD GUI for verification
5. Prompt you to commit the changes

See `PROMPTS.md` for detailed demo examples including:
- Creating complex multi-part assemblies (stepped spindle shafts)
- Modifying existing projects (bolt heads, threads)
- Project discovery and inspection workflows

## Installation

### 1. Install FreeCAD

**macOS:**
```bash
brew install freecad
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install freecad
```

**Linux (Fedora):**
```bash
sudo dnf install freecad
```

**Windows:**
Download from [https://www.freecad.org/downloads.php](https://www.freecad.org/downloads.php)

### 2. Clone and Setup Python Environment

```bash
git clone <your-repo-url>
cd adam_mcp
uv sync --extra dev  # Installs both runtime and dev dependencies
```

The virtual environment will automatically activate when you enter the directory (via direnv).

## How It Works

The project uses an **explicit environment configuration** approach:

- **freecad_env.py**: Platform-aware setup script that configures FreeCAD paths
- Automatically detects macOS, Linux, and Windows
- Clean, visible configuration (no hidden site-packages modifications)
- Call `setup_freecad_environment()` before importing FreeCAD

### Environment Variables

**Custom FreeCAD Installation:**

If FreeCAD is installed in a non-standard location, set the `FREECAD_PATH` environment variable:

```bash
export FREECAD_PATH="/path/to/your/freecad/installation"
```

**Default Projects Directory:**

By default, projects are saved to `~/Documents/Projects/adam_mcp/dev_projects`. You can customize this:

```bash
export ADAM_MCP_DEFAULT_DIR="~/my_cad_projects"
```

For development, the `.envrc` file automatically sets this to `./dev_projects` (relative to project root) when you're in the project directory.

Add these to your `.env` file to make them permanent:
```
FREECAD_PATH=/path/to/your/freecad/installation
ADAM_MCP_DEFAULT_DIR=~/my_cad_projects
```

## Testing the Setup

You can verify FreeCAD integration by starting the MCP server and using the health check tool:

```bash
# Start the server in dev mode
PYTHONPATH=src uv run fastmcp dev src/adam_mcp/core/server.py
```

Then use the `health_check_tool` via your MCP client (e.g., Claude Code) to verify the server is running and FreeCAD is properly integrated.

## Using the MCP Server

### Project-Scoped Configuration

The MCP server is configured for this project via `.mcp.json`:

```json
{
  "mcpServers": {
    "adam-mcp": {
      "command": "uv",
      "args": ["run", "fastmcp", "run", "src/adam_mcp/core/server.py"],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

This configuration:
- ✓ Uses FastMCP CLI (gold standard)
- ✓ Sets PYTHONPATH via env (best practice for src layout)
- ✓ No wrapper scripts needed
- ✓ Checked into version control for team sharing

**Available Tools:**

*Document Management:*
- `health_check_tool` - Verify server and FreeCAD integration status
- `create_document_tool` - Create a new FreeCAD document (or resume existing working file)
- `open_document_tool` - Open an existing FreeCAD document for editing
- `get_document_info_tool` - Query active document details (object count, names)
- `commit_changes_tool` - Save working file changes to main file (validates before commit)
- `rollback_working_changes_tool` - Discard uncommitted changes and reset from main file
- `list_projects_tool` - List all FreeCAD projects in a directory (defaults to projects directory)
- `open_in_freecad_gui_tool` - Open the working file in FreeCAD desktop application for live preview

*Object Inspection:*
- `list_objects_tool` - List all objects in active document (lightweight overview)
- `get_object_details_tool` - Get detailed properties for specific objects

*CAD Operations:*
- `create_cylinder_tool` - Create cylindrical primitive with position and angle control
- `create_sketch_tool` - Create 2D sketch on specified plane (XY, XZ, or YZ)
- `add_sketch_circle_tool` - Add circle to existing sketch
- `add_sketch_polygon_tool` - Add regular polygon to existing sketch (3-12 sides)
- `create_pad_tool` - Extrude sketch into 3D solid (PartDesign Pad)
- `create_pocket_tool` - Cut material from solid using sketch profile (PartDesign Pocket)
- `create_thread_tool` - Add ISO metric threads to cylindrical surface (M3-M30)
- `modify_object_tool` - Modify properties of existing objects (resize, reposition, etc.)

**Document Management Workflow:**

The server uses a **working file system** for safe editing:

1. **Create or open** a document - creates both main file (`.FCStd`) and working file (`_work.FCStd`)
2. **Edit** the document - all changes go to the working file, auto-saved every 5 operations
3. **Commit** changes - validates and saves working file to main file (only way main file is updated)
4. **Rollback** if needed - discard working file changes and reset from main file

**Path Resolution:**

For security, all document paths must be relative (within the configured projects directory):
- **Filename only**: `"bracket.FCStd"` → saved to `{DEFAULT_PROJECTS_DIR}/bracket.FCStd`
- **Subdirectory**: `"designs/bracket.FCStd"` → saved to `{DEFAULT_PROJECTS_DIR}/designs/bracket.FCStd`
- **Nested paths**: `"fasteners/m10/bolt.FCStd"` → saved to `{DEFAULT_PROJECTS_DIR}/fasteners/m10/bolt.FCStd`

Absolute paths (~/path or /path) are rejected for security. All files stay within the configured projects directory.

### Manual Server Start

To run the server manually for testing (FastMCP CLI - gold standard):

```bash
PYTHONPATH=src uv run fastmcp run src/adam_mcp/core/server.py
```

For development with debug logging and MCP Inspector:

```bash
PYTHONPATH=src uv run fastmcp dev src/adam_mcp/core/server.py
```

The `PYTHONPATH=src` ensures the package can be imported correctly with the src layout.

### Claude Code Integration

When you open this project in Claude Code, it will automatically detect the `.mcp.json` configuration and prompt you to approve the MCP server. Once approved, Claude can use the CAD tools directly.

To reset project MCP approvals:
```bash
claude mcp reset-project-choices
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
│       ├── __init__.py          # Package metadata
│       ├── core/                # Infrastructure
│       │   ├── server.py        # FastMCP server entry point
│       │   ├── freecad_env.py   # FreeCAD environment setup
│       │   └── working_files.py # Working file infrastructure
│       ├── constants/            # Configuration organized by domain
│       │   ├── dimensions.py    # Dimension constraints
│       │   ├── messages.py      # Error/success messages
│       │   ├── paths.py         # File paths
│       │   └── operations.py    # Operation categories
│       ├── models/              # Pydantic models for type safety
│       │   ├── base.py          # Base operation models
│       │   ├── responses.py     # Response models
│       │   └── operations/      # Operation models by category
│       ├── operations/          # Business logic (handlers, validators)
│       ├── tools/               # MCP tools
│       │   ├── document.py      # Document management
│       │   └── query.py         # Query tools (list/details)
│       └── utils/               # Helper functions
│           ├── errors.py        # Error formatting
│           ├── validation.py    # Validation utilities
│           ├── paths.py         # Path utilities
│           └── freecad.py       # FreeCAD utilities
├── dev_projects/                # Local development CAD files (gitignored)
├── .venv/                       # UV virtual environment
├── .envrc                       # Direnv config (auto-activation + dev settings)
├── .env                         # Environment variables (optional)
├── .mcp.json                    # MCP server configuration
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## Dependencies

- **FreeCAD 1.0.2** (installed via Homebrew) - CAD kernel
- **fastmcp >= 1.0.0** - MCP server framework
- **pydantic >= 2.0.0** - JSON validation and data models
- **python-dotenv >= 1.0.0** - Environment variable management

## Development

### Prerequisites

- **UV** - Fast Python package manager (`pip install uv` or `brew install uv`)
- **direnv** - Auto-activation of virtual environment (installed automatically during setup)

### Development Workflow

1. **Auto-activation**: The virtual environment activates automatically when entering the project directory
   - Powered by `direnv` + `.envrc` configuration
   - No need to run `source .venv/bin/activate`
   - Auto-sets `ADAM_MCP_DEFAULT_DIR=./dev_projects` for local testing

2. **Local testing**: All test projects go to `./dev_projects/` (gitignored)
   ```bash
   # Create test files - they stay local in dev_projects
   create_document("test_bracket.FCStd")  # → ./dev_projects/test_bracket.FCStd
   list_projects()                         # → lists files in ./dev_projects/

   # Clean up test files easily
   rm -rf dev_projects/*.FCStd
   ```

3. **Dependency management**: Use UV for all package operations
   ```bash
   uv sync              # Sync dependencies from uv.lock
   uv sync --extra dev  # Include dev dependencies (linters, formatters)
   uv pip install pkg   # Add a new package
   ```

4. **Code quality**: Pre-commit hooks run automatically on `git commit`
   ```bash
   pre-commit run --all-files  # Run manually on all files
   ```

### Code Quality Tools

**Configured and enforced via pre-commit hooks:**

- **ruff** - Fast linting (replaces flake8, isort, pyupgrade)
  - Checks: pycodestyle, pyflakes, naming, bugbear, simplify, etc.
  - Auto-fixes many issues

- **black** - Code formatting (100 char lines)

- **mypy** - Static type checking (strict mode)
  - All functions must have type hints
  - Configured in `pyproject.toml` with strict settings

- **bandit** - Security vulnerability scanning

**Run tools manually:**
```bash
ruff check .          # Lint code
ruff check --fix .    # Lint and auto-fix
black .               # Format code
mypy src/             # Type check
```

### Configuration Files

- **pyproject.toml** - All tool configurations (black, ruff, mypy, bandit)
- **.pre-commit-config.yaml** - Pre-commit hook definitions
- **uv.lock** - Lockfile for reproducible builds (committed to git)
- **.python-version** - Python version for this project (3.11)
- **.envrc** - Direnv configuration for auto-activation

### Development Standards

See `CLAUDE_DEV.md` for comprehensive development principles, architecture decisions, and quality standards.

Key principles:
- ✓ Type hints on all functions (strict mypy)
- ✓ No magic numbers or duplicate strings (all constants in `constants/`)
- ✓ DRY principle - extract constants/config
- ✓ Error messages explain what went wrong AND how to fix it
- ✓ Simplicity over cleverness
- ✓ 3-layer validation: Pydantic → Semantic → Geometry

For AI-assisted development with Claude Code, the project includes:
- **CLAUDE.md** - User-facing workflow and commit policy (system prompt for CAD operations)
- **CLAUDE_DEV.md** - Developer-focused principles and architecture guidance
