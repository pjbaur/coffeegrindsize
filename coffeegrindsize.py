"""Compatibility shim for the Coffee Grind Size Analyzer package."""

from coffeegrindsize import *  # noqa: F403
from coffeegrindsize.ui.app import main

if __name__ == "__main__":
    main()
