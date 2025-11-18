# Working File Workflow

## User Workflow (Simple Terms)

### Opening and Editing Documents

When you work on a CAD design through adam-mcp, the system protects your work using two files:

1. **Main file** (`bracket.FCStd`) - Your stable, committed design
2. **Working file** (`bracket.FCStd.work`) - Your experimental workspace

**The workflow:**

```
1. Open a project
   → System copies main file to working file
   → All edits happen on working file
   → Main file stays untouched

2. Make changes
   → Add boxes, fillets, sketches, etc.
   → Working file auto-saves every 5 operations
   → Main file still untouched (safe!)

3. Review your work
   → Open in FreeCAD GUI to see geometry
   → Verify changes are correct

4. Commit when happy
   → Explicitly commit changes
   → System validates geometry first
   → If valid: working file → main file
   → If invalid: reject commit, warn user

5. Version control (your responsibility)
   → Git commit the main file
   → Push to remote
   → Your long-term backup system
```

### Example Session in Claude Code

```
You: "Open my bracket design at ~/designs/bracket.FCStd"
Claude: [Uses open_document MCP tool]
        → Creates ~/designs/bracket.FCStd.work
        ✓ Document opened for editing

You: "Add a 50x30x20mm box"
Claude: [Uses create_box MCP tool]
        → Box created
        → Auto-saved to .work file
        ✓ Box added

You: "Show me"
Claude: [Uses open_in_gui MCP tool]
        → FreeCAD opens showing your working file
        ✓ You see the box

You: "Add 5mm fillets to all edges"
Claude: [Uses fillet_edges MCP tool]
        → Fillets added
        → Auto-saved to .work file
        ✓ Fillets added

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

### Decision 6: User's Responsibility for Long-Term Versioning

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
