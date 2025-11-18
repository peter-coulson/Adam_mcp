# Working File Workflow

User experience and workflow architecture for adam-mcp's file management system.

---

## User Mental Model

When working on CAD designs through adam-mcp, users interact with two files:

1. **Main file** (`design.FCStd`) - Stable, committed design (git-tracked)
2. **Working file** (`design.FCStd.work`) - Experimental workspace (auto-saved, git-ignored)

**Core principle:** Working file is the sandbox. Main file is the source of truth. User decides when sandbox → truth.

---

## Workflow Pattern

```
open_document → edit (auto-save) → commit → [git commit main file]
                  ↓
              rollback (if needed)
```

**Resume by default:** Opening always continues from existing .work file (never overwrites uncommitted changes)
**Explicit commit:** User must explicitly commit changes (validates geometry first)
**Explicit rollback:** Only way to discard uncommitted work and reset from main file

---

## Key Architectural Decisions

### Two-File System (Main + Work)

**Decision:** Main file modified only on explicit commit. Working file auto-saved for crash protection.

**Rationale:**
- User control over what becomes "real"
- Crash safety without losing uncommitted work
- Corruption safety (validation before commit prevents bad geometry from reaching main file)
- Familiar git-like mental model (work = staged, main = committed)

**Alternatives considered:**
- **Timestamped checkpoints** - Creates `design.FCStd.2025-11-18-143022` for each checkpoint. Too complex, unclear which version to use, requires cleanup logic, limited history value (users have git for this)
- **Unlimited version history** - Store every save as new version. Overkill for active session management, disk space overhead, users have git for long-term history
- **Auto-commit every N operations** - Users lose control, can't experiment freely, might commit broken state before realizing mistake
- **SQL-like transactions** - CAD isn't ACID, doesn't fit iterative workflow, rollback semantics unclear for geometric operations

---

### Resume by Default

**Decision:** `open_document()` and `create_document()` NEVER overwrite existing .work files. Always resume from existing work.

**Rationale:**
- Preserve uncommitted changes (expected behavior)
- Safe to call open multiple times
- Supports multiple chat sessions working on same project
- Discarding changes requires deliberate action (rollback)

**Alternatives considered:**
- **Always overwrite .work on open** - DANGEROUS, loses uncommitted work, users expect resume behavior
- **Prompt user on conflict** - Interrupts workflow, annoying for 90% of cases where user wants to resume
- **Timestamped backups before overwrite** - Complex, unclear which backup to restore, cleanup overhead

---

### Explicit Commit with Validation

**Decision:** User must call `commit_changes()`. System validates geometry before committing. Rejects commit if invalid.

**Rationale:**
- Critical safety: never corrupt main file
- Fail-fast: catch problems before they're committed
- User thinks before committing (intentional workflow)
- Recoverable: can fix errors or rollback

**Validation checks:**
1. Document recomputes successfully
2. All objects valid (no broken references)
3. All shapes geometrically valid
4. Document not empty

**Alternatives considered:**
- **No validation** - Unacceptable, main file could be corrupted, user loses work
- **Auto-commit on close** - Might commit broken state before user notices error
- **Warn but allow bad commits** - Defeats purpose of validation, corrupted main file still possible

---

### Auto-Save Every 5 Operations

**Decision:** Working file auto-saves after every 5 operations (transparent to user).

**Rationale:**
- Crash protection (lose at most 4 operations)
- Performance balance (not too slow, not too risky)
- Operation-based vs time-based (won't save mid-operation)

**Configurable:** `AUTO_SAVE_INTERVAL = 5` in constants.py

**Alternatives considered:**
- **Save on every operation** - Too slow, excessive disk I/O, poor user experience
- **Time-based (every 60s)** - Might save mid-operation, unpredictable behavior, race conditions
- **Manual save only** - Users forget, lose work in crashes, defeats purpose of crash protection

---

### Work File Location: Same Directory as Main File

**Decision:** `design.FCStd.work` sits next to `design.FCStd` by default.

**Rationale:**
- Simplicity (no configuration for 90% of users)
- Visibility (user knows where work file is)
- Natural cleanup (delete project folder = delete everything)
- Git-friendly (one .gitignore rule: `*.work`)
- Portability (move project = move everything together)

**Configuration Override:**

For advanced users, override default location via environment variable:

```bash
# Use custom directory for all working files
export ADAM_MCP_WORK_DIR="/Users/peter/cad_workspace"
# Results in: /Users/peter/cad_workspace/design.FCStd.work

# Use system temp directory
export ADAM_MCP_WORK_DIR="temp"
# Results in: /tmp/adam_mcp_work/design.FCStd.work
```

**Use cases for override:**
- Centralized working directory for multiple projects
- Separate disk/partition for working files (e.g., SSD for performance)
- Network mount for shared workspace (multi-machine workflows)

**Alternatives considered:**
- **Hidden `.adam_mcp/` folder** - Extra directory level, less visible, harder to find for troubleshooting
- **System temp (`/tmp`) as default** - OS might clean files unexpectedly, user can't find work easily
- **Home directory (`~/.adam_mcp`)** - Multiple projects in one flat folder, naming conflicts, messy

---

### Open in FreeCAD GUI

**Decision:** `open_in_freecad_gui()` launches FreeCAD desktop app with .work file for live preview.

**Rationale:**
- Visual feedback (users can see their design as they build it)
- Side-by-side workflow (Claude Code terminal + FreeCAD GUI)
- Real-time iteration (make change → reload GUI → verify → continue)
- Standard CAD workflow (matches how CAD users work: text editor + viewer)

**Note:** Manual reload required (FreeCAD doesn't support auto-reload, would need custom plugin)

**Alternatives considered:**
- **Export to viewer format (STEP/STL)** - Extra conversion step, loses FreeCAD-specific features, file size overhead
- **Embedded 3D viewer** - Complex, reinventing FreeCAD GUI, maintenance burden, feature parity impossible
- **Auto-reload via file watching** - Requires FreeCAD plugin (out of scope), polling is unreliable, race conditions

---

### User Manages Long-Term Versioning

**Decision:** adam-mcp manages active session (main + work files). User manages long-term history (git).

**Rationale:**
- Professional assumption (CAD users already have git workflows)
- Avoid duplication (don't reinvent version control)
- Simpler system (focus on session safety, not decades of history)
- Flexibility (user can use git, SVN, Dropbox, whatever)

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
- `WORK_FILE_SUFFIX = ".work"`
- `VALIDATE_BEFORE_COMMIT = True`

---

## Git Integration

**Recommended .gitignore:**
```gitignore
*.work
```

**Workflow:**
1. User works through adam-mcp (edits .work file)
2. User commits changes (validates, updates main file)
3. User git commits main file
4. .work file ignored by git (ephemeral workspace)

---

**Last Updated:** 2025-11-18
