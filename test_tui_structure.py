#!/usr/bin/env python3
"""Test TUI structure and components."""

import os
os.environ["OPENROUTER_API_KEY"] = "test_key"

from tui_main import WormGPTHiveTUI, HumanFeedbackDialog, MissionHistoryScreen

def test_tui_structure():
    """Test that TUI app can be instantiated."""
    try:
        app = WormGPTHiveTUI()
        print("OK - WormGPTHiveTUI instantiated")
        
        assert hasattr(app, 'CSS_PATH'), "Missing CSS_PATH"
        assert app.CSS_PATH == "main.css", "CSS_PATH incorrect"
        print("OK - CSS_PATH configured correctly")
        
        assert hasattr(app, 'BINDINGS'), "Missing BINDINGS"
        print("OK - Key bindings defined")
        
        dialog = HumanFeedbackDialog("Test question?")
        print("OK - HumanFeedbackDialog instantiated")
        
        print("\nAll TUI structure tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR - {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tui_structure()
    exit(0 if success else 1)
