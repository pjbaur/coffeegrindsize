# Coffee Grind Size Analyzer

Desktop application for analyzing coffee grind particle sizes from images. Detects particles, measures sizes, and produces particle size distribution (PSD) histograms.

**Original author:** Jonathan Gagné (MIT License, 2018)
**Fork purpose:** Modernization of the codebase

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.10+.

## Running

```bash
python coffeegrindsize.py
```

## Testing

```bash
pytest -v                    # Run all 43 tests
pytest --cov=coffeegrindsize # Coverage report
ruff check .                 # Lint
```

## Modernization Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project infrastructure (`pyproject.toml`, `.gitignore`, `tests/`) | Done |
| 1 | Comprehensive test suite (43 tests) | Done |
| 2 | Code cleanup (pdb removal, bare excepts, wildcard imports, mutation bug) | Done |
| 3 | Module restructuring (extract analysis, io, ui modules) | Pending |
| 4 | Python 3.10+ modernization (deprecated APIs, type hints) | Pending |
| 5 | CI/CD pipeline (GitHub Actions) | Pending |
| 6 | Optional UX modernization | Pending |

See `IMPLEMENTATION_PLAN.md` for the detailed roadmap and `MODERNIZATION_ASSESSMENT.md` for the full analysis.

## Project Structure

```
coffeegrindsize.py          # Main application (monolithic, to be refactored in Phase 3)
tests/                      # Test suite
  conftest.py               # Shared fixtures (tk_root, gui, synthetic images)
  test_pure_functions.py    # smooth, weighted_stddev, attainable_mass, ey_simulate, lighter
  test_geometry.py          # points_along_polygon
  test_clustering.py        # quick_cluster
  test_threshold.py         # threshold_image
  test_particle_detection.py
  test_statistics.py        # update_statistics
  test_io.py                # save_data/load_data round-trip
  test_defaults.py          # Module constants
  test_snapshot.py          # Golden-file regression test
pyproject.toml              # Build config, dependencies, tool settings
```

## Dependencies

- numpy, scipy — numerical computations
- matplotlib — plotting (TkAgg backend)
- Pillow (PIL) — image processing
- pandas — data I/O

## License

MIT License. See `LICENSE` file.
