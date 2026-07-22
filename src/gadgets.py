"""
KosDWM Gadget System
Provides a pluggable gadget framework for the panel.
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from pathlib import Path
from abc import ABC, abstractmethod


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
        return "A simple example gadget that shows a greeting message."
    
    def on_click(self, event=None):
        """Show Hello World alert when clicked."""
        messagebox.showinfo("Hello World", "Hello World!")


class GadgetManager:
    """
    Manages gadget registration, configuration, and instantiation.
    Loads and saves gadget configuration to ~/.config/KosDWM/gadgets.json
    """
    
    def __init__(self):
        self._available_gadgets = {}  # name -> gadget class
        self._enabled_gadgets = set()  # set of enabled gadget names
        self._config_path = Path.home() / ".config" / "KosDWM" / "gadgets.json"
        
        # Register built-in gadgets
        self._register_builtin_gadgets()
        
        # Load configuration
        self._load_config()
    
    def _register_builtin_gadgets(self):
        """Register all built-in gadget classes."""
        self.register_gadget(HelloWorldGadget)
    
    def register_gadget(self, gadget_class):
        """
        Register a new gadget class.
        
        Args:
            gadget_class: Class that extends GadgetBase
        """
        if not issubclass(gadget_class, GadgetBase):
            raise ValueError(f"Gadget class must extend GadgetBase: {gadget_class}")
        
        # Create temporary instance to get the name
        temp_instance = gadget_class()
        name = temp_instance.get_name()
        
        self._available_gadgets[name] = gadget_class
    
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
        """
        Get list of all available gadget names.
        
        Returns:
            List of gadget name strings
        """
        return list(self._available_gadgets.keys())
    
    def get_enabled_gadgets(self) -> list:
        """
        Get instances of all enabled gadgets.
        
        Returns:
            List of instantiated gadget objects
        """
        gadgets = []
        for name in self._enabled_gadgets:
            if name in self._available_gadgets:
                gadget_class = self._available_gadgets[name]
                gadgets.append(gadget_class())
        return gadgets
    
    def get_gadget_info(self, gadget_name: str) -> dict:
        """
        Get information about a gadget.
        
        Returns:
            Dict with name, description, icon, tooltip, enabled status
        """
        if gadget_name not in self._available_gadgets:
            return None
        
        gadget_class = self._available_gadgets[gadget_name]
        instance = gadget_class()
        
        return {
            "name": instance.get_name(),
            "icon": instance.get_icon(),
            "tooltip": instance.get_tooltip(),
            "description": instance.get_description(),
            "enabled": self.is_enabled(gadget_name)
        }
    
    def _load_config(self):
        """Load gadget configuration from file."""
        if not self._config_path.exists():
            # First run - enable hello_world by default
            self._enabled_gadgets = {"hello_world"}
            self._save_config()
            return
        
        try:
            with open(self._config_path, 'r') as f:
                config = json.load(f)
                self._enabled_gadgets = set(config.get("enabled", []))
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading gadget config: {e}, using defaults")
            self._enabled_gadgets = {"hello_world"}
    
    def _save_config(self):
        """Save gadget configuration to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {
                "enabled": list(self._enabled_gadgets)
            }
            with open(self._config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print(f"Error saving gadget config: {e}")


class GadgetConfigWindow:
    """
    Floating configuration window for enabling/disabling gadgets.
    """
    
    def __init__(self, parent, gadget_manager, on_save_callback=None):
        """
        Initialize the gadget configuration window.
        
        Args:
            parent: Parent tkinter widget
            gadget_manager: GadgetManager instance
            on_save_callback: Optional callback to call after saving
        """
        self.parent = parent
        self.gadget_manager = gadget_manager
        self.on_save_callback = on_save_callback
        self.checkboxes = {}  # gadget_name -> BooleanVar
        
        self._create_window()
    
    def _create_window(self):
        """Create the configuration window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gadget Configuration")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Header label
        header = tk.Label(
            self.window,
            text="Configure Gadgets",
            font=('Arial', 12, 'bold'),
            pady=10
        )
        header.pack()
        
        # Description
        desc = tk.Label(
            self.window,
            text="Enable or disable gadgets to display on the panel:",
            wraplength=380,
            justify='left'
        )
        desc.pack(pady=(0, 10))
        
        # Frame for gadget checkboxes
        self.gadgets_frame = tk.Frame(self.window)
        self.gadgets_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Create checkbox for each available gadget
        self._create_gadget_checkboxes()
        
        # Separator
        separator = tk.Frame(self.window, height=2, bg='gray')
        separator.pack(fill=tk.X, padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
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
            
            # Frame for each gadget
            gadget_frame = tk.Frame(self.gadgets_frame)
            gadget_frame.pack(fill=tk.X, pady=5)
            
            # Checkbox variable
            var = tk.BooleanVar(value=info['enabled'])
            self.checkboxes[gadget_name] = var
            
            # Checkbox
            cb = tk.Checkbutton(
                gadget_frame,
                text=info['name'],
                variable=var,
                font=('Arial', 10, 'bold')
            )
            cb.pack(anchor='w')
            
            # Description label
            desc_label = tk.Label(
                gadget_frame,
                text=info['description'],
                wraplength=340,
                justify='left',
                fg='gray',
                font=('Arial', 9)
            )
            desc_label.pack(anchor='w', padx=(20, 0))
    
    def _on_save(self):
        """Save configuration and close window."""
        # Update gadget manager with new settings
        for gadget_name, var in self.checkboxes.items():
            if var.get():
                self.gadget_manager.enable_gadget(gadget_name)
            else:
                self.gadget_manager.disable_gadget(gadget_name)
        
        # Call callback if provided
        if self.on_save_callback:
            self.on_save_callback()
        
        self.window.destroy()
    
    def _on_cancel(self):
        """Close window without saving."""
        self.window.destroy()
