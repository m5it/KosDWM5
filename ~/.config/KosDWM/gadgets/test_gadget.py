"""
Test Gadget for KosDWM
======================

A simple test gadget to verify the dynamic loading system works.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gadgets import GadgetBase
from tkinter import messagebox


class TestGadget(GadgetBase):
    """A test gadget to verify the loading system."""
    
    def __init__(self):
        super().__init__()
        self.test_value = 42
    
    def get_name(self) -> str:
        return "test_gadget"
    
    def get_icon(self) -> str:
        return "TEST"
    
    def get_tooltip(self) -> str:
        return "Test gadget - click to verify loading works"
    
    def get_description(self) -> str:
        return "A test gadget to verify the dynamic loading system works correctly."
    
    def on_click(self, event=None):
        """Show test message."""
        messagebox.showinfo(
            "Test Gadget", 
            f"Dynamic loading works!\nTest value: {self.test_value}\n\n"
            "If you see this message, the gadget system is functioning correctly."
        )
