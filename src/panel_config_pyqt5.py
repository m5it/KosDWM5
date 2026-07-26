#!/usr/bin/env python3
"""
Panel Configuration Dialog for KosDWM PyQt5

Allows configuring panel colors, sizes, fonts, styling, and multi-monitor placement
"""

import json
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFormLayout, QLineEdit, QSpinBox,
    QComboBox, QColorDialog, QFontDialog, QMessageBox, QCheckBox,
    QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont


class PanelConfigDialog(QDialog):
    """
    Configuration dialog for panel appearance, behavior, and monitor placement
    """
    
    # Signal emitted when configuration is saved
    config_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Panel Configuration")
        self.setGeometry(100, 100, 500, 450)
        
        # Dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QGroupBox {
                font-weight: bold;
                color: #ffffff;
                border: 1px solid #444444;
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
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
            }
            QTabWidget::pane {
                background-color: #1a1a1a;
                border: 1px solid #444444;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #444444;
            }
            QTabBar::tab:selected {
                background-color: #4a4a4a;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
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
            },
            "monitor": {
                "mode": "primary",  # "primary", "specific", "all", "follow_active"
                "specific_index": 0,
                "follow_interval": 500
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
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
    
    def get_monitor_count(self):
        """Get number of connected monitors using xrandr"""
        try:
            result = subprocess.run(
                ["xrandr", "--listactivemonitors"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # First line is "Monitors: N", subsequent lines are monitor info
                lines = result.stdout.strip().split('\n')
                if lines:
                    first_line = lines[0]
                    if "Monitors:" in first_line:
                        return int(first_line.split(':')[1].strip())
            return 1  # Default to 1 if we can't detect
        except Exception as e:
            print(f"Error detecting monitors: {e}")
            return 1
    
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
        
        # Monitor tab (NEW)
        monitor_tab = self._create_monitor_tab()
        tabs.addTab(monitor_tab, "Monitor")
        
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
    
    def _create_monitor_tab(self):
        """Create monitor placement tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Info label
        info_label = QLabel("Configure which monitor displays the panel")
        info_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        layout.addWidget(info_label)
        
        # Monitor mode group
        mode_group = QGroupBox("Monitor Mode")
        mode_layout = QFormLayout(mode_group)
        mode_layout.setSpacing(10)
        
        # Monitor mode dropdown
        self.monitor_mode = QComboBox()
        self.monitor_mode.addItems([
            "Primary Monitor",
            "Specific Monitor",
            "All Monitors",
            "Follow Active Monitor"
        ])
        mode_map = {
            "primary": 0,
            "specific": 1,
            "all": 2,
            "follow_active": 3
        }
        current_mode = self.config["monitor"].get("mode", "primary")
        self.monitor_mode.setCurrentIndex(mode_map.get(current_mode, 0))
        self.monitor_mode.currentIndexChanged.connect(self._on_monitor_mode_changed)
        mode_layout.addRow("Display Mode:", self.monitor_mode)
        
        # Specific monitor index
        self.monitor_index = QSpinBox()
        self.monitor_index.setRange(0, 9)
        self.monitor_index.setValue(self.config["monitor"].get("specific_index", 0))
        self.monitor_index.setEnabled(current_mode == "specific")
        mode_layout.addRow("Monitor Index:", self.monitor_index)
        
        # Detected monitors info
        monitor_count = self.get_monitor_count()
        self.monitor_info = QLabel(f"Detected monitors: {monitor_count}")
        self.monitor_info.setStyleSheet("color: #4a90d9; font-size: 11px;")
        mode_layout.addRow(self.monitor_info)
        
        layout.addWidget(mode_group)
        
        # Follow active settings group
        follow_group = QGroupBox("Follow Active Settings")
        follow_layout = QFormLayout(follow_group)
        
        self.follow_interval = QSpinBox()
        self.follow_interval.setRange(100, 5000)
        self.follow_interval.setSingleStep(100)
        self.follow_interval.setValue(self.config["monitor"].get("follow_interval", 500))
        self.follow_interval.setSuffix(" ms")
        follow_layout.addRow("Check Interval:", self.follow_interval)
        
        follow_info = QLabel(
            "When 'Follow Active Monitor' is selected, the panel will move\n"
            "to whichever monitor has the active window."
        )
        follow_info.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        follow_layout.addRow(follow_info)
        
        layout.addWidget(follow_group)
        
        # Description labels
        desc_group = QGroupBox("Mode Descriptions")
        desc_layout = QVBoxLayout(desc_group)
        
        desc_text = QLabel(
            "<b>Primary Monitor:</b> Always display on the primary monitor<br>"
            "<b>Specific Monitor:</b> Display on a specific monitor by index<br>"
            "<b>All Monitors:</b> Show panel on all connected monitors<br>"
            "<b>Follow Active Monitor:</b> Panel follows the active window"
        )
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("color: #cccccc; font-size: 11px; line-height: 1.4;")
        desc_layout.addWidget(desc_text)
        
        layout.addWidget(desc_group)
        layout.addStretch()
        
        return widget
    
    def _on_monitor_mode_changed(self, index):
        """Handle monitor mode change"""
        # Enable/disable specific index based on mode
        self.monitor_index.setEnabled(index == 1)  # "Specific Monitor"
    
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
        self.menus_bg_btn = QPushButton("Choose Color")
        self.menus_bg_btn.clicked.connect(lambda: self._choose_color("menus", "background_color"))
        self._update_color_button(self.menus_bg_btn, self.config["menus"]["background_color"])
        layout.addRow("Background Color:", self.menus_bg_btn)
        
        # Text color
        self.menus_text_btn = QPushButton("Choose Color")
        self.menus_text_btn.clicked.connect(lambda: self._choose_color("menus", "text_color"))
        self._update_color_button(self.menus_text_btn, self.config["menus"]["text_color"])
        layout.addRow("Text Color:", self.menus_text_btn)
        
        # Hover background
        self.menus_hover_bg_btn = QPushButton("Choose Color")
        self.menus_hover_bg_btn.clicked.connect(lambda: self._choose_color("menus", "hover_bg"))
        self._update_color_button(self.menus_hover_bg_btn, self.config["menus"]["hover_bg"])
        layout.addRow("Hover BG:", self.menus_hover_bg_btn)
        
        # Hover text
        self.menus_hover_text_btn = QPushButton("Choose Color")
        self.menus_hover_text_btn.clicked.connect(lambda: self._choose_color("menus", "hover_text"))
        self._update_color_button(self.menus_hover_text_btn, self.config["menus"]["hover_text"])
        layout.addRow("Hover Text:", self.menus_hover_text_btn)
        
        return widget
    
    def _choose_color(self, section, key):
        """Open color picker for a config option"""
        current_color = self.config[section][key]
        color = QColorDialog.getColor(QColor(current_color), self, f"Choose {key.replace('_', ' ').title()}")
        if color.isValid():
            self.config[section][key] = color.name()
            # Update the appropriate button
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
                    self._update_color_button(self.menus_bg_btn, color.name())
                elif key == "text_color":
                    self._update_color_button(self.menus_text_btn, color.name())
                elif key == "hover_bg":
                    self._update_color_button(self.menus_hover_bg_btn, color.name())
                elif key == "hover_text":
                    self._update_color_button(self.menus_hover_text_btn, color.name())
    
    def _update_color_button(self, button, color):
        """Update color button appearance"""
        button.setStyleSheet(f"""
            background-color: {color};
            color: {'#ffffff' if QColor(color).lightness() < 128 else '#000000'};
            border: 1px solid #555555;
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
        # Update panel settings
        self.config["panel"]["height"] = self.panel_height.value()
        
        # Update monitor settings
        mode_map = {
            0: "primary",
            1: "specific",
            2: "all",
            3: "follow_active"
        }
        self.config["monitor"]["mode"] = mode_map.get(self.monitor_mode.currentIndex(), "primary")
        self.config["monitor"]["specific_index"] = self.monitor_index.value()
        self.config["monitor"]["follow_interval"] = self.follow_interval.value()
        
        # Update button settings
        self.config["buttons"]["font_size"] = self.btn_font_size.value()
        
        # Update clock settings
        self.config["clock"]["format"] = self.clock_format.currentText()
        
        # Update window switcher settings
        self.config["window_switcher"]["min_width"] = self.switcher_min_width.value()
        self.config["window_switcher"]["max_width"] = self.switcher_max_width.value()
        
        if self._save_config():
            self.config_saved.emit()
            QMessageBox.information(self, "Success", "Configuration saved!")
            self.accept()
