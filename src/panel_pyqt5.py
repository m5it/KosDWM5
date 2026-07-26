#!/usr/bin/env python3
"""
Panel widget for KosDWM PyQt5 version
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QComboBox, QFrame, QMenu, QAction, QButtonGroup
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from datetime import datetime

from src.panel_api_pyqt5 import PanelAPI


class Panel(QFrame):
    """
    Top panel with gadgets, menus, clock, and desktop switcher
    """
    
    datetime_changed = pyqtSignal()
    
    def __init__(self, parent=None, is_clone=False):
        super().__init__(parent)
        
        self.is_clone = is_clone
        self.clone_windows = []
        self.last_desktop = -1
        
        # Cache whether xdotool is available
        self._xdotool_available = shutil.which("xdotool") is not None
        
        self.datetime_config = self._load_datetime_config()
        self.monitor_config = self._load_monitor_config()
        
        self.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border: none;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QLabel {
                color: white;
                font-size: 11px;
            }
            QComboBox {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 2px 5px;
                font-size: 11px;
                min-width: 120px;
                max-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666666;
                selection-background-color: #666666;
            }
        """)
        
        from src.desktop_manager_pyqt5 import DesktopManager
        self.desktop_manager = DesktopManager(self)
        self.desktop_manager.desktop_changed.connect(self.on_desktop_changed)
        
        from src.menus_pyqt5 import MenuManager
        self.menu_manager = MenuManager(self)
        
        from src.window_manager_pyqt5 import WindowManager
        self.window_manager = WindowManager()
        
        self.api = PanelAPI(port=8080)
        self.api.start()
        
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(self.datetime_config.get("update_interval", 1000))
        
        self.window_timer = QTimer()
        self.window_timer.timeout.connect(self.update_window_list)
        self.window_timer.start(2000)
        
        # Monitor desktop switches via environment variable
        self.desktop_monitor_timer = QTimer()
        self.desktop_monitor_timer.timeout.connect(self._check_desktop_change)
        self.desktop_monitor_timer.start(500)
        print("[Panel] Desktop monitor started", flush=True)
        
        mode = self.monitor_config.get("mode", "primary")
        if mode == "specific":
            QTimer.singleShot(500, self._update_panel_position)
        
        QTimer.singleShot(1000, self._make_sticky)
    
    def _load_datetime_config(self):
        default_config = {
            "show_time": True,
            "time_format": "24h",
            "show_seconds": False,
            "show_date": False,
            "date_format": "%Y-%m-%d",
            "order": "date_time",
            "update_interval": 1000,
            "timezone": "local",
            "font_family": "Arial",
            "font_size": 10,
            "bold": True,
            "color": "#ffffff"
        }
        
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    if "datetime" in loaded:
                        default_config.update(loaded["datetime"])
            except Exception as e:
                print(f"[Panel] Error loading datetime config: {e}", flush=True)
        
        return default_config
    
    def _load_monitor_config(self):
        default_config = {
            "mode": "primary",
            "specific_index": 0,
            "follow_interval": 500
        }
        
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    if "monitor" in loaded:
                        default_config.update(loaded["monitor"])
            except Exception as e:
                print(f"[Panel] Error loading monitor config: {e}", flush=True)
        
        return default_config
    
    def get_monitors(self):
        try:
            result = subprocess.run(
                ["xrandr", "--listactivemonitors"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                monitors = []
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        geom = parts[2]
                        if '+' in geom:
                            res, offsets = geom.split('+', 1)
                            wh = res.split('x')
                            if len(wh) == 2:
                                width_str = wh[0].split('/')[0]
                                height_str = wh[1].split('/')[0]
                                width = int(width_str)
                                height = int(height_str)
                                
                                x = int(offsets.split('+')[0])
                                y = int(offsets.split('+')[1]) if '+' in offsets else 0
                                
                                monitors.append({
                                    'index': len(monitors),
                                    'name': parts[1].lstrip('+'),
                                    'width': width,
                                    'height': height,
                                    'x': x,
                                    'y': y
                                })
                
                return monitors if monitors else [{'index': 0, 'name': 'primary', 'width': 1920, 'height': 1080, 'x': 0, 'y': 0}]
            
            return [{'index': 0, 'name': 'primary', 'width': 1920, 'height': 1080, 'x': 0, 'y': 0}]
        except Exception as e:
            print(f"[Panel] Error getting monitors: {e}", flush=True)
            return [{'index': 0, 'name': 'primary', 'width': 1920, 'height': 1080, 'x': 0, 'y': 0}]
    
    def _get_current_desktop(self):
        """Get current desktop from root window property"""
        try:
            result = subprocess.run(
                ["xprop", "-root", "_NET_CURRENT_DESKTOP"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                line = result.stdout.strip()
                if '=' in line:
                    desktop = int(line.split('=')[1].strip())
                    return desktop
            return 0
        except Exception as e:
            print(f"[Panel] Error getting current desktop: {e}", flush=True)
            return 0
    
    def _get_panel_window_id(self):
        """Get the actual panel window ID using xdotool or fallback to Qt winId"""
        # Only try xdotool if it's available
        if self._xdotool_available:
            try:
                result = subprocess.run(
                    ["xdotool", "search", "--class", "kosdwm"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    win_ids = result.stdout.strip().split('\n')
                    if win_ids:
                        return win_ids[0].strip()
                
                result = subprocess.run(
                    ["xdotool", "search", "--name", "KosDWM"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    win_ids = result.stdout.strip().split('\n')
                    if win_ids:
                        return win_ids[0].strip()
            except Exception:
                pass  # Fall through to Qt winId
        
        # Fallback to Qt window ID
        parent = self.parent()
        if parent:
            return str(int(parent.winId()))
        return str(int(self.winId()))
    
    def _check_desktop_change(self):
        """Check if desktop changed using environment variable WINDOWID"""
        try:
            # Get WINDOWID from environment - this changes when switching desktops!
            env_windowid = os.environ.get('WINDOWID', '')
            current_desktop = self._get_current_desktop()
            
            if self.last_desktop == -1:
                self.last_desktop = current_desktop
                self._last_windowid = env_windowid
                print(f"[Panel] Initial desktop: {current_desktop}, WINDOWID: {env_windowid}", flush=True)
                self._make_sticky()
                return
            
            # Check if desktop changed (either desktop number or WINDOWID)
            if current_desktop != self.last_desktop or env_windowid != getattr(self, '_last_windowid', ''):
                print(f"[Panel] DESKTOP SWITCHED: {self.last_desktop} -> {current_desktop}, WINDOWID: {self._last_windowid} -> {env_windowid}", flush=True)
                self.last_desktop = current_desktop
                self._last_windowid = env_windowid
                
                win_id = self._get_panel_window_id()
                print(f"[Panel] Panel window ID: {win_id}", flush=True)
                
                # Move panel to new desktop
                subprocess.run(
                    ["wmctrl", "-i", "-r", win_id, "-t", str(current_desktop)],
                    capture_output=True,
                    timeout=5
                )
                
                # Keep it above other windows
                subprocess.run(
                    ["wmctrl", "-i", "-r", win_id, "-b", "add,above"],
                    capture_output=True,
                    timeout=5
                )
                
                print(f"[Panel] Moved panel to desktop {current_desktop}", flush=True)
                
        except Exception as e:
            print(f"[Panel] Error in desktop check: {e}", flush=True)
    
    def _make_sticky(self):
        """Make panel visible on all desktops"""
        try:
            win_id = self._get_panel_window_id()
            print(f"[Panel] Making window {win_id} sticky", flush=True)
            
            subprocess.run(
                ["wmctrl", "-i", "-r", win_id, "-b", "add,sticky"],
                capture_output=True,
                timeout=5
            )
            
            subprocess.run(
                ["xprop", "-id", win_id, "-f", "_NET_WM_DESKTOP", "32c", 
                 "-set", "_NET_WM_DESKTOP", "4294967295"],
                capture_output=True,
                timeout=5
            )
            
            subprocess.run(
                ["xprop", "-id", win_id, "-f", "_NET_WM_WINDOW_TYPE", "32a",
                 "-set", "_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_DOCK"],
                capture_output=True,
                timeout=5
            )
            
            subprocess.run(
                ["wmctrl", "-i", "-r", win_id, "-b", "add,sticky,above"],
                capture_output=True,
                timeout=5
            )
            
            print(f"[Panel] Window {win_id} made sticky", flush=True)
            
        except Exception as e:
            print(f"[Panel] Error making sticky: {e}", flush=True)
    
    def _update_panel_position(self):
        mode = self.monitor_config.get("mode", "primary")
        monitors = self.get_monitors()
        
        if not monitors:
            return
        
        if mode == "all":
            return
        elif mode == "primary":
            return
        elif mode == "specific":
            index = self.monitor_config.get("specific_index", 0)
            if 0 <= index < len(monitors):
                target_monitor = monitors[index]
                self._reposition_on_monitor(target_monitor)
    
    def _reposition_on_monitor(self, monitor):
        parent = self.parent()
        if parent:
            parent.move(monitor['x'], 0)
            print(f"[Panel] Moved to monitor {monitor['index']}", flush=True)
    
    def reload_monitor_config(self):
        self.monitor_config = self._load_monitor_config()
        self._update_panel_position()
        self._make_sticky()
    
    def reload_datetime_config(self):
        self.datetime_config = self._load_datetime_config()
        self.timer.stop()
        self.timer.start(self.datetime_config.get("update_interval", 1000))
        
        font = QFont(
            self.datetime_config.get("font_family", "Arial"),
            self.datetime_config.get("font_size", 10)
        )
        if self.datetime_config.get("bold", True):
            font.setBold(True)
        self.time_label.setFont(font)
        
        color = self.datetime_config.get("color", "#ffffff")
        self.time_label.setStyleSheet(f"color: {color};")
        self.update_time()
        self.datetime_changed.emit()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        self.menus_button = QPushButton("☰")
        self.menus_button.setFixedWidth(30)
        self.menus_button.setMenu(self.build_menus_menu())
        layout.addWidget(self.menus_button)
        
        self.window_combo = QComboBox()
        self.window_combo.setPlaceholderText("🪟 Windows")
        self.window_combo.setEnabled(self.window_manager.is_available())
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        layout.addWidget(self.window_combo)
        
        self.desktop_group = QButtonGroup(self)
        self.desktop_buttons = []
        for i in range(4):
            btn = QPushButton(str(i + 1))
            btn.setFixedWidth(25)
            btn.setFixedHeight(22)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, d=i: self.switch_desktop(d))
            self.desktop_group.addButton(btn)
            self.desktop_buttons.append(btn)
            layout.addWidget(btn)
        
        self.gadgets_frame = QFrame()
        self.gadgets_frame.setStyleSheet("background-color: transparent;")
        self.gadgets_layout = QHBoxLayout(self.gadgets_frame)
        self.gadgets_layout.setContentsMargins(0, 0, 0, 0)
        self.gadgets_layout.setSpacing(5)
        layout.addWidget(self.gadgets_frame)
        
        layout.addStretch()
        
        font = QFont(
            self.datetime_config.get("font_family", "Arial"),
            self.datetime_config.get("font_size", 10)
        )
        if self.datetime_config.get("bold", True):
            font.setBold(True)
        
        self.time_label = QLabel("00:00")
        self.time_label.setFont(font)
        self.time_label.setStyleSheet(f"color: {self.datetime_config.get('color', '#ffffff')};")
        layout.addWidget(self.time_label)
        
        self.config_combo = QComboBox()
        self.config_combo.setPlaceholderText("⚙ Config")
        self.config_combo.addItem("Manage Gadgets")
        self.config_combo.addItem("Panel Settings")
        self.config_combo.addItem("Menu Settings")
        self.config_combo.addItem("Date/Time Settings")
        self.config_combo.addItem("About KosDWM")
        self.config_combo.setFixedWidth(120)
        self.config_combo.setFixedHeight(22)
        self.config_combo.currentIndexChanged.connect(self.on_config_selected)
        layout.addWidget(self.config_combo)
        
        self.load_gadgets()
        self.update_desktop_buttons()
        self.update_window_list()
    
    def update_window_list(self):
        if not self.window_manager.is_available():
            self.window_combo.setEnabled(False)
            return
        
        self.window_combo.setEnabled(True)
        
        current_id = None
        current_index = self.window_combo.currentIndex()
        if current_index > 0:
            current_data = self.window_combo.itemData(current_index)
            if current_data:
                current_id = current_data.get('id')
        
        self.window_combo.blockSignals(True)
        self.window_combo.clear()
        self.window_combo.addItem("🪟 Windows", None)
        
        windows = self.window_manager.get_windows()
        selected_index = 0
        
        for i, window in enumerate(windows):
            title = window['title']
            display_title = title[:32] + "..." if len(title) > 35 else title
            display_text = display_title
            desktop_prefix = ""
            if window['desktop'] != -1:
                current_desktop = self.desktop_manager.current_desktop
                if window['desktop'] != current_desktop:
                    desktop_prefix = f"[{window['desktop']+1}] "
                    display_text = f"{desktop_prefix}{display_title}"
            
            index = self.window_combo.count()
            self.window_combo.addItem(display_text, window)
            tooltip = f"{desktop_prefix}{window['name']}\nDesktop: {window['desktop']+1 if window['desktop'] >= 0 else 'All'}"
            self.window_combo.setItemData(index, tooltip, Qt.ToolTipRole)
            
            if current_id and window['id'] == current_id:
                selected_index = index
        
        self.window_combo.setCurrentIndex(selected_index)
        self.window_combo.blockSignals(False)
    
    def on_window_selected(self, index):
        if index <= 0:
            return
        
        window = self.window_combo.itemData(index)
        if window and 'id' in window:
            self.window_combo.setStyleSheet("""
                QComboBox {
                    background-color: #666666;
                    color: white;
                    border: none;
                    padding: 2px 5px;
                    font-size: 11px;
                    min-width: 120px;
                    max-width: 200px;
                }
            """)
            
            success = self.window_manager.activate_window(window['id'])
            self.window_combo.setCurrentIndex(0)
            
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, self._reset_window_combo_style)
    
    def _reset_window_combo_style(self):
        self.window_combo.setStyleSheet("""
            QComboBox {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 2px 5px;
                font-size: 11px;
                min-width: 120px;
                max-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666666;
                selection-background-color: #666666;
            }
        """)
    
    def load_gadgets(self):
        from src.gadgets_pyqt5 import GadgetManager
        
        while self.gadgets_layout.count():
            item = self.gadgets_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not hasattr(self, 'gadget_manager') or self.gadget_manager is None:
            self.gadget_manager = GadgetManager()
        
        self._gadget_buttons = {}
        enabled = self.gadget_manager.get_enabled_gadgets()
        
        for gadget in enabled:
            btn = QPushButton(gadget.get_icon())
            btn.setFixedSize(40, 22)
            btn.setToolTip(gadget.get_tooltip())
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a4a4a;
                    color: white;
                    border: none;
                    padding: 2px 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            btn._gadget = gadget
            btn.clicked.connect(self._on_gadget_clicked)
            self.gadgets_layout.addWidget(btn)
            self._gadget_buttons[gadget.get_name()] = btn
            gadget.set_panel(self)
        
        self.gadgets_frame.update()
        self.gadgets_frame.show()
    
    def refresh_gadget_icon(self, gadget):
        if hasattr(self, '_gadget_buttons') and gadget.get_name() in self._gadget_buttons:
            btn = self._gadget_buttons[gadget.get_name()]
            btn.setText(gadget.get_icon())
            btn.setToolTip(gadget.get_tooltip())
    
    def _on_gadget_clicked(self):
        btn = self.sender()
        if btn and hasattr(btn, '_gadget'):
            try:
                btn._gadget.on_click()
            except Exception as e:
                print(f"Error in gadget click: {e}", flush=True)
                import traceback
                traceback.print_exc()
    
    def update_time(self):
        date_part = ""
        time_part = ""
        
        now = datetime.now()
        
        if self.datetime_config.get("show_time", True):
            if self.datetime_config.get("time_format") == "12h":
                if self.datetime_config.get("show_seconds"):
                    time_part = now.strftime("%I:%M:%S %p")
                else:
                    time_part = now.strftime("%I:%M %p")
            else:
                if self.datetime_config.get("show_seconds"):
                    time_part = now.strftime("%H:%M:%S")
                else:
                    time_part = now.strftime("%H:%M")
        
        if self.datetime_config.get("show_date", False):
            date_format = self.datetime_config.get("date_format", "%Y-%m-%d")
            try:
                date_part = now.strftime(date_format)
            except:
                date_part = now.strftime("%Y-%m-%d")
        
        order = self.datetime_config.get("order", "date_time")
        if order == "time_date":
            parts = [p for p in [time_part, date_part] if p]
        else:
            parts = [p for p in [date_part, time_part] if p]
        
        display_text = " ".join(parts)
        self.time_label.setText(display_text)
    
    def switch_desktop(self, desktop_id):
        self.desktop_manager.switch_to_desktop(desktop_id)
        self.update_window_list()
    
    def on_desktop_changed(self, desktop_id):
        self.update_desktop_buttons()
        self.update_window_list()
    
    def update_desktop_buttons(self):
        current = self.desktop_manager.current_desktop
        for i, btn in enumerate(self.desktop_buttons):
            btn.setChecked(i == current)
            if i == current:
                btn.setStyleSheet("background-color: #666666; font-weight: bold;")
            else:
                btn.setStyleSheet("background-color: #4a4a4a;")
    
    def build_menus_menu(self):
        menu = QMenu(self)
        
        menu.setStyleSheet("""
            QMenu {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 3px;
                color: #333333;
            }
            QMenu::item:selected {
                background-color: #4a90d9;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #cccccc;
                margin: 5px 0px;
            }
        """)
        
        menus = self.menu_manager.load_menus()
        
        for menu_data in menus:
            menu_name = menu_data.get("name")
            menu_type = menu_data.get("type")
            
            if menu_type == "xdgmenumaker":
                xdg_menu = self.menu_manager._generate_xdg_menu(menu_data)
                submenu = menu.addMenu(menu_name)
                for action in xdg_menu.actions():
                    if action.menu():
                        new_submenu = submenu.addMenu(action.text())
                        for subaction in action.menu().actions():
                            new_submenu.addAction(subaction)
                    elif action.isSeparator():
                        submenu.addSeparator()
                    else:
                        submenu.addAction(action)
            elif menu_type == "script":
                action = menu.addAction(menu_name)
                script_path = menu_data.get("path", "")
                venv_path = menu_data.get("venv", "")
                action.triggered.connect(
                    lambda checked, p=script_path, v=venv_path: 
                    self.menu_manager._run_script(p, v)
                )
            elif menu_type == "leaf":
                # Leaf menu - open content window
                action = menu.addAction(menu_name)
                action.triggered.connect(
                    lambda checked, m=menu_data: self.menu_manager._open_leaf_menu(m)
                )
            elif menu_type == "branch":
                # Branch menu - create submenu with items
                submenu = menu.addMenu(menu_name)
                self._populate_submenu(submenu, menu_data.get("items", []))
            elif menu_type == "separator":
                menu.addSeparator()
        
        menu.addSeparator()
        
        refresh_action = menu.addAction("🔄 Refresh Menus")
        refresh_action.triggered.connect(self._refresh_menus)
        
        return menu
    
    def _populate_submenu(self, menu, items):
        """Recursively populate a submenu with items"""
        for item in items:
            item_name = item.get("name")
            item_type = item.get("type")
            
            if item_type == "separator":
                menu.addSeparator()
            elif item_type == "branch":
                # Nested submenu
                submenu = menu.addMenu(item_name)
                self._populate_submenu(submenu, item.get("items", []))
            elif item_type == "xdgmenumaker":
                # Generate XDG menu dynamically
                xdg_menu = self.menu_manager._generate_xdg_menu(item)
                for action in xdg_menu.actions():
                    if action.menu():
                        new_submenu = menu.addMenu(action.text())
                        for subaction in action.menu().actions():
                            new_submenu.addAction(subaction)
                    elif action.isSeparator():
                        menu.addSeparator()
                    else:
                        menu.addAction(action)
            elif item_type == "script":
                action = menu.addAction(item_name)
                script_path = item.get("path", "")
                venv_path = item.get("venv", "")
                action.triggered.connect(
                    lambda checked, p=script_path, v=venv_path: 
                    self.menu_manager._run_script(p, v)
                )
            elif item_type == "leaf":
                action = menu.addAction(item_name)
                action.triggered.connect(
                    lambda checked, m=item: self.menu_manager._open_leaf_menu(m)
                )
    
    def _refresh_menus(self):
        self.menus_button.setMenu(self.build_menus_menu())
    
    def on_config_selected(self, index):
        if index <= 0:
            return
        
        text = self.config_combo.currentText()
        self.config_combo.setCurrentIndex(0)
        
        if text == "Manage Gadgets":
            self.show_gadget_manager()
        elif text == "Panel Settings":
            self.show_panel_settings()
        elif text == "Menu Settings":
            self.show_menu_settings()
        elif text == "Date/Time Settings":
            self.show_datetime_settings()
        elif text == "About KosDWM":
            self.show_about()
    
    def show_gadget_manager(self):
        from src.gadgets_pyqt5 import GadgetManagerDialog
        dialog = GadgetManagerDialog(self)
        dialog.gadgets_changed.connect(self.load_gadgets)
        dialog.exec_()
    
    def show_panel_settings(self):
        from src.panel_config_pyqt5 import PanelConfigDialog
        dialog = PanelConfigDialog(self)
        dialog.config_saved.connect(self.reload_monitor_config)
        dialog.exec_()
    
    def show_menu_settings(self):
        from src.menu_config_pyqt5 import MenuConfigDialog
        dialog = MenuConfigDialog(self)
        dialog.menus_changed.connect(self._refresh_menus)
        dialog.exec_()
    
    def show_datetime_settings(self):
        from src.datetime_config_pyqt5 import DateTimeConfigDialog
        dialog = DateTimeConfigDialog(self)
        dialog.config_saved.connect(self.reload_datetime_config)
        dialog.exec_()
    
    def show_about(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About KosDWM",
            "<h2>KosDWM Panel</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A lightweight desktop panel for KosDWM window manager.</p>"
            "<p>Built with PyQt5</p>"
        )
    
    def create_clone(self, monitor):
        from PyQt5.QtWidgets import QMainWindow
        
        clone_window = QMainWindow()
        clone_window.setWindowTitle(f"KosDWM Panel - Monitor {monitor['index']}")
        clone_window.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        
        clone_panel = Panel(parent=clone_window, is_clone=True)
        clone_window.setCentralWidget(clone_panel)
        
        clone_window.setGeometry(
            monitor['x'], 0,
            monitor['width'], 30
        )
        
        clone_window.show()
        self.clone_windows.append(clone_window)
        
        return clone_window
    
    def closeEvent(self, event):
        self.api.stop()
        for clone in self.clone_windows:
            clone.close()
        event.accept()
