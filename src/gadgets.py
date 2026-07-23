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

# Import version from AUTOVERSION.py
try:
    # Try to import from parent directory (where AUTOVERSION.py is)
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from AUTOVERSION import VERSION as KOSDWM_VERSION
except ImportError:
    KOSDWM_VERSION = "unknown"


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
    
    def get_name(self) -> str:
        return "hello_world"
    
    def get_icon(self) -> str:
        return "Hello"
    
    def get_tooltip(self) -> str:
        return "Click to see Hello World message"
    
    def get_description(self) -> str:
        return f"A simple example gadget. KosDWM v{KOSDWM_VERSION}"
    
    def on_click(self, event=None):
        """Show Hello World alert when clicked."""
        messagebox.showinfo(
            "Hello World", 
            f"Hello from KosDWM v{KOSDWM_VERSION}!\n\nClick to continue."
        )


class GadgetManager:
    """
    Manages gadget registration, configuration, and instantiation.
    """
    
    def __init__(self):
        self._available_gadgets = {}
        self._gadget_sources = {}
        self._load_errors = []
        self._enabled_gadgets = set()
        self._config_path = Path.home() / ".config" / "KosDWM" / "gadgets.json"
        self._gadgets_dir = Path.home() / ".config" / "KosDWM" / "gadgets"
        
        self._ensure_gadgets_dir()
        self._register_builtin_gadgets()
        self._discover_gadgets()
        self._load_config()
    
    def _ensure_gadgets_dir(self):
        """Create the gadgets directory if it doesn't exist."""
        try:
            self._gadgets_dir.mkdir(parents=True, exist_ok=True)
        except IOError as e:
            print(f"Error creating gadgets directory: {e}")
    
    def _register_builtin_gadgets(self):
        """Register all built-in gadget classes."""
        self.register_gadget(HelloWorldGadget, source="built-in")
    
    def _discover_gadgets(self):
        """Discover and load gadgets from the gadgets directory."""
        self._load_errors.clear()
        
        if not self._gadgets_dir.exists():
            return
        
        py_files = [f for f in self._gadgets_dir.iterdir() 
                    if f.is_file() and f.suffix == '.py' and not f.name.startswith('_')]
        
        for py_file in py_files:
            self._load_gadget_module(py_file)
    
    def _load_gadget_module(self, file_path: Path):
        """Load a gadget module from a file path."""
        try:
            module_name = f"gadget_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return
            
            module = importlib.util.module_from_spec(spec)
            
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            if str(self._gadgets_dir) not in sys.path:
                sys.path.insert(0, str(self._gadgets_dir))
            
            spec.loader.exec_module(module)
            gadget_classes = self._find_gadget_classes(module)
            
            for gadget_class in gadget_classes:
                try:
                    self.register_gadget(gadget_class, source=str(file_path))
                except ValueError:
                    pass
                    
        except Exception as e:
            self._load_errors.append(f"Error loading {file_path.name}: {str(e)}")
    
    def _find_gadget_classes(self, module):
        """Find all GadgetBase subclasses in a module."""
        classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, GadgetBase) and 
                obj is not GadgetBase and
                obj.__module__ == module.__name__):
                classes.append(obj)
        return classes
    
    def register_gadget(self, gadget_class, source="unknown"):
        """Register a new gadget class."""
        if not issubclass(gadget_class, GadgetBase):
            raise ValueError(f"Gadget class must extend GadgetBase: {gadget_class}")
        
        temp_instance = gadget_class()
        name = temp_instance.get_name()
        
        self._available_gadgets[name] = gadget_class
        self._gadget_sources[name] = source
    
    def get_gadget_source(self, gadget_name: str) -> str:
        """Get the source of a gadget."""
        return self._gadget_sources.get(gadget_name, "unknown")
    
    def get_load_errors(self) -> list:
        """Get list of errors that occurred during gadget loading."""
        return self._load_errors.copy()
    
    def reload_gadgets(self):
        """Reload all gadgets from disk."""
        built_ins = {name: cls for name, cls in self._available_gadgets.items() 
                     if self._gadget_sources.get(name) == "built-in"}
        
        self._available_gadgets = built_ins.copy()
        self._gadget_sources = {name: src for name, src in self._gadget_sources.items() 
                               if src == "built-in"}
        
        self._load_errors.clear()
        self._discover_gadgets()
        
        self._enabled_gadgets = {name for name in self._enabled_gadgets 
                                if name in self._available_gadgets}
        self._save_config()
    
    def enable_gadget(self, gadget_name: str):
        """Enable a gadget by name."""
        if gadget_name in self._available_gadgets:
            self._enabled_gadgets.add(gadget_name)
            self._save_config()
    
    def disable_gadget(self, gadget_name: str):
        """Disable a gadget by name."""
        self._enabled_gadgets.discard(gadget_name)
        self._save_config()
    
    def is_enabled(self, gadget_name: str) -> bool:
        """Check if a gadget is enabled."""
        return gadget_name in self._enabled_gadgets
    
    def get_available_gadgets(self) -> list:
        """Get list of all available gadget names."""
        return list(self._available_gadgets.keys())
    
    def get_enabled_gadgets(self) -> list:
        """Get instances of all enabled gadgets."""
        gadgets = []
        for name in self._enabled_gadgets:
            if name in self._available_gadgets:
                gadget_class = self._available_gadgets[name]
                gadgets.append(gadget_class())
        return gadgets
    
    def get_gadget_info(self, gadget_name: str) -> dict:
        """Get information about a gadget."""
        if gadget_name not in self._available_gadgets:
            return None
        
        gadget_class = self._available_gadgets[gadget_name]
        instance = gadget_class()
        source = self.get_gadget_source(gadget_name)
        
        if source == "built-in":
            source_display = "built-in"
            source_path = None
        else:
            source_display = "custom"
            source_path = source
        
        return {
            "name": instance.get_name(),
            "icon": instance.get_icon(),
            "tooltip": instance.get_tooltip(),
            "description": instance.get_description(),
            "enabled": self.is_enabled(gadget_name),
            "source": source_display,
            "source_path": source_path
        }
    
    def _load_config(self):
        """Load gadget configuration from file."""
        if not self._config_path.exists():
            self._enabled_gadgets = {"hello_world"}
            self._save_config()
            return
        
        try:
            with open(self._config_path, 'r') as f:
                config = json.load(f)
                self._enabled_gadgets = set(config.get("enabled", []))
        except (json.JSONDecodeError, IOError):
            self._enabled_gadgets = {"hello_world"}
    
    def _save_config(self):
        """Save gadget configuration to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {"enabled": list(self._enabled_gadgets)}
            with open(self._config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except IOError:
            pass


class GadgetConfigWindow:
    """
    Floating configuration window for enabling/disabling gadgets.
    Displays KosDWM version in the title bar.
    """
    
    def __init__(self, parent, gadget_manager, on_save_callback=None):
        self.parent = parent
        self.gadget_manager = gadget_manager
        self.on_save_callback = on_save_callback
        self.checkboxes = {}
        
        self._create_window()
    
    def _create_window(self):
        """Create the configuration window with version in title."""
        # Include version in window title
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Gadget Configuration - KosDWM v{KOSDWM_VERSION}")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Header with version
        header_frame = tk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame,
            text="⚙️ Configure Gadgets",
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT)
        
        # Version label on right
        tk.Label(
            header_frame,
            text=f"v{KOSDWM_VERSION}",
            font=('Arial', 9),
            fg='gray'
        ).pack(side=tk.RIGHT)
        
        # Description
        desc = tk.Label(
            self.window,
            text="Enable or disable gadgets to display on the panel:",
            wraplength=450,
            justify='left'
        )
        desc.pack(pady=(0, 5))
        
        # Scrollable frame for gadgets
        scroll_frame = tk.Frame(self.window)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(scroll_frame, height=180)
        scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        self.gadgets_frame = tk.Frame(canvas)
        
        self.gadgets_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.gadgets_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create checkbox for each available gadget
        self._create_gadget_checkboxes()
        
        # Errors section
        self._create_errors_section()
        
        # Separator
        separator = tk.Frame(self.window, height=2, bg='gray')
        separator.pack(fill=tk.X, padx=10, pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Reload button
        reload_btn = tk.Button(
            button_frame,
            text="Reload Gadgets",
            command=self._on_reload,
            width=12
        )
        reload_btn.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self._on_save,
            width=10
        )
        save_btn.pack(side=tk.RIGHT)
    
    def _create_gadget_checkboxes(self):
        """Create checkboxes for all available gadgets."""
        for widget in self.gadgets_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes.clear()
        
        available = self.gadget_manager.get_available_gadgets()
        
        if not available:
            no_gadgets = tk.Label(
                self.gadgets_frame,
                text="No gadgets available.",
                fg='gray'
            )
            no_gadgets.pack(pady=20)
            return
        
        for gadget_name in available:
            info = self.gadget_manager.get_gadget_info(gadget_name)
            if info is None:
                continue
            
            gadget_frame = tk.Frame(self.gadgets_frame)
            gadget_frame.pack(fill=tk.X, pady=3, anchor='w')
            
            source_text = info['source']
            source_label = tk.Label(
                gadget_frame,
                text=f"[{source_text}]",
                fg='blue' if source_text == 'built-in' else 'green',
                font=('Arial', 8),
                width=10
            )
            source_label.pack(side=tk.LEFT)
            
            var = tk.BooleanVar(value=info['enabled'])
            var.trace_add('write', lambda *args, name=gadget_name, v=var: 
                         self._on_toggle(name, v))
            self.checkboxes[gadget_name] = var
            
            cb = tk.Checkbutton(
                gadget_frame,
                text=info['name'],
                variable=var,
                font=('Arial', 10, 'bold')
            )
            cb.pack(side=tk.LEFT)
            
            desc_text = info['description']
            if len(desc_text) > 30:
                desc_text = desc_text[:27] + "..."
            desc_label = tk.Label(
                gadget_frame,
                text=desc_text,
                justify='left',
                fg='gray',
                font=('Arial', 8)
            )
            desc_label.pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_errors_section(self):
        """Create section to display load errors."""
        errors = self.gadget_manager.get_load_errors()
        
        if not errors:
            return
        
        error_frame = tk.LabelFrame(self.window, text="Load Errors", fg='red')
        error_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for error in errors[:3]:
            lbl = tk.Label(
                error_frame,
                text=f"• {error}",
                fg='red',
                font=('Arial', 8),
                wraplength=450,
                justify='left'
            )
            lbl.pack(anchor='w', padx=5, pady=1)
        
        if len(errors) > 3:
            more_lbl = tk.Label(
                error_frame,
                text=f"... and {len(errors) - 3} more errors",
                fg='red',
                font=('Arial', 8, 'italic')
            )
            more_lbl.pack(anchor='w', padx=5)
    
    def _on_toggle(self, gadget_name, var):
        """Handle immediate toggle of a gadget."""
        if var.get():
            self.gadget_manager.enable_gadget(gadget_name)
        else:
            self.gadget_manager.disable_gadget(gadget_name)
        
        if self.on_save_callback:
            self.on_save_callback()
    
    def _on_save(self):
        """Save configuration and close window."""
        self.window.destroy()
    
    def _on_reload(self):
        """Reload gadgets from disk and refresh the list."""
        self.gadget_manager.reload_gadgets()
        self._create_gadget_checkboxes()
        self._create_errors_section()
        
        if self.on_save_callback:
            self.on_save_callback()
    
    def _on_cancel(self):
        """Close window without saving."""
        self.window.destroy()
