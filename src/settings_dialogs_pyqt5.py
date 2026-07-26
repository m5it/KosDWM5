#!/usr/bin/env python3
"""
Settings dialogs for KosDWM PyQt5 panel
"""

import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSpinBox, QLineEdit, QGroupBox,
    QTabWidget, QWidget, QFormLayout, QMessageBox, QColorDialog,
    QFontComboBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont


class PanelSettingsDialog(QDialog):
    """Panel settings dialog"""
    monitor_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Panel Settings")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Monitor settings group
        monitor_group = QGroupBox("Monitor Settings")
        monitor_layout = QFormLayout(monitor_group)
        
        self.monitor_mode = QComboBox()
        self.monitor_mode.addItem("Primary Monitor", "primary")
        self.monitor_mode.addItem("All Monitors", "all")
        self.monitor_mode.addItem("Specific Monitor", "specific")
        monitor_layout.addRow("Display Mode:", self.monitor_mode)
        
        self.specific_monitor = QSpinBox()
        self.specific_monitor.setRange(0, 9)
        monitor_layout.addRow("Monitor Index:", self.specific_monitor)
        
        layout.addWidget(monitor_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def load_settings(self):
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    monitor_config = config.get("monitor", {})
                    
                    mode = monitor_config.get("mode", "primary")
                    index = self.monitor_mode.findData(mode)
                    if index >= 0:
                        self.monitor_mode.setCurrentIndex(index)
                    
                    self.specific_monitor.setValue(monitor_config.get("specific_index", 0))
            except Exception as e:
                print(f"Error loading settings: {e}", flush=True)
    
    def save_settings(self):
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        
        try:
            config = {}
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            if "monitor" not in config:
                config["monitor"] = {}
            
            config["monitor"]["mode"] = self.monitor_mode.currentData()
            config["monitor"]["specific_index"] = self.specific_monitor.value()
            
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.monitor_changed.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")


class MenuSettingsDialog(QDialog):
    """Menu settings dialog"""
    menus_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Menu Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_menus()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Menu list
        layout.addWidget(QLabel("Configured Menus:"))
        self.menu_list = QListWidget()
        layout.addWidget(self.menu_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Menu")
        self.add_btn.clicked.connect(self.add_menu)
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_menu)
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_menu)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Dialog buttons
        dialog_btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_menus)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        dialog_btn_layout.addStretch()
        dialog_btn_layout.addWidget(self.save_btn)
        dialog_btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(dialog_btn_layout)
    
    def load_menus(self):
        config_path = Path.home() / ".config" / "KosDWM" / "menus.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    menus = json.load(f)
                    for menu in menus:
                        item = QListWidgetItem(f"{menu.get('name', 'Unknown')} ({menu.get('type', 'unknown')})")
                        item.setData(Qt.UserRole, menu)
                        self.menu_list.addItem(item)
            except Exception as e:
                print(f"Error loading menus: {e}", flush=True)
    
    def add_menu(self):
        # Simple add - in real implementation would show a dialog
        pass
    
    def edit_menu(self):
        pass
    
    def remove_menu(self):
        current = self.menu_list.currentRow()
        if current >= 0:
            self.menu_list.takeItem(current)
    
    def save_menus(self):
        menus = []
        for i in range(self.menu_list.count()):
            item = self.menu_list.item(i)
            menu_data = item.data(Qt.UserRole)
            if menu_data:
                menus.append(menu_data)
        
        config_path = Path.home() / ".config" / "KosDWM" / "menus.json"
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(menus, f, indent=2)
            self.menus_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save menus: {e}")


class DateTimeSettingsDialog(QDialog):
    """Date/time settings dialog"""
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Date/Time Settings")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Time settings
        time_group = QGroupBox("Time Display")
        time_layout = QFormLayout(time_group)
        
        self.show_time = QCheckBox("Show time")
        time_layout.addRow(self.show_time)
        
        self.time_format = QComboBox()
        self.time_format.addItem("24-hour", "24h")
        self.time_format.addItem("12-hour", "12h")
        time_layout.addRow("Format:", self.time_format)
        
        self.show_seconds = QCheckBox("Show seconds")
        time_layout.addRow(self.show_seconds)
        
        layout.addWidget(time_group)
        
        # Date settings
        date_group = QGroupBox("Date Display")
        date_layout = QFormLayout(date_group)
        
        self.show_date = QCheckBox("Show date")
        date_layout.addRow(self.show_date)
        
        self.date_format = QLineEdit()
        self.date_format.setPlaceholderText("%Y-%m-%d")
        date_layout.addRow("Date format:", self.date_format)
        
        self.order = QComboBox()
        self.order.addItem("Date then Time", "date_time")
        self.order.addItem("Time then Date", "time_date")
        date_layout.addRow("Display order:", self.order)
        
        layout.addWidget(date_group)
        
        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.font_family = QFontComboBox()
        appearance_layout.addRow("Font:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(10)
        appearance_layout.addRow("Font size:", self.font_size)
        
        self.bold = QCheckBox("Bold")
        appearance_layout.addRow(self.bold)
        
        self.color_btn = QPushButton("Choose Color...")
        self.color_btn.clicked.connect(self.choose_color)
        self.current_color = "#ffffff"
        appearance_layout.addRow("Text color:", self.color_btn)
        
        layout.addWidget(appearance_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.current_color};")
    
    def load_settings(self):
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    datetime_config = config.get("datetime", {})
                    
                    self.show_time.setChecked(datetime_config.get("show_time", True))
                    self.show_seconds.setChecked(datetime_config.get("show_seconds", False))
                    self.show_date.setChecked(datetime_config.get("show_date", False))
                    
                    time_format = datetime_config.get("time_format", "24h")
                    index = self.time_format.findData(time_format)
                    if index >= 0:
                        self.time_format.setCurrentIndex(index)
                    
                    self.date_format.setText(datetime_config.get("date_format", "%Y-%m-%d"))
                    
                    order = datetime_config.get("order", "date_time")
                    index = self.order.findData(order)
                    if index >= 0:
                        self.order.setCurrentIndex(index)
                    
                    font_family = datetime_config.get("font_family", "Arial")
                    self.font_family.setCurrentFont(QFont(font_family))
                    
                    self.font_size.setValue(datetime_config.get("font_size", 10))
                    self.bold.setChecked(datetime_config.get("bold", True))
                    
                    self.current_color = datetime_config.get("color", "#ffffff")
                    self.color_btn.setStyleSheet(f"background-color: {self.current_color};")
                    
            except Exception as e:
                print(f"Error loading datetime settings: {e}", flush=True)
    
    def save_settings(self):
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        
        try:
            config = {}
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            if "datetime" not in config:
                config["datetime"] = {}
            
            config["datetime"]["show_time"] = self.show_time.isChecked()
            config["datetime"]["show_seconds"] = self.show_seconds.isChecked()
            config["datetime"]["show_date"] = self.show_date.isChecked()
            config["datetime"]["time_format"] = self.time_format.currentData()
            config["datetime"]["date_format"] = self.date_format.text() or "%Y-%m-%d"
            config["datetime"]["order"] = self.order.currentData()
            config["datetime"]["font_family"] = self.font_family.currentFont().family()
            config["datetime"]["font_size"] = self.font_size.value()
            config["datetime"]["bold"] = self.bold.isChecked()
            config["datetime"]["color"] = self.current_color
            
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.settings_changed.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")
