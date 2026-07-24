#!/usr/bin/env python3
"""
Panel Configuration Dialog for KosDWM PyQt5

Allows configuring panel colors, sizes, fonts, and styling
"""

import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QColorDialog, QFontDialog, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class PanelConfigDialog(QDialog):
    """
    Configuration dialog for panel appearance and behavior
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Panel Configuration")
        self.setGeometry(100, 100, 500, 400)
        
        # Light theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 12px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
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
                background-color: #357abd;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        self.config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        self.config = self._load_config()
        
        self.setup_ui()
    
    def _load_config(self):
        """Load panel configuration from file"""
        default_config = {
            "panel": {
                "background_color": "#333333",
                "height": 30,
                "border": "none"
            },
            "buttons": {
                "active_bg": "#666666",
                "inactive_bg": "#4a4a4a",
                "hover_bg": "#555555",
                "text_color": "#ffffff",
                "font_size": 11
            },
            "clock": {
                "font_family": "Arial",
                "font_size": 10,
                "bold": True,
                "color": "#ffffff",
                "format": "%H:%M"
            },
            "window_switcher": {
                "background_color": "#4a4a4a",
                "text_color": "#ffffff",
                "min_width": 120,
                "max_width": 200
            },
            "menus": {
                "background_color": "#f5f5f5",
                "text_color": "#333333",
                "hover_bg": "#4a90d9",
                "hover_text": "#ffffff"
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key in loaded:
                            if isinstance(value, dict):
                                default_config[key].update(loaded[key])
                            else:
                                default_config[key] = loaded[key]
            except Exception as e:
                print(f"Error loading panel config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save panel configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving panel config: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")
            return False
    
    def setup_ui(self):
        """Setup the dialog UI with tabs"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Panel tab
        panel_tab = self._create_panel_tab()
        tabs.addTab(panel_tab, "Panel")
        
        # Buttons tab
        buttons_tab = self._create_buttons_tab()
        tabs.addTab(buttons_tab, "Buttons")
        
        # Clock tab
        clock_tab = self._create_clock_tab()
        tabs.addTab(clock_tab, "Clock")
        
        # Window Switcher tab
        switcher_tab = self._create_switcher_tab()
        tabs.addTab(switcher_tab, "Window Switcher")
        
        # Menus tab
        menus_tab = self._create_menus_tab()
        tabs.addTab(menus_tab, "Menus")
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_and_close)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_panel_tab(self):
        """Create panel appearance tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # Background color
        self.panel_bg_btn = QPushButton("Choose Color")
        self.panel_bg_btn.clicked.connect(lambda: self._choose_color("panel", "background_color"))
        self._update_color_button(self.panel_bg_btn, self.config["panel"]["background_color"])
        layout.addRow("Background Color:", self.panel_bg_btn)
        
        # Height
        self.panel_height = QSpinBox()
        self.panel_height.setRange(20, 100)
        self.panel_height.setValue(self.config["panel"]["height"])
        layout.addRow("Height (px):", self.panel_height)
        
        return widget
    
    def _create_buttons_tab(self):
        """Create buttons appearance tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # Active button color
        self.btn_active_btn = QPushButton("Choose Color")
        self.btn_active_btn.clicked.connect(lambda: self._choose_color("buttons", "active_bg"))
        self._update_color_button(self.btn_active_btn, self.config["buttons"]["active_bg"])
        layout.addRow("Active Button BG:", self.btn_active_btn)
        
        # Inactive button color
        self.btn_inactive_btn = QPushButton("Choose Color")
        self.btn_inactive_btn.clicked.connect(lambda: self._choose_color("buttons", "inactive_bg"))
        self._update_color_button(self.btn_inactive_btn, self.config["buttons"]["inactive_bg"])
        layout.addRow("Inactive Button BG:", self.btn_inactive_btn)
        
        # Hover color
        self.btn_hover_btn = QPushButton("Choose Color")
        self.btn_hover_btn.clicked.connect(lambda: self._choose_color("buttons", "hover_bg"))
        self._update_color_button(self.btn_hover_btn, self.config["buttons"]["hover_bg"])
        layout.addRow("Hover BG:", self.btn_hover_btn)
        
        # Text color
        self.btn_text_btn = QPushButton("Choose Color")
        self.btn_text_btn.clicked.connect(lambda: self._choose_color("buttons", "text_color"))
        self._update_color_button(self.btn_text_btn, self.config["buttons"]["text_color"])
        layout.addRow("Text Color:", self.btn_text_btn)
        
        # Font size
        self.btn_font_size = QSpinBox()
        self.btn_font_size.setRange(8, 20)
        self.btn_font_size.setValue(self.config["buttons"]["font_size"])
        layout.addRow("Font Size:", self.btn_font_size)
        
        return widget
    
    def _create_clock_tab(self):
        """Create clock configuration tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # Font
        self.clock_font_btn = QPushButton("Choose Font")
        self.clock_font_btn.clicked.connect(self._choose_clock_font)
        self._update_font_button(self.clock_font_btn, self.config["clock"])
        layout.addRow("Font:", self.clock_font_btn)
        
        # Color
        self.clock_color_btn = QPushButton("Choose Color")
        self.clock_color_btn.clicked.connect(lambda: self._choose_color("clock", "color"))
        self._update_color_button(self.clock_color_btn, self.config["clock"]["color"])
        layout.addRow("Color:", self.clock_color_btn)
        
        # Format
        self.clock_format = QComboBox()
        self.clock_format.addItems(["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"])
        self.clock_format.setCurrentText(self.config["clock"]["format"])
        layout.addRow("Time Format:", self.clock_format)
        
        return widget
    
    def _create_switcher_tab(self):
        """Create window switcher tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # Background color
        self.switcher_bg_btn = QPushButton("Choose Color")
        self.switcher_bg_btn.clicked.connect(lambda: self._choose_color("window_switcher", "background_color"))
        self._update_color_button(self.switcher_bg_btn, self.config["window_switcher"]["background_color"])
        layout.addRow("Background Color:", self.switcher_bg_btn)
        
        # Text color
        self.switcher_text_btn = QPushButton("Choose Color")
        self.switcher_text_btn.clicked.connect(lambda: self._choose_color("window_switcher", "text_color"))
        self._update_color_button(self.switcher_text_btn, self.config["window_switcher"]["text_color"])
        layout.addRow("Text Color:", self.switcher_text_btn)
        
        # Width
        self.switcher_min_width = QSpinBox()
        self.switcher_min_width.setRange(50, 300)
        self.switcher_min_width.setValue(self.config["window_switcher"]["min_width"])
        layout.addRow("Min Width:", self.switcher_min_width)
        
        self.switcher_max_width = QSpinBox()
        self.switcher_max_width.setRange(100, 500)
        self.switcher_max_width.setValue(self.config["window_switcher"]["max_width"])
        layout.addRow("Max Width:", self.switcher_max_width)
        
        return widget
    
    def _create_menus_tab(self):
        """Create menus appearance tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # Background color
        self.menu_bg_btn = QPushButton("Choose Color")
        self.menu_bg_btn.clicked.connect(lambda: self._choose_color("menus", "background_color"))
        self._update_color_button(self.menu_bg_btn, self.config["menus"]["background_color"])
        layout.addRow("Background Color:", self.menu_bg_btn)
        
        # Text color
        self.menu_text_btn = QPushButton("Choose Color")
        self.menu_text_btn.clicked.connect(lambda: self._choose_color("menus", "text_color"))
        self._update_color_button(self.menu_text_btn, self.config["menus"]["text_color"])
        layout.addRow("Text Color:", self.menu_text_btn)
        
        # Hover background
        self.menu_hover_btn = QPushButton("Choose Color")
        self.menu_hover_btn.clicked.connect(lambda: self._choose_color("menus", "hover_bg"))
        self._update_color_button(self.menu_hover_btn, self.config["menus"]["hover_bg"])
        layout.addRow("Hover Background:", self.menu_hover_btn)
        
        return widget
    
    def _choose_color(self, section, key):
        """Open color picker and update config"""
        current_color = self.config[section][key]
        color = QColorDialog.getColor(QColor(current_color), self, "Choose Color")
        if color.isValid():
            self.config[section][key] = color.name()
            # Update button
            if section == "panel" and key == "background_color":
                self._update_color_button(self.panel_bg_btn, color.name())
            elif section == "buttons":
                if key == "active_bg":
                    self._update_color_button(self.btn_active_btn, color.name())
                elif key == "inactive_bg":
                    self._update_color_button(self.btn_inactive_btn, color.name())
                elif key == "hover_bg":
                    self._update_color_button(self.btn_hover_btn, color.name())
                elif key == "text_color":
                    self._update_color_button(self.btn_text_btn, color.name())
            elif section == "clock" and key == "color":
                self._update_color_button(self.clock_color_btn, color.name())
            elif section == "window_switcher":
                if key == "background_color":
                    self._update_color_button(self.switcher_bg_btn, color.name())
                elif key == "text_color":
                    self._update_color_button(self.switcher_text_btn, color.name())
            elif section == "menus":
                if key == "background_color":
                    self._update_color_button(self.menu_bg_btn, color.name())
                elif key == "text_color":
                    self._update_color_button(self.menu_text_btn, color.name())
                elif key == "hover_bg":
                    self._update_color_button(self.menu_hover_btn, color.name())
    
    def _update_color_button(self, button, color):
        """Update button to show selected color"""
        button.setStyleSheet(f"""
            background-color: {color};
            color: {'#ffffff' if QColor(color).lightness() < 128 else '#000000'};
            border: 1px solid #cccccc;
            padding: 5px 10px;
            min-width: 100px;
        """)
        button.setText(color)
    
    def _choose_clock_font(self):
        """Open font picker for clock"""
        current_font = QFont(
            self.config["clock"]["font_family"],
            self.config["clock"]["font_size"]
        )
        current_font.setBold(self.config["clock"]["bold"])
        
        font, ok = QFontDialog.getFont(current_font, self, "Choose Clock Font")
        if ok:
            self.config["clock"]["font_family"] = font.family()
            self.config["clock"]["font_size"] = font.pointSize()
            self.config["clock"]["bold"] = font.bold()
            self._update_font_button(self.clock_font_btn, self.config["clock"])
    
    def _update_font_button(self, button, clock_config):
        """Update font button text"""
        font_str = f"{clock_config['font_family']} {clock_config['font_size']}pt"
        if clock_config['bold']:
            font_str += " Bold"
        button.setText(font_str)
    
    def save_and_close(self):
        """Save configuration and close dialog"""
        # Update config from UI values
        self.config["panel"]["height"] = self.panel_height.value()
        self.config["buttons"]["font_size"] = self.btn_font_size.value()
        self.config["clock"]["format"] = self.clock_format.currentText()
        self.config["window_switcher"]["min_width"] = self.switcher_min_width.value()
        self.config["window_switcher"]["max_width"] = self.switcher_max_width.value()
        
        if self._save_config():
            QMessageBox.information(self, "Success", "Configuration saved!\nRestart KosDWM to apply changes.")
            self.accept()
    
    def get_config(self):
        """Return current configuration"""
        return self.config
