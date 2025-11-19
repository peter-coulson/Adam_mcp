# Working File Workflow

User experience and workflow architecture for adam-mcp's file management system.

---

## User Mental Model

When working on CAD designs through adam-mcp, users interact with two files:

1. **Main file** (`design.FCStd`) - Stable, committed design (git-tracked)
2. **Working file** (`design_work.FCStd`) - Experimental workspace (auto-saved, git-ignored)

**Core principle:** Working file is the sandbox. Main file is the source of truth. User decides when sandbox → truth.

---

## Workflow Pattern

```
open_document → edit (auto-save) → commit → [git commit main file]
                  ↓
              rollback (if needed)
```

**Resume by default:** Opening always continues from existing work file (never overwrites uncommitted changes)
**Explicit commit:** User must explicitly commit changes (validates geometry first)
**Explicit rollback:** Only way to discard uncommitted work and reset from main file

---

## Key Architectural Decisions

### Two-File System (Main + Work)

**Decision:** Main file modified only on explicit commit. Working file auto-saved for crash protection.

**Rationale:** User control, crash/corruption safety, familiar git-like mental model (work = staged, main = committed)

**Alternatives considered:** Timestamped checkpoints (too complex, users have git), unlimited version history (overkill for session), auto-commit (users lose control), SQL transactions (doesn't fit CAD workflow)

---

### Resume by Default

**Decision:** `open_document()` and `create_document()` NEVER overwrite existing work files. Always resume from existing work.

**Rationale:** Preserve uncommitted changes, safe to call open multiple times, supports multiple sessions, deliberate discard via rollback

**Alternatives considered:** Always overwrite (dangerous, loses work), prompt on conflict (interrupts workflow), timestamped backups (too complex)

---

### Explicit Commit with Validation

**Decision:** User must call `commit_changes()`. System validates geometry before committing. Rejects commit if invalid.

**Rationale:** Never corrupt main file, fail-fast validation, intentional workflow, recoverable (fix or rollback)

**Validation checks:**
1. Document recomputes successfully
2. All objects valid (no broken references)
3. All shapes geometrically valid
4. Document not empty

**Alternatives considered:** No validation (unacceptable, corruption risk), auto-commit on close (might commit broken state), warn but allow (defeats purpose)

---

### Auto-Save Every 5 Operations

**Decision:** Working file auto-saves after every 5 operations (transparent to user).

**Rationale:** Crash protection (max 4 ops lost), performance balance, operation-based (won't save mid-operation)

**Configurable:** `AUTO_SAVE_INTERVAL = 5` in constants.py

**Alternatives considered:** Every operation (too slow), time-based (unpredictable, race conditions), manual only (users forget, crash risk)

---

### Work File Location: Same Directory as Main File

**Decision:** `design_work.FCStd` sits next to `design.FCStd` by default.

**Rationale:** Simplicity (no config), visibility, natural cleanup, git-friendly (`*_work.FCStd`), portability

**Configuration Override:**

For advanced users, override default location via environment variable:

```bash
# Use custom directory for all working files
export ADAM_MCP_WORK_DIR="/Users/peter/cad_workspace"
# Results in: /Users/peter/cad_workspace/design_work.FCStd

# Use system temp directory
export ADAM_MCP_WORK_DIR="temp"
# Results in: /tmp/adam_mcp_work/design_work.FCStd
```

**Use cases for override:**
- Centralized working directory for multiple projects
- Separate disk/partition for working files (e.g., SSD for performance)
- Network mount for shared workspace (multi-machine workflows)

**Alternatives considered:** Hidden folder (less visible, harder troubleshooting), system temp (unexpected cleanup), home directory (naming conflicts, messy)

---

### Open in FreeCAD GUI

**Decision:** `open_in_freecad_gui()` launches FreeCAD desktop app with work file for live preview.

**Rationale:** Visual feedback, side-by-side workflow (terminal + GUI), real-time iteration, standard CAD workflow

**Note:** Manual reload required (FreeCAD doesn't support auto-reload, would need custom plugin)

**Alternatives considered:** Export to viewer format (loses features, conversion overhead), embedded 3D viewer (reinventing GUI, high maintenance), auto-reload (requires plugin, unreliable)

---

### User Manages Long-Term Versioning

**Decision:** adam-mcp manages active session (main + work files). User manages long-term history (git).

**Rationale:** Don't reinvent version control, focus on session safety (minutes-hours), user has git/VCS for long-term (days-years)

**Clear boundary:**
- adam-mcp: Protects active work session (minutes to hours)
- User's git/VCS: Protects long-term history (days to years)

---

## Implementation Notes

**Security:** Platform-specific file opening (no shell injection risk)
- macOS: `subprocess.Popen(["open", "-a", "FreeCAD", path])`
- Linux: `subprocess.Popen(["freecad", path])`
- Windows: `os.startfile(path)`

**File management:** See `src/adam_mcp/working_files.py` for implementation

**Constants:** All workflow constants in `src/adam_mcp/constants.py`
- `AUTO_SAVE_INTERVAL = 5`
- `WORK_FILE_SUFFIX = "_work"`
- `VALIDATE_BEFORE_COMMIT = True`

---

## Git Integration

**Recommended .gitignore:**
```gitignore
*_work.FCStd
```

**Workflow:**
1. User works through adam-mcp (edits work file)
2. User commits changes (validates, updates main file)
3. User git commits main file
4. Work file ignored by git (ephemeral workspace)

---

**Last Updated:** 2025-11-18
