# Coffeegrindsize Modernization Assessment

**Date:** 2026-03-08
**Current version:** v1.0.0 (last meaningful update ~2021)
**License:** MIT (Jonathan Gagné, 2018)

---

## What the App Does

Desktop application that analyzes images of ground coffee particles. It detects individual particles, measures their sizes, and produces particle size distribution (PSD) histograms. Supports comparison across samples and extraction yield simulation. Used by coffee enthusiasts and professionals for grind quality analysis.

---

## Current State

### Architecture
- **Single monolithic file:** `coffeegrindsize.py` — 3,222 lines, one god-class (`coffeegrindsize_GUI`) with 62 methods
- No separation of concerns: UI, image processing, statistics, and I/O are all interleaved
- No configuration file — all defaults are hardcoded module-level variables (lines 28–88)
- No plugin or extension system

### Tech Stack
| Component | Current | Status |
|-----------|---------|--------|
| Python | 3.7 (bundled in App/venv) | EOL since June 2023 |
| GUI | tkinter | Functional but dated look/feel |
| Plotting | matplotlib (TkAgg backend) | Works but embedded charts are clunky |
| Image processing | Pillow (PIL) | Still maintained |
| Numerics | numpy, scipy | Still maintained |
| Data I/O | pandas | Still maintained |
| Packaging (macOS) | PyInstaller → DMG | Functional |
| Packaging (Windows) | PyInstaller → WiX MSI | Functional |
| Legacy packaging | py2app (`App/setup.py`) | Abandoned/unused |

### What's Missing
- **No tests** — zero unit, integration, or end-to-end tests
- **No CI/CD** — builds are fully manual via shell scripts
- **No type hints** anywhere
- **No linting/formatting** configuration
- **No .gitignore** file
- **No dependency lockfile** (no requirements.txt, no pyproject.toml)

### Code Quality Issues
- `import pdb` and `pdb.set_trace()` left in production code (lines 24–26, 1670)
- Multiple bare `except:` clauses (lines ~2068, 2770, 2999, 3005) — swallow all errors silently
- `from tkinter import *` wildcard import pollutes namespace
- Fragile mainloop workaround wrapping `root.mainloop()` in a `while True` / `except UnicodeDecodeError` loop (lines 3216–3221)
- Commented-out UI elements (zoom buttons, efficiency displays) that should be removed or implemented
- Hardcoded Dropbox URL for help documentation
- Copyright year hardcoded to 2021

---

## Testable Logic in the Current Codebase

Despite being a monolith, there is significant testable logic. The key challenge is that all methods live on `coffeegrindsize_GUI`, which requires a tkinter root window to instantiate. The testing strategy must work around this.

### Pure Computational Methods (testable directly or with minimal GUI mocking)

These methods perform math/science with numpy arrays and have no side effects beyond return values:

| Method | Lines | What it does | Test approach |
|--------|-------|-------------|---------------|
| `smooth(x, window_size)` | 2427–2429 | Moving average convolution | Pure function — direct unit test |
| `weighted_stddev(data, weights, ...)` | 2730–2756 | Weighted standard deviation with bias correction | Pure function — direct unit test |
| `attainable_mass_simulate(volumes)` | 2023–2035 | Simulates extractable mass from particle volumes | Pure function — direct unit test |
| `ey_simulate(surfaces)` | 2038–2044 | Extraction yield from particle surfaces | Pure function — direct unit test |
| `lighter(color, percent)` | 2721–2726 | Lightens an RGB color toward white | Pure function — direct unit test |
| `points_along_polygon(X, Y, X_poly, Y_poly)` | 1987–2020 | Finds points near polygon edges (geometry) | Pure function — direct unit test |
| `quick_cluster(xlist, ylist, xstart, ystart)` | 2432–2496 | Flood-fill neighbor clustering | Pure function — direct unit test |

### Complex Analysis Methods (testable with synthetic image data)

| Method | Lines | What it does | Test approach |
|--------|-------|-------------|---------------|
| `threshold_image()` | 1862–1984 | Blue-channel thresholding, polygon masking | Build synthetic PIL image + mock GUI state |
| `launch_psd()` | 2046–2354 | Full particle detection pipeline | Build pre-thresholded state + mock GUI |
| `refresh_cluster_data()` | 2357–2424 | Extracts arrays from cluster dicts, builds outline image | Provide cluster_data list + mock GUI |
| `update_statistics()` | 2758–2826 | Computes diameter/surface/volume/EY stats | Provide cluster arrays + mock GUI vars |
| `psd_hist_from_data()` | 2498–2718 | Generates histogram with error bars | Provide cluster arrays + mock matplotlib |

### I/O Methods (testable with temp files)

| Method | Lines | What it does | Test approach |
|--------|-------|-------------|---------------|
| `load_data()` | ~2999 | Loads CSV particle data | Temp CSV files |
| `save_data()` | ~3050+ | Exports analysis to CSV | Temp dir, verify output |
| `load_comparison_data()` | ~3050+ | Loads second dataset for overlay | Temp CSV files |

### GUI-Only Methods (low-priority for testing)

Mouse handlers (`motion`, `move_start`, `move_move`, `line_start`, `line_move`), display switching (`change_display_type`, `redraw`), widget builders (`label_entry`, `dropdown_entry`), and zoom logic. These would need a full tkinter test harness and offer less value per test.

### Module-Level Constants & Defaults

The `reference_objects_dict`, default parameters, and `Comparison` class (lines 28–96) are testable as-is without any GUI.

---

## Modernization Roadmap

### Phase 0: Local Fork (Prerequisite)

**Goal:** Create a safe working copy before any modifications.

1. **Fork the repository** to your own GitHub account (if working from an upstream repo)
2. **Clone locally** to a fresh working directory
3. **Create a dedicated branch** for modernization work (e.g., `modernization` or `phase-1-testing`)
4. **Verify the app builds and runs** from the clean clone before making changes
5. **Document the original state** — note the exact commit hash and any environment-specific quirks

This ensures:
- Original code is preserved as a reference
- Changes can be easily compared via `git diff`
- Mistakes can be rolled back without risk
- Multiple developers can collaborate on the modernization

**Estimated effort:** 30 minutes

---

### Phase 1: Comprehensive Testing (High effort, highest value)

**Goal:** Build a safety net that locks in current behavior before any code changes. Every subsequent phase is validated against these tests.

#### 1a. Project scaffolding for testing (day 1)

Minimal infrastructure to enable `pytest` — no changes to application code.

- Add `pyproject.toml` with `[project]` (Python ≥3.10, dependencies) and `[tool.pytest.ini_options]`
- Add `.gitignore` (`.DS_Store`, `__pycache__`, `*.pyc`, `.env`, `App/venv/`, `App/dist/`, `.trees/`, etc.)
- Create `tests/` directory structure:
  ```
  tests/
  ├── conftest.py              # Shared fixtures (synthetic images, mock GUI)
  ├── fixtures/                # Small test images, sample CSVs
  ├── test_pure_functions.py   # smooth, weighted_stddev, attainable_mass, etc.
  ├── test_geometry.py         # points_along_polygon, quick_cluster
  ├── test_threshold.py        # threshold_image with synthetic data
  ├── test_particle_detection.py  # launch_psd end-to-end with synthetic images
  ├── test_statistics.py       # update_statistics, psd_hist_from_data
  ├── test_io.py               # load_data, save_data round-trip
  ├── test_defaults.py         # Constants, reference_objects_dict, Comparison class
  └── test_build_tools.py      # fix_info_plist.py, fix_heat_wxs.py
  ```

#### 1b. Pure function tests (days 1–2)

Start with the easiest wins — functions that take numpy arrays and return values:

- **`smooth()`**: Verify moving average on known sequences, edge cases (window > data length)
- **`weighted_stddev()`**: Compare against manual calculations; test both `frequency=True/False` and `unbiased=True/False` modes; verify the bias correction formula
- **`attainable_mass_simulate()`**: Known volume inputs → verify depth_limit=0.1mm cutoff behavior, boundary (radius exactly at depth_limit), large/small particles
- **`ey_simulate()`**: Known surface inputs → verify extraction yield formula with k_reference=0.25014 and extraction_limit=0.3
- **`lighter()`**: RGB tuples → verify blending toward white at 0%, 50%, 100%

#### 1c. Geometry & clustering tests (days 2–3)

- **`points_along_polygon()`**: Construct simple polygons (square, triangle), scatter known points, verify which are detected as edge-adjacent. Test with points exactly on edges vs. far away.
- **`quick_cluster()`**: Build small grids of pixel coordinates with known clusters (e.g., two separated blobs, one connected blob, L-shaped cluster). Verify correct flood-fill grouping. Test single-pixel cluster, adjacent-diagonal rejection (uses Manhattan distance ≤ 1.001).

#### 1d. GUI mock fixtures (day 3)

Create a `conftest.py` fixture that builds a minimal `coffeegrindsize_GUI` instance by:
1. Creating a tkinter `Tk()` root (hidden with `withdraw()`)
2. Instantiating `coffeegrindsize_GUI(root)`
3. Providing helper methods to inject synthetic image data and pre-set GUI variables
4. Tearing down cleanly after each test

Alternatively, for methods that only read `self.*` attributes, create a lightweight mock/stub that provides just the needed attributes without full GUI initialization.

#### 1e. Thresholding tests (days 3–4)

Using synthetic PIL images (solid colors, gradients, known patterns):
- Verify `threshold_image()` correctly identifies dark pixels in the blue channel
- Test with and without an analysis polygon region
- Verify `background_median` calculation
- Test edge case: polygon with no pixels inside
- Verify thresholded fraction calculation

#### 1f. Particle detection integration tests (days 4–5)

Using synthetic images with known particle arrangements:
- **Single particle**: One dark circle on white background → verify 1 cluster detected with correct approximate diameter
- **Multiple separated particles**: Two circles far apart → verify 2 clusters
- **Adjacent particles**: Two circles touching → verify cluster-breaking cost function separates them (or not, depending on `maxcost`)
- **Edge rejection**: Particle at image boundary → verify it's excluded
- **Minimum surface filter**: Tiny particle below `min_surface` → verify it's skipped
- **Roundness filter**: Elongated shape below `min_roundness` → verify it's skipped
- **Quick mode vs. full mode**: Same image, `quick_var=0` vs `quick_var=1` → verify quick mode skips the cost-based cluster breaking

#### 1g. Statistics & histogram tests (day 5)

- **`update_statistics()`**: Provide known cluster arrays with a known pixel_scale → verify computed averages and standard deviations match hand calculations
- **`psd_hist_from_data()`**: Verify histogram bin edges and weights for each histogram type (number/mass/surface vs diameter/surface/volume). Use `matplotlib.pyplot.close()` cleanup.
- **CSV round-trip**: `save_data()` then `load_data()` → verify cluster data survives serialization

#### 1h. Build tools tests (day 5–6)

- **`fix_info_plist.py`**: Create a temp Info.plist, run the script, verify version/copyright/dark-mode keys are injected
- **`fix_heat_wxs.py`**: Create a minimal heat.wxs XML, run the script, verify output structure
- **`dmgbuild_settings.py`**: Verify it loads without error when version.txt exists

#### 1i. Snapshot/golden-file tests (day 6)

For the most critical scientific outputs, create "golden" reference data:
- Process a small test image through the full pipeline (threshold → PSD → statistics)
- Save the resulting cluster data CSV and statistics as reference files in `tests/fixtures/`
- Write a test that reruns the pipeline and asserts numerical equality (within floating-point tolerance)
- These golden tests are the ultimate regression guard for all future phases

**Estimated effort for Phase 1: 5–7 days**

---

### Phase 2: Housekeeping (Low effort, validated by Phase 1 tests)

**Goal:** Clean up code without changing behavior. Run the full test suite after each change.

1. **Remove dead code** — pdb imports (lines 24–26, 1670), commented-out UI blocks (lines 403–408, 508–526), unused `App/setup.py`
2. **Fix bare excepts** — replace with specific exception types (`ValueError`, `FileNotFoundError`, etc.) at lines ~2068, 2770, 2999, 3005
3. **Fix wildcard import** — replace `from tkinter import *` with explicit imports
4. **Fix the mainloop hack** (lines 3216–3221) — investigate UnicodeDecodeError root cause on modern macOS/Python
5. **Add linting** — configure ruff; add a pre-commit config
6. **Run full test suite after each change** to confirm no regressions

**Estimated effort:** 1–2 days

---

### Phase 3: Restructure (Medium effort, validated by Phase 1 tests)

**Goal:** Break the monolith into maintainable modules. Tests verify nothing breaks.

Suggested package structure:
```
coffeegrindsize/
├── __main__.py            # Entry point
├── app.py                 # GUI shell, window setup
├── ui/
│   ├── toolbar.py         # Toolbar and controls
│   ├── canvas.py          # Image display and interaction
│   ├── dialogs.py         # File dialogs, settings
│   └── histogram.py       # Histogram display panel
├── analysis/
│   ├── threshold.py       # Image thresholding
│   ├── clustering.py      # Particle detection and clustering
│   ├── statistics.py      # PSD calculations, extraction yield
│   └── scaling.py         # Pixel-to-physical unit conversion
├── models/
│   ├── particle.py        # Particle data model
│   └── comparison.py      # Comparison data model
├── io/
│   ├── image_loader.py    # Image loading and preprocessing
│   └── csv_export.py      # Data export
└── config.py              # Configuration management (replace hardcoded defaults)
```

**Approach:** Extract one module at a time. After each extraction:
1. Move the function(s) to the new module
2. Update imports in `coffeegrindsize.py` to delegate to the new module
3. Run the full test suite
4. Update test imports if needed

The golden-file tests from Phase 1i are the ultimate check — if the end-to-end numerical output doesn't change, the refactor is safe.

**Estimated effort:** 3–5 days

---

### Phase 4: Python & Dependency Modernization (Medium effort)

**Goal:** Run on current Python with current libraries.

1. **Target Python 3.10+** — verify all numpy/scipy/matplotlib/Pillow APIs still work
2. **Fix deprecated calls** — e.g., `np.fromstring` → `np.frombuffer` (line 2972), `Image.ANTIALIAS` → `Image.LANCZOS` (line 1767)
3. **Add type hints** incrementally — start with the extracted analysis modules
4. **Update PyInstaller configuration** and build_tools scripts
5. **Run full test suite** to catch any behavioral changes from API updates

**Estimated effort:** 2–3 days

---

### Phase 5: CI/CD Pipeline (Low-medium effort)

**Goal:** Automate testing and builds.

1. **GitHub Actions workflow** — run lint + tests on every push/PR
2. **Matrix testing** — Python 3.10, 3.11, 3.12 on macOS and Ubuntu
3. **Automated installer builds** — build macOS DMG and Windows MSI on tagged releases
4. **Remove `App/` directory** from version control — built artifacts should come from CI, not the repo

**Estimated effort:** 2–3 days

---

### Phase 6: UX Modernization (High effort, optional)

**Goal:** Modern look and feel.

| Option | Effort | Notes |
|--------|--------|-------|
| **tkinter + sv_ttk** | 1–2 days | Minimal code changes, adds Sun Valley theme. Easiest win. |
| **CustomTkinter** | 3–5 days | Modern-looking tkinter wrapper. Requires rewriting widgets. |
| **Web-based (Streamlit/Gradio)** | 1–2 weeks | Complete UI rewrite. Enables browser-based use. |
| **Qt (PySide6/PyQt6)** | 2–3 weeks | Full UI rewrite. Professional desktop look. |

**Recommendation:** Start with sv_ttk for an immediate visual refresh with minimal risk.

---

## Effort Summary

| Phase | Effort | Priority | Depends on |
|-------|--------|----------|------------|
| 0. Local fork | 30 minutes | **Required — do first** | Nothing |
| 1. Comprehensive testing | 5–7 days | **Highest** | Phase 0 |
| 2. Housekeeping | 1–2 days | High | Phase 1 |
| 3. Restructure | 3–5 days | High | Phase 1 |
| 4. Python modernization | 2–3 days | Medium | Phase 1 |
| 5. CI/CD | 2–3 days | Medium | Phase 1 |
| 6. UX modernization | 1 day – 3 weeks | Low | Phases 2–3 |

**Total for Phases 0–5:** ~3–4 weeks of focused work
**Total including Phase 6 (minimal UX):** ~3.5–4.5 weeks
**Total including Phase 6 (full rewrite):** ~6–7 weeks

---

## Risks & Considerations

- **GUI dependency for testing.** The monolithic class requires a tkinter root to instantiate. The `conftest.py` fixture must handle this carefully — `Tk()` with `withdraw()`, or mock objects for pure-computation tests. On headless CI, `xvfb` may be needed.
- **Scientific accuracy is the core value.** The clustering and PSD algorithms must be preserved exactly. Golden-file snapshot tests are the primary guard here. Any change that alters numerical output must be deliberate and documented.
- **`weighted_stddev()` mutates its input.** Line 2742 normalizes the `weights` array in-place (`weights /= np.nansum(weights)`). This is a latent bug — if the caller reuses the array, values are corrupted. Tests should document this behavior and Phase 2 should fix it.
- **Cross-platform builds.** The build tooling is fragile and environment-dependent (hardcoded `$GITHUB` paths, platform-specific scripts). Phase 5 addresses this.
- **User base.** If active users exist, backward compatibility of CSV output format matters. The CSV round-trip tests in Phase 1g protect this.
- **The `App/` directory** contains a pre-built macOS .app bundle with a Python 3.7 venv. Should be removed from version control and produced via CI instead.
