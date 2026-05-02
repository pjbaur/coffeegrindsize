# Coffeegrindsize Modernization — Development Plan

## Context

The coffeegrindsize application is a desktop tool for analyzing coffee grind particle sizes from images. It lives in a single 3,222-line monolithic Python file (`coffeegrindsize.py`) with one god-class (`coffeegrindsize_GUI`, 62 methods). It has zero tests, no CI/CD, no `.gitignore`, no `pyproject.toml`, and targets Python 3.7 (EOL June 2023). The goal is to modernize it incrementally — tests first, then cleanup, restructuring, and infrastructure — without breaking its scientific accuracy.

**Key constraint:** All methods live on the GUI class, requiring a tkinter root to instantiate. Testing strategy must work around this.

**Critical file:** `/private/tmp/gt-lab/coffee-grind-size-myfork/coffeegrindsize.py`

---

## Phase 0: Project Setup (~1 hour)

No application code changes. Infrastructure only.

### 0.1 [x] Create working branch
```
git checkout -b modernization master
```

### 0.2 [x] Create `.gitignore`
```
__pycache__/
*.pyc
*.pyo
.DS_Store
Thumbs.db
.env
.env.local
.env.*.local
.claude/settings.local.json
.trees/
App/venv/
App/dist/
App/build/
*.egg-info/
dist/
build/
.pytest_cache/
.ruff_cache/
htmlcov/
.coverage
```

### 0.3 [x] Create `pyproject.toml`
```toml
[project]
name = "coffeegrindsize"
version = "1.1.0"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.24",
    "scipy>=1.10",
    "matplotlib>=3.7",
    "Pillow>=9.5",
    "pandas>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-cov>=4.1",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]
```

### 0.4 [x] Create test directory structure
```
tests/
├── __init__.py
├── conftest.py
├── fixtures/                    # Small test images, sample CSVs
├── test_pure_functions.py
├── test_geometry.py
├── test_clustering.py
├── test_threshold.py
├── test_particle_detection.py
├── test_statistics.py
├── test_io.py
└── test_defaults.py
```

### 0.5 [x] Verification
- `pip install -e ".[dev]"` succeeds
- `pytest --collect-only` runs without errors

---

## Phase 1: Comprehensive Testing (5–7 days)

**Goal:** Lock in current behavior before any code changes. Every subsequent phase is validated against these tests.

### 1a. [x] conftest.py — Shared Fixtures

**File:** `tests/conftest.py`

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `tk_root` | session | Hidden `Tk()` root via `withdraw()`. Yields root, destroys on teardown. On headless CI: requires `xvfb`. |
| `gui` | function | Fresh `coffeegrindsize_GUI(tk_root)` per test. Prevents state leakage. |
| `synthetic_white_image` | function | 100×100 all-white PIL Image (RGB 255,255,255) |
| `synthetic_image_with_dark_circle` | function | 100×100 white image, dark circle (blue=20) radius 10 at (50,50). Returns `(image, center, radius)`. |
| `synthetic_two_circles_image` | function | 100×100 white, two dark circles radius 5 at (25,25) and (75,75). |
| `sample_cluster_data` | function | Dict with 10 pre-built particles: `surfaces`, `long_axes`, `short_axes`, `roundness`, `volumes`, `pixel_scale=10.0` |
| `sample_csv_content` | function | CSV string matching `save_data()` output format |

---

### 1b. [x] Pure Function Tests — `tests/test_pure_functions.py`

#### `smooth(x, window_size)` — lines 2427–2429
Implementation: `np.convolve(x, np.ones(window_size)/window_size, "same")`

| Test | Input | Expected | Why |
|------|-------|----------|-----|
| `test_smooth_impulse` | `x=[0,0,0,1,0,0,0]`, ws=3 | `[0,0,⅓,⅓,⅓,0,0]` | Shows kernel shape |
| `test_smooth_uniform` | `x=[1,1,1,1,1]`, ws=3 | `[⅔,1,1,1,⅔]` | Edge effects from "same" mode |
| `test_smooth_ramp` | `x=[1,2,3,4,5]`, ws=3 | `[1.0,2.0,3.0,4.0,3.0]` | Boundary behavior |
| `test_smooth_window_1` | `x=[1,2,3,4]`, ws=1 | `[1,2,3,4]` | Identity (degenerate) |
| `test_smooth_window_larger_than_data` | `x=[1,2,3]`, ws=5 | shape=3, no crash | Edge case |

#### `weighted_stddev(data, weights, frequency, unbiased)` — lines 2730–2756

| Test | data | weights | freq | unbiased | Expected |
|------|------|---------|------|----------|----------|
| `test_wstddev_equal_weights` | `[1,2,3,4,5]` | `[1,1,1,1,1]` | T | T | `√2.5 ≈ 1.5811` |
| `test_wstddev_reliability` | `[1,2,3]` | `[0.5,0.3,0.2]` | F | T | Hand-calculated with reliability bias |
| `test_wstddev_biased` | `[1,2,3,4,5]` | `[1,1,1,1,1]` | T | F | Population stddev |
| `test_wstddev_mutates_weights` | `[1,2]` | `[2,3]` | T | T | Assert weights array IS modified (documents known bug) |

**Hand-calculated verification for `test_wstddev_equal_weights`:**
- bias_estimator = (5-1)/5 = 0.8
- wmean = 3.0, deviations² = [4,1,0,1,4]
- wvar = (4+1+0+1+4)×0.2 / 0.8 = 2.0/0.8 = 2.5
- result = √2.5

#### `attainable_mass_simulate(volumes)` — lines 2023–2035
Constants: `depth_limit = 0.1` mm

| Test | Input radius | Expected |
|------|-------------|----------|
| `test_attainable_tiny` | r=0.05 (< depth_limit) | Volume unchanged |
| `test_attainable_boundary` | r=0.1 (== depth_limit) | Volume unchanged |
| `test_attainable_large` | r=0.5 | V − 4/3π(0.4)³ |
| `test_attainable_mixed` | [tiny, large] | [unchanged, reduced] |

#### `ey_simulate(surfaces)` — lines 2038–2044
Formula: `speed = 1/surface`, `ey = speed/(0.25014+speed) × 0.3`

| Test | surfaces | Expected |
|------|----------|----------|
| `test_ey_unit` | `[1.0]` | `1/(0.25014+1) × 0.3 ≈ 0.2400` |
| `test_ey_large_surface` | `[1e6]` | Near 0 |
| `test_ey_small_surface` | `[0.001]` | Near 0.3 |

#### `lighter(color, percent)` — lines 2721–2726
Input/output in [0,1] range. Blends toward white.

| Test | color | percent | Expected |
|------|-------|---------|----------|
| `test_lighter_0pct` | `(0.5,0.5,0.5)` | 0.0 | `(0.5,0.5,0.5)` unchanged |
| `test_lighter_100pct` | `(0.5,0.5,0.5)` | 1.0 | `(1.0,1.0,1.0)` white |
| `test_lighter_black_50` | `(0,0,0)` | 0.5 | `(0.5,0.5,0.5)` |

---

### 1c. [x] Geometry Tests — `tests/test_geometry.py`

#### `points_along_polygon(X, Y, X_poly, Y_poly)` — lines 1987–2020
Finds points within √2×1.01 of polygon edge segments.

| Test | Points | Polygon | Expected |
|------|--------|---------|----------|
| `test_point_on_edge` | `(5,0)` | edge `(0,0)→(10,0)` | Index found |
| `test_point_far` | `(5,5)` | edge `(0,0)→(10,0)` | Empty result |
| `test_empty_points` | empty arrays | any | Empty result |

---

### 1d. [x] Clustering Tests — `tests/test_clustering.py`

#### `quick_cluster(xlist, ylist, xstart, ystart)` — lines 2432–2496
Flood-fill with Manhattan distance ≤ 1.001.

| Test | Pixels | Start | Expected |
|------|--------|-------|----------|
| `test_single_pixel` | `(5,5)` | 5,5 | `{0}` |
| `test_adjacent` | `(0,0),(1,0)` | 0,0 | `{0,1}` |
| `test_diagonal_not_connected` | `(0,0),(1,1)` | 0,0 | `{0}` only (Manhattan=2) |
| `test_l_shape` | `(0,0),(1,0),(2,0),(2,1),(2,2)` | 0,0 | All 5 |
| `test_two_blobs` | group1 + gap + group2 | start in group1 | group1 only |

---

### 1e. [x] Threshold Tests — `tests/test_threshold.py`

Tests `threshold_image()` (lines 1862–1984). Requires injecting synthetic images into `gui.img_source` and setting GUI variables.

| Test | Image | Expected |
|------|-------|----------|
| `test_threshold_all_white` | 100×100 white | No thresholded pixels |
| `test_threshold_half_dark` | Top half blue=50, bottom white | ~50% thresholded |
| `test_threshold_with_polygon` | Dark circle + polygon mask | Only pixels inside polygon |

---

### 1f. [x] Statistics Tests — `tests/test_statistics.py`

Tests `update_statistics()` (lines 2758–2826). Inject known cluster arrays via `sample_cluster_data` fixture, mock GUI StringVar objects, verify computed averages/stddevs are positive and reasonable.

---

### 1g. [x] I/O Tests — `tests/test_io.py`

CSV round-trip: mock `filedialog`, call `save_data()` to temp dir, read back with pandas, assert cluster arrays match. Test `load_data()` with a fixture CSV.

---

### 1h. [x] Defaults Tests — `tests/test_defaults.py`

No GUI needed — test module-level constants directly.

| Test | What |
|------|------|
| `test_reference_objects_dict` | 14 entries, "US Quarter" = 24.26, "Custom" = None |
| `test_comparison_class` | `Comparison(a=1).a == 1` |
| `test_default_constants` | `def_threshold == 58.8`, `def_maxcost == 0.35`, `def_min_surface == 5` |

---

### 1i. [x] Golden-file Snapshot Test

- Create a small (50×50) synthetic test image with 3 known dark circles
- Run full pipeline: threshold → launch_psd → refresh_cluster_data → save to `tests/fixtures/golden_clusters.csv`
- Test asserts numerical equality (within float tolerance) against golden file
- This is the ultimate regression guard for all future phases

### 1j. [x] Phase 1 Verification
```
pytest -v --tb=short          # All tests pass
pytest --cov=coffeegrindsize  # Coverage reported for all tested functions
```

---

## Phase 2: Code Cleanup (1–2 days)

**Status:** Complete as of 2026-05-01.

**Depends on:** Phase 1 complete. Run full test suite after each change.

### 2.1 [x] Remove debug code
- Lines 24–26: `import pdb` / `stop = pdb.set_trace` → delete
- Line 666: `subMenu.add_command(label="Python Debugger...", command=self.pdb_call)` → delete
- Lines 1669–1670: `pdb_call` method → delete

**Verify:** `grep -n "pdb" coffeegrindsize.py` → empty

### 2.2 [x] Fix bare `except:` clauses (8 occurrences)
All follow the pattern `try: float(var.get()) except: return`. Replace each with `except (ValueError, TypeError):`.

| Line | Context |
|------|---------|
| ~915 | `update_pixel_scale` |
| ~1880 | `threshold_image` |
| ~2068 | `launch_psd` |
| ~2503 | `psd_hist_from_data` |
| ~2597 | `psd_hist_from_data` (xmin/xmax) |
| ~2621 | `psd_hist_from_data` (nbins) |
| ~2769 | `update_statistics` |
| ~3100 | `save_data` |

### 2.3 [x] Fix wildcard import
Replace `from tkinter import *` (line 3) with explicit imports. Determine exact list by grepping for tkinter names used (`Frame`, `Label`, `Button`, `Canvas`, `StringVar`, `IntVar`, `NORMAL`, `DISABLED`, `LEFT`, `RIGHT`, `TOP`, `BOTTOM`, `BOTH`, `X`, `Y`, `N`, `S`, `E`, `W`, `NW`, `NE`, `SE`, `SW`, `END`, `HORIZONTAL`, `VERTICAL`, `SUNKEN`, `RAISED`, `Scrollbar`, `Menu`, `Checkbutton`, `OptionMenu`, `PhotoImage`, `Entry`, `Tk`).

### 2.4 [x] Fix mainloop hack
Replace lines 3216–3221 (`while True: try: root.mainloop() ...`) with plain `root.mainloop()`. The `UnicodeDecodeError` was a Python 3.7/old macOS issue.

### 2.5 [x] Fix `weighted_stddev` mutation bug
Line 2742: `weights /= np.nansum(weights)` → `weights = weights / np.nansum(weights)`. Update the Phase 1 test to assert weights are NOT mutated.

### 2.6 [x] Add ruff linting
Run `ruff check coffeegrindsize.py`, fix non-behavioral issues only (unused imports, trailing whitespace). Add `.pre-commit-config.yaml` with ruff.

---

## Phase 3: Module Restructuring (3–5 days)

**Depends on:** Phase 1 (tests), Phase 2 (clean code). Extract one module at a time, test after each.

**Status:** ✅ Completed on 2026-05-01.

Implemented package layout, extracted config/models/analysis/io/utils modules, moved the GUI into `coffeegrindsize/ui/app.py`, and kept `coffeegrindsize.py` as a compatibility shim. Verification: `uv run --extra dev ruff check coffeegrindsize coffeegrindsize.py` and `uv run --extra dev pytest` both pass.

### Target package layout
```
coffeegrindsize/
├── __init__.py
├── __main__.py              # Entry point
├── config.py                # Constants, defaults, reference_objects_dict
├── models.py                # Comparison class
├── analysis/
│   ├── __init__.py
│   ├── threshold.py         # threshold_image core logic
│   ├── clustering.py        # quick_cluster, flood-fill
│   ├── statistics.py        # weighted_stddev, update_statistics core
│   ├── simulation.py        # attainable_mass_simulate, ey_simulate
│   └── geometry.py          # points_along_polygon, smooth
├── io/
│   ├── __init__.py
│   └── csv_io.py            # save/load data logic (no dialogs)
├── ui/
│   ├── __init__.py
│   ├── app.py               # Slimmed GUI class
│   ├── toolbar.py
│   ├── canvas.py
│   ├── dialogs.py
│   └── histogram.py         # psd_hist_from_data
└── utils.py                 # lighter()
```

### Extraction order
1. [x] `config.py` — module constants (lines 28–88). Zero risk.
2. [x] `models.py` — `Comparison` class (lines 91–95). Trivial.
3. [x] `analysis/simulation.py` — `attainable_mass_simulate`, `ey_simulate`. Remove `self`, make standalone.
4. [x] `analysis/geometry.py` — `points_along_polygon`, `smooth`.
5. [x] `analysis/clustering.py` — `quick_cluster`.
6. [x] `analysis/statistics.py` — `weighted_stddev` + computation core of `update_statistics`.
7. [x] `analysis/threshold.py` — computation core of `threshold_image`.
8. [x] `io/csv_io.py` — DataFrame creation/CSV logic from `save_data`/`load_data`.
9. [x] `utils.py` — `lighter()`.
10. [x] `ui/` — GUI class stays mostly intact, delegates to analysis modules. Last priority.

Keep `coffeegrindsize.py` as a thin shim that imports and launches the package.

### Per-extraction pattern
1. [x] Create new module with extracted function(s) (remove `self` param)
2. [x] In GUI class, replace method body with delegation call
3. [x] Update test imports
4. [x] `pytest` — must pass
5. [x] Golden-file test — must produce identical output
6. [x] Commit

---

## Phase 4: Python 3.10+ Modernization (2–3 days)

**Depends on:** Phase 1.

### 4.1 [x] Fix deprecated APIs
| Location | Current | Fix |
|----------|---------|-----|
| Line 2972 | `np.fromstring(...)` | `np.frombuffer(...)` |
| Line 1767 | `Image.ANTIALIAS` | `Image.LANCZOS` |
| Lines 1915, 1941 | `np.max(contained) is False` | `not np.any(contained)` |

### 4.2 [x] Add type hints to extracted analysis modules
Start with `analysis/simulation.py`, `analysis/geometry.py`, `analysis/clustering.py`. Use `numpy.typing.NDArray`.

### 4.3 [x] Modernize string formatting
Replace `.format()` calls with f-strings throughout.

### 4.4 [x] Remove `App/` from version control
```
git rm -r --cached App/
```
Add `App/` to `.gitignore`. Built artifacts should come from CI.

---

## Phase 5: CI/CD (2–3 days)

**Status:** ✅ Completed on 2026-05-01.

**Depends on:** Phase 1.

### 5.1 [x] GitHub Actions workflow — `.github/workflows/ci.yml`
- Matrix: Python 3.10, 3.11, 3.12 on Ubuntu (macOS deferred — tkinter on GH macOS runners is brittle; revisit once Ubuntu leg is stable)
- Linux: `sudo apt-get install -y xvfb`, run tests with `xvfb-run -a`
- Steps: checkout → install xvfb → setup-uv → `uv python install` → `uv sync --extra dev` → `uv run ruff check .` → `xvfb-run -a uv run pytest -v --cov`
- **Note:** `uv sync` substituted for `pip install -e ".[dev]"` to match local dev (`uv.lock` is checked in). Concurrency group cancels superseded PR runs. Coverage XML uploaded as artifact from the 3.12 leg only.

### 5.2 [x] Coverage configuration
In `pyproject.toml`: `fail_under = 60`. Coverage scope is restricted to `coffeegrindsize` excluding `coffeegrindsize/ui/*` and `coffeegrindsize/__main__.py` (GUI code requires a live tkinter session and is unsuitable for unit tests). Baseline cov on the included modules is 89.81%, leaving ~30-point headroom above the gate.

---

## Phase 6: Optional UX Modernization (1 day – 3 weeks)

**Depends on:** Phases 2–3.

**Recommendation:** Start with `sv_ttk` for an immediate visual refresh (1 day).

- [x] Add `sv_ttk` to runtime dependencies and apply `sv_ttk.set_theme("light")` at startup.
- [x] Replace `tkinter.*` widgets with `ttk.*` equivalents.

Future option: web-based UI (Streamlit/Gradio) reusing extracted analysis modules.

---

## Risk Summary

| Risk | Impact | Mitigation |
|------|--------|------------|
| GUI fixture fails on headless CI | Tests blocked | `xvfb-run` on Linux; mock-based tests where possible |
| Extraction breaks subtle state dependency | Regression | Golden-file snapshot tests catch numerical drift |
| `weighted_stddev` fix changes downstream stats | Behavioral change | Document; verify with known datasets |
| Wildcard import replacement misses a name | App crash at startup | Grep-based enumeration + manual test launch |
| Deprecated API replacement changes output | Numerical drift | `np.frombuffer` produces identical data; pixel comparison tests |

---

## Verification Strategy

After each phase:
1. [ ] `pytest -v --tb=short` — all tests pass
2. [ ] Golden-file test — identical numerical output
3. [ ] Manual app launch — GUI opens, loads an image, runs analysis
4. [ ] `ruff check .` — no lint errors (Phase 2+)
