# adam-mcp

FreeCAD MCP Server - A Model Context Protocol server for programmatic CAD operations using FreeCAD.

## Project Status

**MCP Server Foundation Complete** - Ready for CAD tool implementation

## Features

**Implemented:**
- ✓ FreeCAD Python API integration
- ✓ FastMCP server with type-safe operations
- ✓ Document management (create, open, commit, rollback)
- ✓ Default projects directory with environment variable configuration
- ✓ Project listing and discovery
- ✓ Working file system with auto-save
- ✓ Health monitoring

**Planned:**
- Sketch creation and geometry tools
- Extrude operations
- Fillet operations
- Export to multiple formats (STEP, STL, OBJ, etc.)

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

By default, projects are saved to `~/freecad_projects`. You can customize this:

```bash
export ADAM_MCP_DEFAULT_DIR="~/my_cad_projects"
```

For development, the `.envrc` file automatically sets this to `./dev_projects` when you're in the project directory.

Add these to your `.env` file to make them permanent:
```
FREECAD_PATH=/path/to/your/freecad/installation
ADAM_MCP_DEFAULT_DIR=~/my_cad_projects
```

## Testing the Setup

Run the environment setup script to verify FreeCAD integration:

```bash
python freecad_env.py
# or with UV
uv run python freecad_env.py
```

You should see:
```
✓ FreeCAD environment configured
✓ FreeCAD imported successfully
✓ Created test box
✓ Setup test passed!
```

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
- `health_check_tool` - Verify server and FreeCAD integration status
- `create_document_tool` - Create a new FreeCAD document (or resume existing working file)
- `open_document_tool` - Open an existing FreeCAD document for editing
- `get_document_info_tool` - Query active document details (object count, names)
- `commit_changes_tool` - Save working file changes to main file (validates before commit)
- `rollback_working_changes_tool` - Discard uncommitted changes and reset from main file
- `list_projects_tool` - List all FreeCAD projects in a directory (defaults to projects directory)
- `open_in_freecad_gui_tool` - Open the working file in FreeCAD desktop application for live preview

**Document Management Workflow:**

The server uses a **working file system** for safe editing:

1. **Create or open** a document - creates both main file (`.FCStd`) and working file (`.FCStd.work`)
2. **Edit** the document - all changes go to the working file, auto-saved every 5 operations
3. **Commit** changes - validates and saves working file to main file (only way main file is updated)
4. **Rollback** if needed - discard working file changes and reset from main file

**Path Resolution:**

All document paths support flexible formats:
- **Filename only**: `"bracket.FCStd"` → resolves to `~/freecad_projects/bracket.FCStd`
- **Relative path**: `"designs/bracket.FCStd"` → resolves to `~/freecad_projects/designs/bracket.FCStd`
- **Absolute path**: `"~/custom/bracket.FCStd"` → uses exact path specified

This makes it easy to work with projects without typing full paths every time.

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
│       │   ├── query.py         # Query tools (list/details)
│       │   ├── discovery.py     # List available operations
│       │   └── execution.py     # Execute operations
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
   # Create test files - they stay local and don't pollute ~/freecad_projects
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
mypy src/ freecad_env.py  # Type check
```

### Configuration Files

- **pyproject.toml** - All tool configurations (black, ruff, mypy, bandit)
- **.pre-commit-config.yaml** - Pre-commit hook definitions
- **uv.lock** - Lockfile for reproducible builds (committed to git)
- **.python-version** - Python version for this project (3.11)
- **.envrc** - Direnv configuration for auto-activation

### Quality Standards

Per `CLAUDE.md`, all code must follow:
- ✓ Type hints on all functions
- ✓ No magic numbers or duplicate strings
- ✓ DRY principle - extract constants/config
- ✓ Error messages explain what went wrong AND how to fix it
- ✓ Simplicity over cleverness
