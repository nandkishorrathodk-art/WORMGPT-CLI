#!/usr/bin/env python3
"""Test TUI imports and basic functionality."""

try:
    from textual.app import App

    print("OK - Textual imported successfully")

    from tui_main import WormGPTHiveTUI

    print("OK - WormGPTHiveTUI imported successfully")

    print("\nAll imports successful! TUI is ready to run.")
    print("To launch: venv\\Scripts\\python.exe tui_main.py")

except ImportError as e:
    print(f"ERROR - Import error: {e}")
except Exception as e:
    print(f"ERROR - {e}")
