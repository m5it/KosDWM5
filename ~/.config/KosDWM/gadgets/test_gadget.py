#!/usr/bin/env python3
"""
Test Gadget for KosDWM
======================

A simple test gadget to verify the dynamic loading system works.
"""

import sys
import os
from pathlib import Path

def find_kosdwm_path():
    """
    Find the KosDWM installation directory.
    """
    # 1. Check environment variable
    if 'KOSDWM_HOME' in os.environ:
        path = Path(os.environ['KOSDWM_HOME'])
        if path.exists():
            return path
    
    # 2. Check config file
    config_path = Path.home() / ".config" / "KosDWM" / "kosdwm_path.conf"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                path = Path(f.read().strip())
                if path.exists():
                    return path
        except:
            pass
    
    # 3. Try common locations
    common_paths = [
        Path.home() / "Projects" / "KosDWM",
        Path.home() / "workspace" / "KosDWM",
        Path.home() / "code" / "KosDWM",
        Path.home() / "KosDWM",
        Path("/opt/KosDWM"),
        Path("/usr/local/share/KosDWM"),
    ]
    
    for path in common_paths:
        if (path / "src").exists():
            return path
    
    # 4. Fallback
    gadget_dir = Path(__file__).parent
    kosdwm_path = gadget_dir.parent
    
    if (kosdwm_path / "src").exists():
        return kosdwm_path
    
    raise RuntimeError("Could not find KosDWM installation.")

# Add KosDWM to Python path
KOSDWM_PATH = find_kosdwm_path()
sys.path.insert(0, str(KOSDWM_PATH / "src"))

from gadgets import GadgetBase
from tkinter import messagebox


class TestGadget(GadgetBase):
    """
    A simple test gadget to verify the gadget system works.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_name(self) -> str:
        return "test_gadget"
    
    def get_icon(self) -> str:
        return "🧪"
    
    def get_tooltip(self) -> str:
        return "Click to test the gadget system"
    
    def get_description(self) -> str:
        return "A test gadget to verify KosDWM gadget loading works correctly."
    
    def on_click(self, event=None):
        messagebox.showinfo(
            "Test Gadget",
            "Gadget system is working!\n\n"
            f"KOSDWM_HOME: {KOSDWM_PATH}\n"
            "Python path includes: src/"
        )
        return True


# Create instance
gadget = TestGadget()
