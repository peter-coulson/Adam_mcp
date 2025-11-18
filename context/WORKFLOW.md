# Working File Workflow

## User Workflow (Simple Terms)

### Opening and Editing Documents

When you work on a CAD design through adam-mcp, the system protects your work using two files:

1. **Main file** (`bracket.FCStd`) - Your stable, committed design
2. **Working file** (`bracket.FCStd.work`) - Your experimental workspace

**The workflow:**

```
1. Open a project
   → RESUME BY DEFAULT: If .work file exists, use it (continue where you left off)
   → Only creates .work from main if .work doesn't exist
   → All edits happen on working file
   → Main file stays untouched

2. Make changes
   → Add boxes, fillets, sketches, etc.
   → Working file auto-saves every 5 operations
   → Main file still untouched (safe!)

3. Review your work in real-time
   → Use open_in_freecad_gui() to launch FreeCAD GUI
   → GUI shows your .work file
   → Reload in GUI to see latest auto-saved changes
   → Claude Code + FreeCAD GUI side-by-side workflow

4. Commit when happy
   → Explicitly commit changes
   → System validates geometry first
   → If valid: working file → main file
   → If invalid: reject commit, warn user

5. Reset if needed
   → Use rollback_working_changes() to discard uncommitted work
   → This is the ONLY way to reset from main file
   → Reopening doesn't reset (it resumes)

6. Version control (your responsibility)
   → Git commit the main file
   → Push to remote
   → Your long-term backup system
```

### Example Session in Claude Code

```
You: "Open my bracket design at ~/designs/bracket.FCStd"
Claude: [Uses open_document MCP tool]
        → Checks if ~/designs/bracket.FCStd.work exists
        → .work exists! Resumes from uncommitted changes
        ✓ Document opened (continuing where you left off)

You: "Show me the current state"
Claude: [Uses open_in_freecad_gui MCP tool]
        → Launches FreeCAD GUI with .work file
        ✓ FreeCAD window opens showing your design

You: "Add a 50x30x20mm box"
Claude: [Uses create_box MCP tool]
        → Box created
        → Auto-saved to .work file
        ✓ Box added

You: "Can I see it?"
Claude: "The FreeCAD GUI is already open. Reload the document (File > Reload)
         to see the new box in the .work file."

You: "Add 5mm fillets to all edges"
Claude: [Uses fillet_edges MCP tool]
        → Fillets added
        → Auto-saved to .work file
        ✓ Fillets added (reload GUI to see changes)

You: "Perfect! Commit these changes"
Claude: [Uses commit_changes MCP tool]
        → Validates document (checks geometry is valid)
        → Copies .work file → main file
        ✓ Changes committed to bracket.FCStd

You: "Git commit it"
Claude: [Uses git bash commands]
        → git add bracket.FCStd
        → git commit -m "Added filleted box"
        ✓ Committed to git
```

**Key points:**
- FreeCAD GUI shows the `.work` file (not main file)
- Use File > Reload in GUI to see latest auto-saved changes
- Multiple editing sessions can work on same `.work` file
- Only explicit `rollback_working_changes()` discards uncommitted work

### If Something Goes Wrong

```
You: "Add complex feature X"
Claude: [Uses tool, but it corrupts geometry]
        ✗ Geometry invalid

You: "Oh no! Undo that"
Claude: [Uses rollback_working_changes MCP tool]
        → Closes working file
        → Copies main file → working file (reset)
        → Reopens working file
        ✓ All changes since last commit discarded
        ✓ Back to known-good state
```

### File Locations

**Default: Same directory as main file**
```
/Users/peter/designs/
  bracket.FCStd        # Main file (your committed design)
  bracket.FCStd.work   # Working file (auto-managed)
```

**Why same directory?**
- Simple - no configuration needed
- Visible - you can see both files if needed
- Natural cleanup - delete project deletes .work file too
- Git-friendly - add `*.work` to .gitignore

**Can be configured** via environment variable:
```bash
# Use custom directory for all working files
export ADAM_MCP_WORK_DIR="/tmp/adam_mcp_work"

# Or use system temp
export ADAM_MCP_WORK_DIR="temp"
```

### Crash Recovery

**If MCP server crashes:**
- Working file exists on disk (auto-saved)
- Main file untouched (safe!)
- Reopen working file, continue from last auto-save
- Lost at most 4 operations (auto-save every 5)

**If you close chat:**
- Working file preserved on disk
- Next session: reopen and continue

**If you mess up:**
- Main file still clean
- Use rollback_working_changes() to reset
- Start over from last commit

---

## Why We Made These Decisions

### Decision 1: Two-File System (Main + Work)

**What we chose:**
- Main file (stable, only changes on explicit commit)
- Working file (auto-saved, experimental)

**Why:**
- **Simplicity** - Only 2 files, easy to understand
- **User control** - User decides when changes become "real"
- **Crash safety** - Auto-save protects against crashes
- **Corruption safety** - Main file never corrupted by bad operations
- **Familiar mental model** - Like git staging area (work = staged, main = committed)

**Alternatives considered:**
- ❌ Timestamped checkpoints - Too complex, cleanup overhead, limited history
- ❌ Unlimited version history - Overkill, users have git for this
- ❌ Auto-commit on every save - No way to discard bad changes

### Decision 2: Explicit Commits (Manual User Control)

**What we chose:**
- User must explicitly call `commit_changes()`
- Validation happens before commit
- Commit rejected if geometry invalid

**Why:**
- **Safety** - Can't accidentally commit corrupted state
- **Intentional** - User thinks before committing
- **Recoverable** - Can discard bad work before it affects main file
- **Matches CAD workflow** - CAD is iterative, not transactional

**Alternatives considered:**
- ❌ Auto-commit every N operations - User loses control, can't experiment freely
- ❌ Auto-commit on close - Might commit broken state before user notices
- ❌ SQL-like transactions - CAD isn't ACID, doesn't fit the workflow

### Decision 3: Work File in Same Directory

**What we chose:**
- `bracket.FCStd.work` sits next to `bracket.FCStd`
- User can see both files
- Can be overridden with environment variable

**Why:**
- **Simplicity** - No configuration needed for 90% of users
- **Visibility** - User knows where working file is
- **Natural cleanup** - Delete project folder deletes everything
- **Git-friendly** - One .gitignore rule: `*.work`
- **Portability** - Move project folder, everything moves together

**Alternatives considered:**
- ❌ Hidden `.adam_mcp/` folder - Extra complexity, one more directory level
- ❌ System temp (`/tmp`) - OS might clean it, user can't find it easily
- ❌ Home directory (`~/.adam_mcp`) - Multiple projects in one folder, messy

**Configuration option:**
Advanced users can override if needed:
```bash
# Put all working files in temp
export ADAM_MCP_WORK_DIR="/tmp/adam_mcp_work"
```

### Decision 4: Auto-Save Every 5 Operations

**What we chose:**
- Working file auto-saves after every 5 operations
- Transparent to user
- Configurable via constant

**Why:**
- **Crash protection** - Lose at most 4 operations
- **Performance** - Not saving on every operation (too slow)
- **Balance** - Frequent enough to be safe, infrequent enough to be fast

**Alternatives considered:**
- ❌ Save on every operation - Too slow, excessive disk I/O
- ❌ Time-based (every 60s) - Might save in middle of complex operation
- ❌ Manual save only - Users forget, lose work in crashes

**Configuration:**
```python
AUTO_SAVE_INTERVAL = 5  # Adjustable per user preference
```

### Decision 5: Validation Before Commit

**What we chose:**
- Run `validate_document()` before every commit
- Reject commit if geometry invalid
- User must fix errors or rollback

**Why:**
- **Critical safety** - Never corrupt main file
- **Fail-fast** - Catch problems before they're committed
- **Clear feedback** - User knows immediately if something is wrong
- **Recoverable** - Can fix or rollback, not stuck

**Validation checks:**
1. Document recomputes successfully
2. All objects valid (no broken references)
3. All shapes geometrically valid
4. No empty document (has objects)

**Alternative considered:**
- ❌ No validation - Main file could be corrupted, unacceptable risk

### Decision 6: Resume by Default (Never Overwrite .work Files)

**What we chose:**
- `open_document()` and `create_document()` NEVER overwrite existing `.work` files
- If `.work` exists, resume from it (preserve uncommitted changes)
- Only `rollback_working_changes()` can reset from main file
- Opening a document multiple times is safe

**Why:**
- **Preserve work** - Never lose uncommitted changes accidentally
- **Expected behavior** - Users expect to continue where they left off
- **Safe reopening** - Can safely call `open_document()` multiple times
- **Explicit reset** - Discarding changes requires deliberate action
- **Multiple sessions** - Different chat sessions can work on same `.work` file

**Implementation:**
```python
def setup_working_file(main_file_path: str) -> str:
    work_file_path = get_work_file_path(main_file_path)

    # Resume editing if work file already exists (NEVER overwrite)
    if Path(work_file_path).exists():
        return work_file_path

    # Initialize work file from main if main exists
    if Path(main_file_path).exists():
        shutil.copy2(main_file_path, work_file_path)

    return work_file_path
```

**Alternatives considered:**
- ❌ Always overwrite .work on open - DANGEROUS, loses uncommitted work
- ❌ Prompt user on conflict - Interrupts workflow, annoying for normal case
- ❌ Timestamped backups - Complex, unclear which version to use

**Multiple sessions:**
Since `.work` files are never overwritten, multiple MCP sessions (different Claude Code chats) can safely work on the same project. They all edit the same `.work` file. Conflicts are possible but acceptable for MVP - users manage this manually.

### Decision 7: Open in FreeCAD GUI (Live Preview)

**What we chose:**
- Added `open_in_freecad_gui()` tool to launch FreeCAD GUI
- Opens the `.work` file (not main file)
- Cross-platform support (macOS, Linux, Windows)
- User manually reloads in GUI to see latest changes

**Why:**
- **Visual feedback** - Users can see their CAD design as they build it
- **Side-by-side workflow** - Claude Code terminal + FreeCAD GUI windows
- **Real-time iteration** - Make change → reload GUI → verify → continue
- **Standard workflow** - Matches how CAD users work (text editor + CAD viewer)

**Implementation security:**
Platform-specific file opening commands:
```python
# macOS - use 'open' command (standard, no shell injection risk)
subprocess.Popen(["open", "-a", "FreeCAD", work_file_path])

# Linux - use 'freecad' executable from PATH
subprocess.Popen(["freecad", work_file_path])

# Windows - use os.startfile() (native, no shell=True needed)
os.startfile(work_file_path)
```

**Security note on `# nosec` comments:**
- File paths come from internal state, not user input (safe)
- B603/B607: Using standard system commands (`open`, `freecad`) is correct approach
- B606: `os.startfile()` is Windows-native, safer than subprocess with shell=True
- B404: subprocess module is required for launching external apps
- All warnings are false positives for this legitimate use case

**Why not auto-reload in GUI:**
- FreeCAD doesn't support file watching/auto-reload
- Would require custom FreeCAD plugin (out of scope for MVP)
- Manual reload is acceptable, matches standard CAD workflow

**Alternatives considered:**
- ❌ Export to viewer format (STEP/STL) - Extra steps, loses FreeCAD features
- ❌ Embedded 3D viewer - Complex, reinventing FreeCAD GUI
- ❌ Auto-reload via polling - Requires FreeCAD plugin, too complex

### Decision 8: User's Responsibility for Long-Term Versioning

**What we chose:**
- We manage active session (main + work files)
- User manages long-term history (git, backups, cloud)

**Why:**
- **Professional assumption** - CAD users already have git/backup workflows
- **Avoid duplication** - Don't reinvent version control
- **Simpler system** - Focus on session safety, not decades of history
- **Flexibility** - User can use git, SVN, Dropbox, whatever they want

**What we provide:**
- ✓ Crash protection (auto-save working file)
- ✓ Corruption protection (validation, rollback)
- ✓ Session management (main + work files)

**What user provides:**
- Git commits of main file
- Remote backups
- Long-term version history

**Clear boundary:**
```
adam-mcp:         Protects active work session (minutes to hours)
User's git/VCS:   Protects long-term history (days to years)
```

---

## Configuration Reference

### Constants (in server.py)

```python
# Working file configuration
AUTO_SAVE_INTERVAL = 5           # Save work file every N operations
WORK_FILE_SUFFIX = ".work"       # Extension for working files
VALIDATE_BEFORE_COMMIT = True    # Safety gate for commits
```

### Environment Variables

```bash
# Optional: Override working file location
export ADAM_MCP_WORK_DIR="/custom/path"    # Custom directory
export ADAM_MCP_WORK_DIR="temp"            # Use system temp

# Default (if not set): Same directory as main file
```

### .gitignore Recommendation

```gitignore
# Ignore adam-mcp working files
*.work
```

---

## Trade-offs and Limitations

### What This System Provides
- ✓ Crash protection (auto-save)
- ✓ Corruption protection (validation)
- ✓ User control (explicit commits)
- ✓ Rollback capability (discard bad work)
- ✓ Simple mental model (2 files)

### What This System Does NOT Provide
- ✗ Unlimited version history (use git)
- ✗ Branching/merging (use git)
- ✗ Cloud sync (use git/Dropbox)
- ✗ Multi-user collaboration (use git + CAD PDM)
- ✗ Undo across sessions (use git revert)

### Known Limitations
- Working file survives crashes, but uncommitted work is lost if:
  - User deletes .work file manually
  - OS cleans temp directory (if configured)
  - Disk fills up (save fails)
- Auto-save interval is fixed (5 operations) - not time-based
- Only one working file per main file (no parallel experiments)
- FreeCAD GUI requires manual reload to see changes (no auto-refresh)
- Multiple sessions editing same .work file can conflict (acceptable for MVP)

### Future Enhancements (If Needed)
- Operation log for replay (event sourcing)
- Configurable auto-save interval
- Multiple working branches per project
- Integration with git (auto-commit on commit_changes)
- Cloud sync of working files

---

## Summary

**This workflow is optimized for:**
- Professional CAD users who already use git
- Iterative design sessions (hours of work)
- Safety first (never corrupt main file)
- User control (explicit commits)
- Simplicity (2 files, clear rules)

**The core principle:**
> Working file is your sandbox. Main file is your source of truth. You decide when sandbox → truth.

This matches how professional developers work (feature branch → main), applied to CAD.
