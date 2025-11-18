# adam-mcp

FreeCAD MCP Server - A Model Context Protocol server for programmatic CAD operations using FreeCAD.

## Project Status

**MCP Server Foundation Complete** - Ready for CAD tool implementation

## Features

**Implemented:**
- ✓ FreeCAD Python API integration
- ✓ FastMCP server with type-safe operations
- ✓ Document management (create, query)
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

### Custom FreeCAD Installation

If FreeCAD is installed in a non-standard location, set the `FREECAD_PATH` environment variable:

```bash
export FREECAD_PATH="/path/to/your/freecad/installation"
# Then run your script
python freecad_env.py
```

Or add it to your `.env` file:
```
FREECAD_PATH=/path/to/your/freecad/installation
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
      "args": ["run", "fastmcp", "run", "src/adam_mcp/server.py"],
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
- `health_check` - Verify server and FreeCAD integration status
- `create_document` - Create or reuse a FreeCAD document
- `get_document_info` - Query active document details

### Manual Server Start

To run the server manually for testing (FastMCP CLI - gold standard):

```bash
PYTHONPATH=src uv run fastmcp run src/adam_mcp/server.py
```

For development with debug logging and MCP Inspector:

```bash
PYTHONPATH=src uv run fastmcp dev src/adam_mcp/server.py
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

## Development

### Prerequisites

- **UV** - Fast Python package manager (`pip install uv` or `brew install uv`)
- **direnv** - Auto-activation of virtual environment (installed automatically during setup)

### Development Workflow

1. **Auto-activation**: The virtual environment activates automatically when entering the project directory
   - Powered by `direnv` + `.envrc` configuration
   - No need to run `source .venv/bin/activate`

2. **Dependency management**: Use UV for all package operations
   ```bash
   uv sync              # Sync dependencies from uv.lock
   uv sync --extra dev  # Include dev dependencies (linters, formatters)
   uv pip install pkg   # Add a new package
   ```

3. **Code quality**: Pre-commit hooks run automatically on `git commit`
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
