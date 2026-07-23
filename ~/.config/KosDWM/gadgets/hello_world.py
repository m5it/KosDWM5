#!/usr/bin/env python3
"""
KosDWM Gadget Example - Hello World
====================================

This is an example gadget script for KosDWM.
"""

import sys
import os
from pathlib import Path

def find_kosdwm_path():
    """Find the KosDWM installation directory."""
    if 'KOSDWM_HOME' in os.environ:
        path = Path(os.environ['KOSDWM_HOME'])
        if path.exists():
            return path
    
    config_path = Path.home() / ".config" / "KosDWM" / "kosdwm_path.conf"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                path = Path(f.read().strip())
                if path.exists():
                    return path
        except:
            pass
    
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
    
    gadget_dir = Path(__file__).parent
    kosdwm_path = gadget_dir.parent
    
    if (kosdwm_path / "src").exists():
        return kosdwm_path
    
    raise RuntimeError("Could not find KosDWM installation.")

KOSDWM_PATH = find_kosdwm_path()
sys.path.insert(0, str(KOSDWM_PATH / "src"))

from gadgets import GadgetBase
import tkinter as tk


class HelloWorldGadget(GadgetBase):
    """A simple example gadget that shows a hello message when clicked."""
    
    def __init__(self):
        super().__init__()
        self.click_count = 0
    
    def get_name(self) -> str:
        return "hello_world"
    
    def get_icon(self) -> str:
        return "👋"
    
    def get_tooltip(self) -> str:
        return "Click to say hello!"
    
    def get_description(self) -> str:
        return "A simple example gadget that shows a greeting message."
    
    def on_click(self, event=None):
        self.click_count += 1
        window = tk.Toplevel()
        window.title("Hello from KosDWM!")
        window.geometry("300x150")
        window.transient()
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (300 // 2)
        y = (window.winfo_screenheight() // 2) - (150 // 2)
        window.geometry(f'+{x}+{y}')
        
        tk.Label(
            window,
            text=f"Hello World!\n\nYou've clicked this gadget {self.click_count} time(s).",
            font=('Arial', 14),
            pady=20
        ).pack()
        
        tk.Button(
            window,
            text="OK",
            command=window.destroy,
            width=10
        ).pack(pady=10)
        
        return True


gadget = HelloWorldGadget()
