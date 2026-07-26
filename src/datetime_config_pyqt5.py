#!/usr/bin/env python3
"""
Date/Time Configuration Dialog for KosDWM PyQt5

Allows configuring clock appearance and behavior
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QGroupBox, QComboBox, QSpinBox, QCheckBox,
    QFontDialog, QColorDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor


class DateTimeConfigDialog(QDialog):
    """
    Configuration dialog for date/time display settings
    """
    
    # Signal emitted when configuration is saved
    config_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🕐 Date & Time Configuration")
        self.setGeometry(100, 100, 450, 400)
        
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
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
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
        self.update_preview()
    
    def _load_config(self):
        """Load configuration from file"""
        default_config = {
            "datetime": {
                "show_time": True,
                "time_format": "24h",
                "show_seconds": False,
                "show_date": False,
                "date_format": "%Y-%m-%d",
                "update_interval": 1000,
                "timezone": "local",
                "font_family": "Arial",
                "font_size": 10,
                "bold": True,
                "color": "#ffffff"
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    if "datetime" in loaded:
                        default_config["datetime"].update(loaded["datetime"])
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            existing = {}
            if self.config_path.exists():
                try:
                    with open(self.config_path, 'r') as f:
                        existing = json.load(f)
                except:
                    pass
            
            existing["datetime"] = self.config["datetime"]
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(existing, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")
            return False
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("🕐 Clock Configuration")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        layout.addWidget(header)
        
        # Time format group
        time_group = QGroupBox("Time Format")
        time_layout = QFormLayout(time_group)
        
        self.show_time_check = QCheckBox("Show time in panel")
        self.show_time_check.setChecked(self.config["datetime"]["show_time"])
        self.show_time_check.stateChanged.connect(self.update_preview)
        time_layout.addRow(self.show_time_check)
        
        self.time_format_combo = QComboBox()
        self.time_format_combo.addItems(["24-hour (14:30)", "12-hour (2:30 PM)"])
        if self.config["datetime"]["time_format"] == "12h":
            self.time_format_combo.setCurrentIndex(1)
        self.time_format_combo.currentIndexChanged.connect(self.update_preview)
        time_layout.addRow("Format:", self.time_format_combo)
        
        self.show_seconds_check = QCheckBox("Show seconds")
        self.show_seconds_check.setChecked(self.config["datetime"]["show_seconds"])
        self.show_seconds_check.stateChanged.connect(self.update_preview)
        time_layout.addRow(self.show_seconds_check)
        
        layout.addWidget(time_group)
        
        # Date format group
        date_group = QGroupBox("Date Format")
        date_layout = QFormLayout(date_group)
        
        self.show_date_check = QCheckBox("Show date in panel")
        self.show_date_check.setChecked(self.config["datetime"]["show_date"])
        self.show_date_check.stateChanged.connect(self.update_preview)
        date_layout.addRow(self.show_date_check)
        
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "2025-07-23 (%Y-%m-%d)",
            "23/07/2025 (%d/%m/%Y)",
            "07/23/2025 (%m/%d/%Y)",
            "23 July 2025 (%d %B %Y)",
            "July 23, 2025 (%B %d, %Y)",
            "Wed, 23 Jul (%a, %d %b)"
        ])
        date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d %B %Y", "%B %d, %Y", "%a, %d %b"]
        current_format = self.config["datetime"]["date_format"]
        if current_format in date_formats:
            self.date_format_combo.setCurrentIndex(date_formats.index(current_format))
        self.date_format_combo.currentIndexChanged.connect(self.update_preview)
        date_layout.addRow("Date Format:", self.date_format_combo)
        
        layout.addWidget(date_group)
        
        # Update interval
        interval_group = QGroupBox("Update Settings")
        interval_layout = QFormLayout(interval_group)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 60000)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.setValue(self.config["datetime"]["update_interval"])
        self.interval_spin.setSuffix(" ms")
        interval_layout.addRow("Update Interval:", self.interval_spin)
        
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems(["Local Time", "UTC"])
        if self.config["datetime"]["timezone"] == "UTC":
            self.timezone_combo.setCurrentIndex(1)
        interval_layout.addRow("Timezone:", self.timezone_combo)
        
        layout.addWidget(interval_group)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.font_btn = QPushButton("Choose Font")
        self.font_btn.clicked.connect(self._choose_font)
        self._update_font_button()
        appearance_layout.addRow("Font:", self.font_btn)
        
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._choose_color)
        self._update_color_button()
        appearance_layout.addRow("Color:", self.color_btn)
        
        layout.addWidget(appearance_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            font-size: 24px;
            padding: 20px;
            background-color: #333333;
            border-radius: 5px;
        """)
        preview_layout.addWidget(self.preview_label)
        
        layout.addWidget(preview_group)
        
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
    
    def _choose_font(self):
        """Open font picker"""
        current_font = QFont(
            self.config["datetime"]["font_family"],
            self.config["datetime"]["font_size"]
        )
        current_font.setBold(self.config["datetime"]["bold"])
        
        font, ok = QFontDialog.getFont(current_font, self, "Choose Clock Font")
        if ok:
            self.config["datetime"]["font_family"] = font.family()
            self.config["datetime"]["font_size"] = font.pointSize()
            self.config["datetime"]["bold"] = font.bold()
            self._update_font_button()
            self.update_preview()
    
    def _update_font_button(self):
        """Update font button text"""
        font_str = f"{self.config['datetime']['font_family']} {self.config['datetime']['font_size']}pt"
        if self.config['datetime']['bold']:
            font_str += " Bold"
        self.font_btn.setText(font_str)
    
    def _choose_color(self):
        """Open color picker"""
        current_color = self.config["datetime"]["color"]
        color = QColorDialog.getColor(QColor(current_color), self, "Choose Clock Color")
        if color.isValid():
            self.config["datetime"]["color"] = color.name()
            self._update_color_button()
            self.update_preview()
    
    def _update_color_button(self):
        """Update color button appearance"""
        color = self.config["datetime"]["color"]
        self.color_btn.setStyleSheet(f"""
            background-color: {color};
            color: {'#ffffff' if QColor(color).lightness() < 128 else '#000000'};
            border: 1px solid #555555;
            padding: 5px 10px;
            min-width: 100px;
        """)
        self.color_btn.setText(color)
    
    def update_preview(self):
        """Update the preview label"""
        format_parts = []
        
        if self.show_date_check.isChecked():
            date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d %B %Y", "%B %d, %Y", "%a, %d %b"]
            date_format = date_formats[self.date_format_combo.currentIndex()]
            format_parts.append(date_format)
        
        if self.show_time_check.isChecked():
            if self.time_format_combo.currentIndex() == 0:
                time_format = "%H:%M"
            else:
                time_format = "%I:%M %p"
            
            if self.show_seconds_check.isChecked():
                time_format = time_format.replace("%M", "%M:%S")
            
            format_parts.append(time_format)
        
        if not format_parts:
            self.preview_label.setText("(Hidden)")
            return
        
        full_format = " ".join(format_parts)
        now = datetime.now()
        
        if self.timezone_combo.currentIndex() == 1:
            now = now.astimezone(timezone.utc)
        
        try:
            preview_text = now.strftime(full_format)
        except:
            preview_text = "Invalid format"
        
        color = self.config["datetime"]["color"]
        font_family = self.config["datetime"]["font_family"]
        font_size = self.config["datetime"]["font_size"]
        bold = "bold" if self.config["datetime"]["bold"] else "normal"
        
        self.preview_label.setText(preview_text)
        self.preview_label.setStyleSheet(f"""
            font-family: {font_family};
            font-size: {font_size * 2}px;
            font-weight: {bold};
            color: {color};
            padding: 20px;
            background-color: #333333;
            border-radius: 5px;
        """)
    
    def save_and_close(self):
        """Save configuration and close"""
        self.config["datetime"]["show_time"] = self.show_time_check.isChecked()
        self.config["datetime"]["time_format"] = "12h" if self.time_format_combo.currentIndex() == 1 else "24h"
        self.config["datetime"]["show_seconds"] = self.show_seconds_check.isChecked()
        self.config["datetime"]["show_date"] = self.show_date_check.isChecked()
        
        date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d %B %Y", "%B %d, %Y", "%a, %d %b"]
        self.config["datetime"]["date_format"] = date_formats[self.date_format_combo.currentIndex()]
        
        self.config["datetime"]["update_interval"] = self.interval_spin.value()
        self.config["datetime"]["timezone"] = "UTC" if self.timezone_combo.currentIndex() == 1 else "local"
        
        if self._save_config():
            # Emit signal to notify panel to reload settings
            self.config_saved.emit()
            QMessageBox.information(self, "Success", "Configuration saved!")
            self.accept()
    
    def get_config(self):
        """Return current configuration"""
        return self.config["datetime"]
