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
    
    def __init__(self):
        self._panel = None  # Reference to panel for updates
    
    def set_panel(self, panel):
        """Store reference to panel for refresh notifications"""
        self._panel = panel
    
    def refresh_icon(self):
        """Notify panel that icon needs refresh"""
        if self._panel:
            self._panel.refresh_gadget_icon(self)
    
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
    
    def __init__(self):
        super().__init__()
    
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
        
        # Apply dark theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5aa0e9;
            }
        """)
        
        msg_box.exec_()


class TestGadget(GadgetBase):
    """
    Test gadget that displays a counter
    """
    
    def __init__(self):
        super().__init__()
        self.counter = 0
    
    def get_name(self):
        return "test_gadget"
    
    def get_icon(self):
        self.counter += 1
        return f"🧪{self.counter}"
    
    def get_tooltip(self):
        return f"Test gadget (clicked {self.counter} times)"
    
    def on_click(self):
        """Increment counter and show message."""
        from PyQt5.QtWidgets import QMessageBox, QApplication
        
        msg_box = QMessageBox(QApplication.activeWindow())
        msg_box.setWindowTitle("Test Gadget")
        msg_box.setText(f"Test gadget clicked!\nCount: {self.counter}")
        
        # Apply dark theme styling
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5aa0e9;
            }
        """)
        
        msg_box.exec_()


class GadgetManager:
    """
    Manages gadget loading and configuration
    """
    
    def __init__(self):
        self.config_file = Path.home() / ".config" / "KosDWM" / "gadgets.json"
        self.gadgets = {}
        self._load_builtin_gadgets()
        self._load_config()
    
    def _load_builtin_gadgets(self):
        """Load built-in gadgets"""
        self.gadgets["hello_world"] = HelloWorldGadget()
        self.gadgets["test_gadget"] = TestGadget()
        
        # Try to load notices gadget
        try:
            from notices_gadget_pyqt5 import NoticesGadget
            self.gadgets["notices"] = NoticesGadget()
        except ImportError as e:
            print(f"Could not load notices gadget: {e}")
    
    def _load_config(self):
        """Load gadget configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.enabled_gadgets = config.get("enabled", [])
            except Exception as e:
                print(f"Error loading gadget config: {e}")
                self.enabled_gadgets = []
        else:
            # Default: enable all gadgets
            self.enabled_gadgets = list(self.gadgets.keys())
            self._save_config()
    
    def _save_config(self):
        """Save gadget configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump({"enabled": self.enabled_gadgets}, f, indent=2)
        except Exception as e:
            print(f"Error saving gadget config: {e}")
    
    def get_enabled_gadgets(self):
        """Get list of enabled gadgets"""
        return [self.gadgets[name] for name in self.enabled_gadgets 
                if name in self.gadgets]
    
    def get_all_gadgets(self):
        """Get all available gadgets"""
        return list(self.gadgets.values())
    
    def enable_gadget(self, name):
        """Enable a gadget"""
        if name in self.gadgets and name not in self.enabled_gadgets:
            self.enabled_gadgets.append(name)
            self._save_config()
    
    def disable_gadget(self, name):
        """Disable a gadget"""
        if name in self.enabled_gadgets:
            self.enabled_gadgets.remove(name)
            self._save_config()
    
    def is_enabled(self, name):
        """Check if a gadget is enabled"""
        return name in self.enabled_gadgets


def configure_gadgets(parent=None):
    """Open gadget configuration dialog"""
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                  QCheckBox, QPushButton, QLabel, QScrollArea,
                                  QWidget, QFrame)
    
    manager = GadgetManager()
    
    dialog = QDialog(parent)
    dialog.setWindowTitle("Configure Gadgets")
    dialog.setGeometry(100, 100, 400, 300)
    
    # Apply dark theme
    dialog.setStyleSheet("""
        QDialog {
            background-color: #2d2d2d;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
        }
        QCheckBox {
            color: #ffffff;
            font-size: 13px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QPushButton {
            background-color: #4a90d9;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5aa0e9;
        }
        QScrollArea {
            border: none;
            background-color: #2d2d2d;
        }
    """)
    
    layout = QVBoxLayout(dialog)
    
    # Title
    title = QLabel("Select gadgets to display:")
    title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
    layout.addWidget(title)
    
    # Scroll area for gadgets
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_content = QWidget()
    scroll_layout = QVBoxLayout(scroll_content)
    
    checkboxes = {}
    for gadget in manager.get_all_gadgets():
        checkbox = QCheckBox(f"{gadget.get_icon()} {gadget.get_name()}")
        checkbox.setChecked(manager.is_enabled(gadget.get_name()))
        checkbox.setToolTip(gadget.get_description())
        scroll_layout.addWidget(checkbox)
        checkboxes[gadget.get_name()] = checkbox
    
    scroll_layout.addStretch()
    scroll.setWidget(scroll_content)
    layout.addWidget(scroll)
    
    # Buttons
    btn_layout = QHBoxLayout()
    
    cancel_btn = QPushButton("Cancel")
    cancel_btn.setStyleSheet("background-color: #666666;")
    cancel_btn.clicked.connect(dialog.reject)
    btn_layout.addWidget(cancel_btn)
    
    btn_layout.addStretch()
    
    save_btn = QPushButton("Save")
    save_btn.clicked.connect(lambda: _save_gadget_config(dialog, manager, checkboxes))
    btn_layout.addWidget(save_btn)
    
    layout.addLayout(btn_layout)
    
    dialog.exec_()


def _save_gadget_config(dialog, manager, checkboxes):
    """Save gadget configuration"""
    for name, checkbox in checkboxes.items():
        if checkbox.isChecked():
            manager.enable_gadget(name)
        else:
            manager.disable_gadget(name)
    dialog.accept()


if __name__ == "__main__":
    # Test the gadget system
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    manager = GadgetManager()
    print("Available gadgets:")
    for gadget in manager.get_all_gadgets():
        print(f"  - {gadget.get_name()}: {gadget.get_icon()} ({'enabled' if manager.is_enabled(gadget.get_name()) else 'disabled'})")
    
    # Test configuration dialog
    configure_gadgets()
