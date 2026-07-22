"""
Malformed Gadget - Testing Error Handling
This gadget is intentionally broken to test error handling.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gadgets import GadgetBase


# This class doesn't properly extend GadgetBase
class MalformedGadget:
    """A malformed gadget missing required methods."""
    
    def get_name(self):
        return "malformed"
    
    # Missing get_icon(), on_click(), get_tooltip()
