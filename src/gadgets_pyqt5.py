#!/usr/bin/env python3
"""
Gadget system for KosDWM PyQt5 version
"""

import json
import os
import sys
import importlib.util
import inspect
from pathlib import Path
from abc import ABC, abstractmethod

# Import version
try:
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from AUTOVERSION import VERSION as KOSDWM_VERSION
except ImportError:
    KOSDWM_VERSION = "unknown"


class GadgetBase(ABC):
    """
    Abstract base class for all KosDWM gadgets
    """
    
    @abstractmethod
    def get_name(self):
        """Return the unique name/identifier of the gadget."""
        pass
    
    @abstractmethod
    def get_icon(self):
        """Return the text/icon to display on the gadget button."""
        pass
    
    @abstractmethod
    def on_click(self):
        """Handle click event on the gadget."""
        pass
    
    @abstractmethod
    def get_tooltip(self):
        """Return tooltip text for the gadget."""
        pass
    
    def get_description(self):
        """Return a longer description for configuration dialogs."""
        return self.get_tooltip()


class HelloWorldGadget(GadgetBase):
    """
    Example gadget that displays a Hello World message when clicked
    """
    
    def get_name(self):
        return "hello_world"
    
    def get_icon(self):
        return "👋"
    
    def get_tooltip(self):
        return "Click to see Hello World message"
    
    def get_description(self):
        return f"A simple example gadget. KosDWM v{KOSDWM_VERSION}"
    
    def on_click(self):
        """Show Hello World alert when clicked."""
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        # Create styled message box
        msg_box = QMessageBox(QApplication.activeWindow())
        msg_box.setWindowTitle("Hello World")
        msg_box.setText(f"Hello from KosDWM v{KOSDWM_VERSION}!\n\nClick to continue.")
        msg_box.setIcon(QMessageBox.Information)
        
        # Light theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        
        msg_box.exec_()


class TestGadget(GadgetBase):
    """
    Test gadget to verify the loading system works
    """
    
    def __init__(self):
        self.test_value = 42
    
    def get_name(self):
        return "test_gadget"
    
    def get_icon(self):
        return "🧪"
    
    def get_tooltip(self):
        return "Test gadget - click to verify loading works"
    
    def get_description(self):
        return "A test gadget to verify the gadget loading system works correctly."
    
    def on_click(self):
        """Show test message."""
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        # Create styled message box
        msg_box = QMessageBox(QApplication.activeWindow())
        msg_box.setWindowTitle("Test Gadget")
        msg_box.setText(f"Dynamic loading works!\nTest value: {self.test_value}\n\n"
                       "If you see this message, the gadget system is functioning correctly.")
        msg_box.setIcon(QMessageBox.Information)
        
        # Light theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        
        msg_box.exec_()


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
        """Register built-in gadgets."""
        self.register_gadget(HelloWorldGadget, source="built-in")
        self.register_gadget(TestGadget, source="built-in")
        
        # Try to register notices gadget
        try:
            from notices_gadget_pyqt5 import NoticesGadget
            self.register_gadget(NoticesGadget, source="built-in")
            print("NoticesGadget registered")
        except ImportError as e:
            print(f"NoticesGadget not available: {e}")
    
    def _discover_gadgets(self):
        """Discover and load gadgets from the gadgets directory."""
        self._load_errors.clear()
        
        if not self._gadgets_dir.exists():
            return
        
        py_files = [f for f in self._gadgets_dir.iterdir()
                    if f.is_file() and f.suffix == '.py' and not f.name.startswith('_')]
        
        for py_file in py_files:
            self._load_gadget_module(py_file)
    
    def _load_gadget_module(self, file_path):
        """Load a gadget module from a file path."""
        try:
            module_name = f"gadget_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return
            
            module = importlib.util.module_from_spec(spec)
            
            # Add paths
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
        # Check if it's a gadget by looking for required methods
        required_methods = ['get_name', 'get_icon', 'on_click', 'get_tooltip']
        for method in required_methods:
            if not hasattr(gadget_class, method):
                raise ValueError(f"Gadget class missing required method: {method}")
        
        temp_instance = gadget_class()
        name = temp_instance.get_name()
        
        self._available_gadgets[name] = gadget_class
        self._gadget_sources[name] = source
    
    def get_gadget_source(self, gadget_name):
        """Get the source of a gadget."""
        return self._gadget_sources.get(gadget_name, "unknown")
    
    def get_load_errors(self):
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
    
    def enable_gadget(self, gadget_name):
        """Enable a gadget by name."""
        if gadget_name in self._available_gadgets:
            self._enabled_gadgets.add(gadget_name)
            self._save_config()
    
    def disable_gadget(self, gadget_name):
        """Disable a gadget by name."""
        self._enabled_gadgets.discard(gadget_name)
        self._save_config()
    
    def is_enabled(self, gadget_name):
        """Check if a gadget is enabled."""
        return gadget_name in self._enabled_gadgets
    
    def get_available_gadgets(self):
        """Get list of all available gadget names."""
        return list(self._available_gadgets.keys())
    
    def get_enabled_gadgets(self):
        """Get instances of all enabled gadgets."""
        gadgets = []
        for name in self._enabled_gadgets:
            if name in self._available_gadgets:
                gadget_class = self._available_gadgets[name]
                gadgets.append(gadget_class())
        return gadgets
    
    def get_gadget_info(self, gadget_name):
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
            self._enabled_gadgets = {"hello_world", "test_gadget"}
            self._save_config()
            return
        
        try:
            with open(self._config_path, 'r') as f:
                config = json.load(f)
                self._enabled_gadgets = set(config.get("enabled", []))
                # If empty, set defaults
                if not self._enabled_gadgets:
                    self._enabled_gadgets = {"hello_world", "test_gadget"}
        except (json.JSONDecodeError, IOError):
            self._enabled_gadgets = {"hello_world", "test_gadget"}
    
    def _save_config(self):
        """Save gadget configuration to file."""
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            config = {"enabled": list(self._enabled_gadgets)}
            with open(self._config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError:
            pass
