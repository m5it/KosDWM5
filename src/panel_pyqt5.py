#!/usr/bin/env python3
"""
Panel widget for KosDWM PyQt5 version
"""

import json
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
    
    # Signal emitted when datetime settings change
    datetime_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load datetime configuration
        self.datetime_config = self._load_datetime_config()
        
        # Height is controlled by parent window (30px)
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
        
        # Setup desktop manager
        from src.desktop_manager_pyqt5 import DesktopManager
        self.desktop_manager = DesktopManager(self)
        self.desktop_manager.desktop_changed.connect(self.on_desktop_changed)
        
        # Setup menu manager
        from src.menus_pyqt5 import MenuManager
        self.menu_manager = MenuManager(self)
        
        # Setup window manager
        from src.window_manager_pyqt5 import WindowManager
        self.window_manager = WindowManager()
        
        # Initialize Panel API server (before setup_ui so gadgets can access it)
        self.api = PanelAPI(port=8080)
        self.api.start()
        
        self.setup_ui()
        
        # Timer for clock updates - use configured interval
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(self.datetime_config.get("update_interval", 1000))
        
        # Timer for window list updates
        self.window_timer = QTimer()
        self.window_timer.timeout.connect(self.update_window_list)
        self.window_timer.start(2000)  # Update every 2 seconds
    
    def _load_datetime_config(self):
        """Load datetime configuration from panel.json"""
        default_config = {
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
        
        config_path = Path.home() / ".config" / "KosDWM" / "panel.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded = json.load(f)
                    if "datetime" in loaded:
                        default_config.update(loaded["datetime"])
                        print(f"[Panel] Loaded datetime config: {loaded['datetime']}")
            except Exception as e:
                print(f"[Panel] Error loading datetime config: {e}")
        
        return default_config
    
    def reload_datetime_config(self):
        """Reload datetime configuration and update display"""
        print("[Panel] Reloading datetime configuration")
        self.datetime_config = self._load_datetime_config()
        
        # Update timer interval
        self.timer.stop()
        self.timer.start(self.datetime_config.get("update_interval", 1000))
        
        # Update font
        font = QFont(
            self.datetime_config.get("font_family", "Arial"),
            self.datetime_config.get("font_size", 10)
        )
        if self.datetime_config.get("bold", True):
            font.setBold(True)
        self.time_label.setFont(font)
        
        # Update color
        color = self.datetime_config.get("color", "#ffffff")
        self.time_label.setStyleSheet(f"color: {color};")
        
        # Force update
        self.update_time()
        
        # Emit signal
        self.datetime_changed.emit()
    
    def setup_ui(self):
        """Setup the panel UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Left side: Menus button with dynamic menu
        self.menus_button = QPushButton("☰")
        self.menus_button.setFixedWidth(30)
        self.menus_button.setMenu(self.build_menus_menu())
        layout.addWidget(self.menus_button)
        
        # Window switcher dropdown
        self.window_combo = QComboBox()
        self.window_combo.setPlaceholderText("🪟 Windows")
        self.window_combo.setEnabled(self.window_manager.is_available())
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        layout.addWidget(self.window_combo)
        
        # Desktop buttons
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
        
        # Middle: Gadgets frame
        self.gadgets_frame = QFrame()
        self.gadgets_frame.setStyleSheet("background-color: transparent;")
        self.gadgets_layout = QHBoxLayout(self.gadgets_frame)
        self.gadgets_layout.setContentsMargins(0, 0, 0, 0)
        self.gadgets_layout.setSpacing(5)
        layout.addWidget(self.gadgets_frame)
        
        layout.addStretch()
        
        # Clock with configured font
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
        
        # Config dropdown
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
        
        # Load gadgets
        self.load_gadgets()
        
        # Set current desktop
        self.update_desktop_buttons()
        
        # Initial window list population
        self.update_window_list()
    
    def update_window_list(self):
        """Update the window switcher dropdown with current windows"""
        if not self.window_manager.is_available():
            self.window_combo.setEnabled(False)
            return
        
        self.window_combo.setEnabled(True)
        
        # Get current selection before clearing
        current_id = None
        current_index = self.window_combo.currentIndex()
        if current_index > 0:  # 0 is placeholder
            current_data = self.window_combo.itemData(current_index)
            if current_data:
                current_id = current_data.get('id')
        
        # Block signals while updating
        self.window_combo.blockSignals(True)
        self.window_combo.clear()
        
        # Add placeholder with icon
        self.window_combo.addItem("🪟 Windows", None)
        
        # Get windows and add to dropdown
        windows = self.window_manager.get_windows()
        selected_index = 0
        
        for i, window in enumerate(windows):
            # Truncate long titles
            title = window['title']
            display_title = title[:32] + "..." if len(title) > 35 else title
            
            # Add desktop number prefix if not on current desktop
            display_text = display_title
            desktop_prefix = ""
            if window['desktop'] != -1:  # -1 means sticky/all desktops
                current_desktop = self.desktop_manager.current_desktop
                if window['desktop'] != current_desktop:
                    desktop_prefix = f"[{window['desktop']+1}] "
                    display_text = f"{desktop_prefix}{display_title}"
            
            index = self.window_combo.count()
            self.window_combo.addItem(display_text, window)
            
            # Set tooltip with full info
            tooltip = f"{desktop_prefix}{window['name']}\nDesktop: {window['desktop']+1 if window['desktop'] >= 0 else 'All'}"
            self.window_combo.setItemData(index, tooltip, Qt.ToolTipRole)
            
            # Restore selection if this window was selected
            if current_id and window['id'] == current_id:
                selected_index = index
        
        # Restore selection
        self.window_combo.setCurrentIndex(selected_index)
        self.window_combo.blockSignals(False)
    
    def on_window_selected(self, index):
        """Handle window selection from dropdown"""
        if index <= 0:  # Placeholder selected
            return
        
        window = self.window_combo.itemData(index)
        if window and 'id' in window:
            # Visual feedback - briefly highlight the combo
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
            
            # Activate the window
            success = self.window_manager.activate_window(window['id'])
            
            # Reset to placeholder after activation
            self.window_combo.setCurrentIndex(0)
            
            # Reset style after a short delay
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, self._reset_window_combo_style)
    
    def _reset_window_combo_style(self):
        """Reset window combo to normal style"""
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
        """Load gadgets into the panel"""
        from src.gadgets_pyqt5 import GadgetManager
        
        # Clear existing gadgets
        while self.gadgets_layout.count():
            item = self.gadgets_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create gadget manager and store as instance variable for config access
        if not hasattr(self, 'gadget_manager') or self.gadget_manager is None:
            self.gadget_manager = GadgetManager()
        
        # Store gadget->button mapping for refresh
        self._gadget_buttons = {}
        
        # Debug: print how many gadgets we're loading
        enabled = self.gadget_manager.get_enabled_gadgets()
        print(f"[Panel] Loading {len(enabled)} gadgets")
        
        # Add enabled gadgets - pass panel reference so gadgets can access API
        for gadget in enabled:
            print(f"[Panel] Adding gadget: {gadget.get_name()} with icon {gadget.get_icon()}")
            btn = QPushButton(gadget.get_icon())
            btn.setFixedSize(40, 22)
            btn.setToolTip(gadget.get_tooltip())
            # Make button visible and styled
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
            # Store gadget reference on button to avoid lambda capture issues
            btn._gadget = gadget
            btn.clicked.connect(self._on_gadget_clicked)
            self.gadgets_layout.addWidget(btn)
            # Store mapping
            self._gadget_buttons[gadget.get_name()] = btn
            # Set panel reference on gadget for refresh notifications and API access
            gadget.set_panel(self)
        
        # Force layout update
        self.gadgets_frame.update()
        self.gadgets_frame.show()
        print(f"[Panel] Gadgets loaded: {list(self._gadget_buttons.keys())}")
    
    def refresh_gadget_icon(self, gadget):
        """Refresh icon for a specific gadget"""
        if hasattr(self, '_gadget_buttons') and gadget.get_name() in self._gadget_buttons:
            btn = self._gadget_buttons[gadget.get_name()]
            btn.setText(gadget.get_icon())
            btn.setToolTip(gadget.get_tooltip())
    
    def _on_gadget_clicked(self):
        """Handle gadget button click"""
        btn = self.sender()
        if btn and hasattr(btn, '_gadget'):
            try:
                btn._gadget.on_click()
            except Exception as e:
                print(f"Error in gadget click: {e}")
                import traceback
                traceback.print_exc()
    
    def update_time(self):
        """Update the clock with configured format"""
        parts = []
        
        # Get current datetime
        now = datetime.now()
        
        # Build time string if enabled
        if self.datetime_config.get("show_time", True):
            if self.datetime_config.get("time_format") == "12h":
                # 12-hour format
                if self.datetime_config.get("show_seconds"):
                    time_str = now.strftime("%I:%M:%S %p")
                else:
                    time_str = now.strftime("%I:%M %p")
            else:
                # 24-hour format
                if self.datetime_config.get("show_seconds"):
                    time_str = now.strftime("%H:%M:%S")
                else:
                    time_str = now.strftime("%H:%M")
            parts.append(time_str)
        
        # Build date string if enabled
        if self.datetime_config.get("show_date", False):
            date_format = self.datetime_config.get("date_format", "%Y-%m-%d")
            try:
                date_str = now.strftime(date_format)
                parts.append(date_str)
            except:
                date_str = now.strftime("%Y-%m-%d")  # Fallback
                parts.append(date_str)
        
        # Join with space
        display_text = " ".join(parts) if parts else ""
        self.time_label.setText(display_text)
    
    def switch_desktop(self, desktop_id):
        """Switch to specified desktop"""
        self.desktop_manager.switch_to_desktop(desktop_id)
        # Update window list to show new desktop's windows
        self.update_window_list()
    
    def on_desktop_changed(self, desktop_id):
        """Handle desktop change"""
        self.update_desktop_buttons()
        self.update_window_list()
    
    def update_desktop_buttons(self):
        """Update desktop button states"""
        current = self.desktop_manager.current_desktop
        for i, btn in enumerate(self.desktop_buttons):
            btn.setChecked(i == current)
            if i == current:
                btn.setStyleSheet("background-color: #666666; font-weight: bold;")
            else:
                btn.setStyleSheet("background-color: #4a4a4a;")
    
    def build_menus_menu(self):
        """Build the dynamic menus"""
        print(f"[Panel] build_menus_menu called")
        menu = QMenu(self)
        
        # Light theme for menu
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
        # Load dynamic menus from directory structure
        menus = self.menu_manager.load_menus()
        print(f"[Panel] Loaded {len(menus)} menus from menu_manager")
        
        for menu_data in menus:
            menu_name = menu_data.get("name")
            menu_type = menu_data.get("type")
            print(f"[Panel] Processing menu: {menu_name} (type={menu_type})")
            
            if menu_type == "xdgmenumaker":
                # xdgmenumaker generates its own submenu
                print(f"[Panel]  Adding xdgmenumaker menu: {menu_name}")
                xdg_menu = self.menu_manager._generate_xdg_menu(menu_data)
                # Add as submenu
                submenu = menu.addMenu(menu_name)
                # Copy actions from xdg_menu to submenu
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
                # Script menu
                print(f"[Panel]  Adding script menu: {menu_name}")
                action = menu.addAction(menu_name)
                script_path = menu_data.get("path", "")
                venv_path = menu_data.get("venv", "")
                action.triggered.connect(
                    lambda checked, p=script_path, v=venv_path: self.menu_manager._run_script(p, v)
                )
            elif menu_type == "leaf":
                # Leaf menu
                print(f"[Panel]  Adding leaf menu: {menu_name}")
                action = menu.addAction(menu_name)
                action.triggered.connect(
                    lambda checked, m=menu_data: self.menu_manager._open_leaf_menu(m)
                )
            elif menu_type == "branch":
                # Create top-level submenu
                submenu = menu.addMenu(menu_data["name"])
                self.menu_manager._populate_menu(submenu, menu_data.get("items", []))
                print(f"[Panel]  Added branch menu: {menu_name}")
        
        menu.addSeparator()
        menu.addAction("Exit", self.window().close)
        
        return menu
    
    def on_config_selected(self, index):
        """Handle configuration dropdown selection"""
        if index < 0:
            return
        
        # Block signals temporarily to prevent re-triggering when resetting
        self.config_combo.blockSignals(True)
        self.config_combo.setCurrentIndex(-1)
        self.config_combo.blockSignals(False)
        
        # Open appropriate dialog
        if index == 0:
            self.open_gadget_config()
        elif index == 1:
            self.open_panel_config()
        elif index == 2:
            self.open_menu_config()
        elif index == 3:
            self.open_datetime_config()
        elif index == 4:
            self.open_about_dialog()
    
    def open_gadget_config(self):
        """Open gadget configuration"""
        from src.gadget_config_pyqt5 import GadgetConfigDialog
        
        dialog = GadgetConfigDialog(self.gadget_manager, self)
        if dialog.exec_():
            self.load_gadgets()
    
    def open_panel_config(self):
        """Open panel configuration"""
        from src.panel_config_pyqt5 import PanelConfigDialog
        
        dialog = PanelConfigDialog(self)
        dialog.exec_()
    
    def open_menu_config(self):
        """Open menu configuration"""
        from src.menu_config_pyqt5 import MenuConfigDialog
        
        dialog = MenuConfigDialog(self)
        # Connect signal to reload menus when changes are saved
        dialog.menus_changed.connect(self.reload_menus)
        dialog.exec_()
    
    def reload_menus(self):
        """Reload menus from disk and refresh the menu button"""
        # Clear and rebuild the menus menu
        self.menus_button.setMenu(self.build_menus_menu())
    
    def open_datetime_config(self):
        """Open date/time configuration"""
        from src.datetime_config_pyqt5 import DateTimeConfigDialog
        
        dialog = DateTimeConfigDialog(self)
        # Connect signal to reload datetime settings when changes are saved
        dialog.config_saved.connect(self.reload_datetime_config)
        dialog.exec_()
    
    def open_about_dialog(self):
        """Open About KosDWM dialog"""
        from src.about_dialog_pyqt5 import AboutDialog
        
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def closeEvent(self, event):
        """Clean up on close - stop the API server"""
        if hasattr(self, 'api') and self.api:
            self.api.stop()
        event.accept()
