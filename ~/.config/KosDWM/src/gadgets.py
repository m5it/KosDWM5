"""
KosDWM Gadget System
Provides a pluggable gadget framework for the panel.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import sys
import importlib.util
import inspect
from pathlib import Path
from abc import ABC, abstractmethod

# Import version
try:
    from version import get_version, get_version_info
    VERSION = get_version()
except ImportError:
    VERSION = "unknown"


class GadgetBase(ABC):
    """
    Abstract base class for all KosDWM gadgets.
    Gadgets are small interactive elements displayed on the panel.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name/identifier of the gadget."""
        pass
    
    @abstractmethod
    def get_icon(self) -> str:
        """Return the text/icon to display on the gadget button."""
        pass
    
    @abstractmethod
    def on_click(self, event=None):
        """Handle click event on the gadget."""
        pass
    
    @abstractmethod
    def get_tooltip(self) -> str:
        """Return tooltip text for the gadget."""
        pass
    
    def get_description(self) -> str:
        """Return a longer description for configuration dialogs."""
        return self.get_tooltip()


class HelloWorldGadget(GadgetBase):
    """
    Example gadget that displays a Hello World message when clicked.
    """
    
    def __init__(self):
        self.click_count = 0
    
    def get_name(self) -> str:
        return "hello_world"
    
    def get_icon(self) -> str:
        return "Hello"
    
    def get_tooltip(self) -> str:
        return "Click to see Hello World message"
    
    def get_description(self) -> str:
        return f"A simple example gadget. KosDWM v{VERSION}"
    
    def on_click(self, event=None):
        self.click_count += 1
        messagebox.showinfo(
            "Hello World",
            f"Hello from KosDWM v{VERSION}!\n\nClicked {self.click_count} time(s)."
        )


class GadgetManager:
    """
    Manages discovery, loading, and configuration of gadgets.
    """
    
    GADGETS_DIR = Path.home() / ".config" / "KosDWM" / "gadgets"
    CONFIG_FILE = Path.home() / ".config" / "KosDWM" / "gadgets_config.json"
    
    def __init__(self):
        self.gadgets = {}
        self.enabled = set()
        self._ensure_directories()
        self._load_config()
    
    def _ensure_directories(self):
        """Ensure gadget directories exist."""
        self.GADGETS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load gadget configuration."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.enabled = set(config.get('enabled', []))
            except (json.JSONDecodeError, IOError):
                self.enabled = set()
    
    def _save_config(self):
        """Save gadget configuration."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump({'enabled': list(self.enabled)}, f, indent=2)
        except IOError as e:
            print(f"Error saving gadget config: {e}")
    
    def discover_gadgets(self):
        """Discover available gadgets."""
        self.gadgets = {}
        
        # Add built-in gadgets
        self.gadgets['hello_world'] = HelloWorldGadget()
        
        # Discover from gadgets directory
        if self.GADGETS_DIR.exists():
            for file_path in self.GADGETS_DIR.glob("*.py"):
                if file_path.name.startswith('_'):
                    continue
                
                try:
                    gadget = self._load_gadget(file_path)
                    if gadget:
                        self.gadgets[gadget.get_name()] = gadget
                except Exception as e:
                    print(f"Error loading gadget {file_path}: {e}")
        
        return self.gadgets
    
    def _load_gadget(self, file_path):
        """Load a gadget from a Python file."""
        module_name = f"gadget_{file_path.stem}"
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        
        # Add KosDWM src to path for imports
        kosdwm_src = Path(__file__).parent
        if str(kosdwm_src) not in sys.path:
            sys.path.insert(0, str(kosdwm_src))
        
        spec.loader.exec_module(module)
        
        # Find GadgetBase subclasses
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, GadgetBase) and 
                obj is not GadgetBase and
                not name.startswith('_')):
                return obj()
        
        return None
    
    def get_enabled_gadgets(self):
        """Get list of enabled gadgets."""
        return [self.gadgets[name] for name in self.enabled if name in self.gadgets]
    
    def enable_gadget(self, name):
        """Enable a gadget."""
        if name in self.gadgets:
            self.enabled.add(name)
            self._save_config()
    
    def disable_gadget(self, name):
        """Disable a gadget."""
        self.enabled.discard(name)
        self._save_config()
    
    def is_enabled(self, name):
        """Check if a gadget is enabled."""
        return name in self.enabled
    
    def get_version(self):
        """Get KosDWM version."""
        return VERSION


class GadgetConfigurationDialog:
    """
    Dialog for configuring which gadgets are enabled.
    """
    
    def __init__(self, parent, gadget_manager):
        self.gadget_manager = gadget_manager
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Gadget Configuration - KosDWM v{VERSION}")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_ui()
        
        parent.wait_window(self.dialog)
    
    def _create_ui(self):
        """Create the dialog UI."""
        # Header
        header = tk.Frame(self.dialog, padx=10, pady=10)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=f"⚙️ Gadget Configuration",
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header,
            text=f"v{VERSION}",
            font=('Arial', 10),
            fg='gray'
        ).pack(side=tk.RIGHT)
        
        # Gadget list
        list_frame = tk.Frame(self.dialog, padx=10, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(list_frame)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add gadget entries
        gadgets = self.gadget_manager.discover_gadgets()
        
        self.var_map = {}
        for name, gadget in sorted(gadgets.items()):
            frame = tk.Frame(scrollable_frame, pady=5)
            frame.pack(fill=tk.X, padx=5)
            
            var = tk.BooleanVar(value=self.gadget_manager.is_enabled(name))
            self.var_map[name] = var
            
            cb = tk.Checkbutton(frame, variable=var)
            cb.pack(side=tk.LEFT)
            
            tk.Label(
                frame,
                text=gadget.get_icon(),
                font=('Arial', 12),
                width=3
            ).pack(side=tk.LEFT)
            
            info_frame = tk.Frame(frame)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            tk.Label(
                info_frame,
                text=name,
                font=('Arial', 10, 'bold'),
                anchor='w'
            ).pack(fill=tk.X)
            
            tk.Label(
                info_frame,
                text=gadget.get_description(),
                font=('Arial', 9),
                fg='gray',
                anchor='w',
                wraplength=300
            ).pack(fill=tk.X)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, padx=10, pady=10)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(
            btn_frame,
            text="Reload Gadgets",
            command=self._reload
        ).pack(side=tk.LEFT)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Save",
            command=self._save,
            bg='#4a90d9',
            fg='white',
            width=10
        ).pack(side=tk.RIGHT)
    
    def _reload(self):
        """Reload gadgets from disk."""
        self.gadget_manager.discover_gadgets()
        messagebox.showinfo("Reload", "Gadgets reloaded!")
        self.dialog.destroy()
        self.result = True
    
    def _save(self):
        """Save configuration."""
        for name, var in self.var_map.items():
            if var.get():
                self.gadget_manager.enable_gadget(name)
            else:
                self.gadget_manager.disable_gadget(name)
        
        self.dialog.destroy()
        self.result = True
