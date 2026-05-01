# Coffee Grind Size Analyzer

Desktop application for analyzing coffee grind particle sizes from images. Detects particles, measures sizes, and produces particle size distribution (PSD) histograms.

## Project Overview

- **Main file:** `coffeegrindsize.py` — 3,222-line monolithic Python file
- **GUI class:** `coffeegrindsize_GUI` (62 methods) — requires tkinter root to instantiate
- **Original author:** Jonathan Gagné (MIT License, 2018)
- **Current target:** Python 3.7 (EOL)

## Modernization Effort

This fork is being modernized. See `IMPLEMENTATION_PLAN.md` for the detailed roadmap and `MODERNIZATION_ASSESSMENT.md` for the full analysis.

### Phases
1. **Phase 0:** Project setup (branch, `.gitignore`, `pyproject.toml`, `tests/`)
2. **Phase 1:** Comprehensive testing (lock in behavior before changes)
3. **Phase 2:** Code cleanup (remove debug code, fix bare excepts, fix wildcard imports)
4. **Phase 3:** Module restructuring (extract analysis, io, ui modules)
5. **Phase 4:** Python 3.10+ modernization
6. **Phase 5:** CI/CD pipeline
7. **Phase 6:** Optional UX modernization

## Key Constraint

All methods live on the GUI class and require a tkinter root to instantiate. Testing strategy works around this using:
- Hidden `Tk()` root with `withdraw()` for GUI-dependent tests
- Pure function extraction for computational methods
- Synthetic image fixtures for integration tests

## Dependencies

- numpy, scipy — numerical computations
- matplotlib — plotting (TkAgg backend)
- Pillow (PIL) — image processing
- pandas — data I/O

## Testing Strategy

When tests are added, they will cover:
- **Pure functions:** `smooth()`, `weighted_stddev()`, `attainable_mass_simulate()`, `ey_simulate()`, `lighter()`
- **Geometry:** `points_along_polygon()`, `quick_cluster()`
- **Image analysis:** `threshold_image()`, `launch_psd()`, `refresh_cluster_data()`
- **I/O:** `load_data()`, `save_data()` round-trip
- **Golden-file snapshots:** Full pipeline regression tests

## Known Issues

- `weighted_stddev()` mutates its input weights array (line 2742)
- Debug code left in production (`pdb` imports at lines 24–26, 1670)
- Bare `except:` clauses swallow errors silently
- Deprecated APIs: `np.fromstring`, `Image.ANTIALIAS`

## Build Artifacts

The `App/` directory contains a pre-built macOS .app bundle with Python 3.7. This should be removed from version control and produced via CI instead.

## 🔁 Persistent Work Log

To ensure continuity across sessions and accurate progress tracking, maintain a running work log in this project.

### Log File
- Location: `./.claude/work-log.md`
- Create the file if it does not exist.

### When to Update
Update the log **every time you:**
- Complete a task or subtask
- Modify the plan
- Encounter an error or blocker
- Make a significant decision
- Start or end a work session

### Log Format
Use the following structure for each entry:
[YYYY-MM-DD HH:MM] - <Short Title>

### Context
What task or plan step you are working on.

### Actions Taken
- Step-by-step summary of what was done
- Files created/modified (with paths)

### Decisions
- Key design or implementation decisions
- Tradeoffs considered (brief)

### Issues / Blockers
- Errors encountered
- Unknowns or risks

### Status
- ✅ Completed
- 🔄 In Progress
- ⛔ Blocked

### Next Steps
- Clear, actionable next steps

### Plan Tracking (Required if a Plan Exists)
If a plan exists (e.g., in `plan.md` or similar):
- Reference the **specific step(s)** being worked on
- Mark steps as complete in both:
    - The plan file
    - The work log

### Rules
- Append entries; **never overwrite history**
- Be concise but specific enough for another agent to resume work
- Prefer bullet points over paragraphs
- Always include file paths when relevant
- If resuming work, **read the last 2–3 log entries first**

### Goal
This log should allow any future Claude instance to:
- Instantly understand current progress
- Resume work without re-analysis
- Avoid duplicating effort

### Session Start Protocol
At the start of any session:
1. Read the last 3 entries in `./.claude/work-log.md`
2. Identify current status and next steps
3. Confirm alignment with any existing plan

## 🧪 Test Integrity & Change Tracking

Tests are the source of truth for correctness. Modifying tests to make failures pass must be treated as a high-risk action and fully documented.

### Test Change Log
- Location: `./.claude/test-change-log.md`
- Create if it does not exist

### When to Log (REQUIRED)
Log an entry ANY time you:
- Modify an existing test
- Delete or disable a test
- Relax assertions
- Change test inputs or expectations
- Skip/xfail a test
- Replace a failing test with a different one

### Required Justification Rule
You MUST answer:

> "Is this change fixing the test, or hiding a bug?"

If there is any uncertainty, assume it may be hiding a bug.

### Log Format
[YYYY-MM-DD HH:MM] - Test Change: <test name>

### Original Behavior
- What the test was asserting
- Why it failed

### Change Made
- Exact modification (before/after if possible)
- File path(s)

### Justification
- Why this change is correct
- Why the previous test was wrong or outdated

### Risk Assessment
- Could this hide a real bug? If not, why?
- What scenarios might now go untested?

### Linked Code Changes
- Files modified to address root cause (if any)

### Decision
- ✅ Valid test correction
- ⚠️ Temporary workaround
- ❌ Potential bug masking

### Follow-up Required
- Any additional tests needed?
- Any refactoring needed?

### Hard Rules
- NEVER silently modify or delete a test
- NEVER change a test without logging it
- Prefer fixing implementation over changing tests
- If changing a test, explicitly consider:
  - Was the expectation incorrect?
  - Has the requirement changed?
  - Is the implementation actually wrong?

### Preferred Workflow
When a test fails:

1. Diagnose root cause
2. Attempt to fix implementation FIRST
3. Only modify test if:
   - The test is incorrect, OR
   - Requirements have changed

4. If modifying a test:
   - Log it in `test-change-log.md`
   - Explain reasoning clearly

## 📋 Plan Enforcement
- Always reference a plan step in work-log entries
- Mark steps complete in BOTH:
  - `plan.md`
  - `work-log.md`
- Do not work outside the plan unless explicitly justified

