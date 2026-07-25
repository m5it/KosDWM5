#!/usr/bin/env python3
"""
Menu system for KosDWM PyQt5

Auto-generates menus from directory structure in ~/.config/KosDWM/Menus/
Matches original TkInter behavior exactly
"""

import json
import subprocess
import os
import importlib.util
import glob
import re
from pathlib import Path
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer


class MenuManager:
    """
    Manages dynamic menus for KosDWM - auto-generated from directory structure
    """
    
    def __init__(self, parent=None):
        self.parent = parent
        self.menus_dir = Path.home() / ".config" / "KosDWM" / "Menus"
        self._pending_dialog = None
    
    def load_menus(self):
        """Load all menus from directory structure"""
        menus = []
        
        if not self.menus_dir.exists():
            print(f"[MenuManager] Menus directory not found: {self.menus_dir}")
            return menus
        
        print(f"[MenuManager] Loading menus from: {self.menus_dir}")
        
        # Scan each directory in Menus as a top-level menu
        for menu_dir in sorted(self.menus_dir.iterdir()):
            if menu_dir.is_dir() and menu_dir.name != '__pycache__':
                print(f"[MenuManager] Scanning menu directory: {menu_dir.name}")
                
                # Check if this directory itself has a config.json (xdgmenumaker, script, or leaf)
                config_file = menu_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file) as f:
                            config = json.load(f)
                        
                        menu_type = config.get("type", "leaf")
                        print(f"[MenuManager]  Top-level config found, type={menu_type}")
                        
                        if menu_type == "xdgmenumaker":
                            menus.append({
                                "name": menu_dir.name,
                                "type": "xdgmenumaker",
                                "config": config,
                                "path": menu_dir
                            })
                            print(f"[MenuManager]  Added xdgmenumaker menu: {menu_dir.name}")
                            continue
                        elif menu_type == "script":
                            script_path = config.get("scriptPath", "")
                            venv_path = config.get("venvPath", "")
                            menus.append({
                                "name": menu_dir.name,
                                "type": "script",
                                "path": script_path,
                                "venv": venv_path,
                                "config": config
                            })
                            print(f"[MenuManager]  Added script menu: {menu_dir.name}")
                            continue
                        elif menu_type == "leaf":
                            menus.append({
                                "name": menu_dir.name,
                                "type": "leaf",
                                "config": config,
                                "path": menu_dir
                            })
                            print(f"[MenuManager]  Added leaf menu: {menu_dir.name}")
                            continue
                    except Exception as e:
                        print(f"[MenuManager]  Error loading top-level config {config_file}: {e}")
                
                # Otherwise, scan for subdirectories as branch menu
                menu_data = self._scan_menu_directory(menu_dir)
                if menu_data:
                    item_count = len(menu_data.get('items', []))
                    print(f"[MenuManager] Loaded branch menu: {menu_data.get('name')} with {item_count} items")
                    menus.append(menu_data)
        
        print(f"[MenuManager] Total menus loaded: {len(menus)}")
        return menus
    
    def _scan_menu_directory(self, directory):
        """Recursively scan a menu directory"""
        items = []
        
        print(f"[MenuManager] _scan_menu_directory: {directory}")
        
        for item_path in sorted(directory.iterdir()):
            if item_path.name == '__pycache__':
                continue
            
            if item_path.is_dir():
                print(f"[MenuManager]  Found dir: {item_path.name}")
                # Check if this subfolder has config.json
                config_file = item_path / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file) as f:
                            config = json.load(f)
                        
                        menu_type = config.get("type", "leaf")
                        print(f"[MenuManager]   Config found, type={menu_type}")
                        
                        # Check if it's a script type config
                        if menu_type == "script":
                            # Script menu with config
                            script_path = config.get("scriptPath", "")
                            venv_path = config.get("venvPath", "")
                            items.append({
                                "name": item_path.name,
                                "type": "script",
                                "path": script_path,
                                "venv": venv_path,
                                "config": config
                            })
                            print(f"[MenuManager]   Added script item: {item_path.name}")
                        elif menu_type == "xdgmenumaker":
                            # xdgmenumaker - generates menu from XDG .desktop files
                            items.append({
                                "name": item_path.name,
                                "type": "xdgmenumaker",
                                "config": config,
                                "path": item_path
                            })
                            print(f"[MenuManager]   Added xdgmenumaker item: {item_path.name}")
                        else:
                            # Leaf menu - add as clickable item
                            items.append({
                                "name": item_path.name,
                                "type": "leaf",
                                "config": config,
                                "path": item_path
                            })
                            print(f"[MenuManager]   Added leaf item: {item_path.name}")
                    except Exception as e:
                        print(f"[MenuManager]   Error loading config {config_file}: {e}")
                else:
                    # Branch menu - recurse
                    print(f"[MenuManager]   No config, recursing as branch")
                    submenu = self._scan_menu_directory(item_path)
                    if submenu:
                        submenu["name"] = item_path.name
                        submenu["type"] = "branch"
                        items.append(submenu)
                        print(f"[MenuManager]   Added branch item: {item_path.name}")
            elif item_path.suffix == '.py' and item_path.name != '__init__.py':
                # Python script - add as runnable script
                print(f"[MenuManager]  Found .py script: {item_path.name}")
                items.append({
                    "name": item_path.stem,
                    "type": "script",
                    "path": str(item_path)
                })
        
        # Return as branch menu if has items
        if items:
            result = {
                "name": directory.name,
                "type": "branch",
                "items": items
            }
            print(f"[MenuManager] Returning branch with {len(items)} items")
            return result
        
        print(f"[MenuManager] No items found in {directory}")
        return None
    
    def _run_script(self, script_path, venv_path=None):
        """Run a Python script, optionally using a virtual environment"""
        print(f"[MenuManager] _run_script: {script_path}, venv={venv_path}")
        if not script_path or not os.path.exists(script_path):
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Script not found:\n{script_path}"
            )
            return
        
        try:
            # Determine which Python executable to use
            if venv_path and os.path.exists(os.path.join(venv_path, "bin", "python")):
                python_exe = os.path.join(venv_path, "bin", "python")
            elif venv_path and os.path.exists(os.path.join(venv_path, "Scripts", "python.exe")):
                python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            else:
                python_exe = "python3"
            
            print(f"[MenuManager] Running: {python_exe} {script_path}")
            # Run the script
            subprocess.Popen([python_exe, script_path], cwd=os.path.dirname(script_path))
            
        except Exception as e:
            print(f"[MenuManager] Error running script {script_path}: {e}")
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to run script:\n{e}"
            )
    
    def _open_leaf_menu(self, menu_data):
        """Show window with content from folder's config.json"""
        config = menu_data.get("config", {})
        path = menu_data.get("path")
        
        if not path:
            return
        
        # Use longer delay to let menu close first (prevents freeze)
        self._pending_dialog = (config, path)
        QTimer.singleShot(100, self._show_pending_dialog)
    
    def _show_pending_dialog(self):
        """Show the pending dialog"""
        if self._pending_dialog:
            config, path = self._pending_dialog
            self._show_leaf_dialog(config, path)
            self._pending_dialog = None
    
    def _show_leaf_dialog(self, config, path):
        """Actually show the leaf dialog"""
        # Get settings from config
        content_file = config.get('windowContent', '')
        script_cmd = config.get('windowScript', '')
        loop_interval = config.get('loop', 0)
        looptype = config.get('looptype', 'second')
        title = config.get('title', path.name)
        
        # Create window
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(title)
        dialog.setGeometry(100, 100, 600, 400)
        
        # Dark theme for all leaf menus
        if script_cmd:
            # Terminal-like for script output
            dialog.setStyleSheet("""
                QDialog { background-color: #1a1a1a; }
                QTextEdit { 
                    background-color: #000000; 
                    color: #00ff00; 
                    border: 1px solid #333333;
                    border-radius: 3px;
                    padding: 10px;
                    font-family: monospace;
                    font-size: 11px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
        else:
            # Dark theme for static content
            dialog.setStyleSheet("""
                QDialog { background-color: #1a1a1a; }
                QTextEdit { 
                    background-color: #2d2d2d; 
                    color: #ffffff; 
                    border: 1px solid #444444;
                    border-radius: 3px;
                    padding: 10px;
                    font-family: monospace;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Text widget
        text = QTextEdit()
        text.setReadOnly(True)
        layout.addWidget(text)
        
        # Button frame
        btn_frame = QHBoxLayout()
        btn_frame.addStretch()
        
        # Check for ok.py
        ok_script = path / "ok.py"
        if ok_script.exists():
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(lambda: self._run_ok_script(dialog, ok_script))
            btn_frame.addWidget(ok_btn)
        else:
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(dialog.accept)
            btn_frame.addWidget(ok_btn)
        
        layout.addLayout(btn_frame)
        
        # Handle script command (looping)
        if script_cmd:
            interval_ms = loop_interval * 1000 if looptype == 'second' else loop_interval
            
            def update_output():
                try:
                    result = subprocess.run(
                        script_cmd, 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        timeout=10
                    )
                    text.clear()
                    text.setText(result.stdout if result.stdout else result.stderr)
                except Exception as e:
                    text.clear()
                    text.setText(str(e))
                
                # Schedule next update if window still exists and looping enabled
                if dialog.isVisible() and loop_interval > 0:
                    QTimer.singleShot(interval_ms, update_output)
            
            # Initial run
            update_output()
        else:
            # Static content
            if content_file:
                full_path = path / content_file
                try:
                    with open(full_path, 'r') as f:
                        text.setText(f.read())
                except FileNotFoundError:
                    text.setText(f"Content not found: {content_file}")
                except Exception as e:
                    text.setText(f"Error reading content: {e}")
        
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
    
    def _run_ok_script(self, window, script_path):
        """Run ok.py script and close window"""
        try:
            spec = importlib.util.spec_from_file_location("ok_script", str(script_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'run'):
                module.run(window)
            else:
                window.accept()
        except Exception as e:
            print(f"[MenuManager] Error running ok.py: {e}")
            window.accept()
    
    def _generate_xdg_menu(self, menu_data):
        """Generate menu from XDG .desktop files like OpenBox"""
        print(f"[MenuManager] _generate_xdg_menu called for: {menu_data.get('name')}")
        config = menu_data.get("config", {})
        path = menu_data.get("path")
        
        # Create a menu that will be populated with XDG apps
        menu = QMenu(self.parent)
        
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
        
        # Get categories to organize apps
        categories = {}
        
        # Scan XDG application directories
        xdg_dirs = [
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path.home() / ".local/share/applications"
        ]
        
        print(f"[MenuManager]  Scanning XDG dirs: {xdg_dirs}")
        
        for xdg_dir in xdg_dirs:
            if not xdg_dir.exists():
                print(f"[MenuManager]   Skipping non-existent: {xdg_dir}")
                continue
            
            desktop_files = list(xdg_dir.glob("*.desktop"))
            print(f"[MenuManager]   Found {len(desktop_files)} .desktop files in {xdg_dir}")
            
            for desktop_file in desktop_files:
                try:
                    app_info = self._parse_desktop_file(desktop_file)
                    if app_info and app_info.get("NoDisplay") != "true":
                        category = app_info.get("Categories", "Other").split(";")[0] or "Other"
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(app_info)
                        print(f"[MenuManager]    Added app: {app_info.get('Name')} in {category}")
                    else:
                        print(f"[MenuManager]    Skipped (NoDisplay): {desktop_file.name}")
                except Exception as e:
                    print(f"[MenuManager]    Error parsing {desktop_file}: {e}")
        
        print(f"[MenuManager]  Categories found: {list(categories.keys())}")
        
        # Sort categories and add to menu
        for category in sorted(categories.keys()):
            apps = categories[category]
            apps.sort(key=lambda x: x.get("Name", "").lower())
            
            submenu = menu.addMenu(category)
            print(f"[MenuManager]  Added category: {category} with {len(apps)} apps")
            for app in apps:
                action = submenu.addAction(app.get("Name", "Unknown"))
                action.setIcon(self.parent.style().standardIcon(self.parent.style().SP_ComputerIcon))
                action.triggered.connect(lambda checked, a=app: self._launch_xdg_app(a))
        
        return menu
    
    def _parse_desktop_file(self, desktop_path):
        """Parse a .desktop file and return app info"""
        info = {}
        with open(desktop_path, 'r', encoding='utf-8', errors='ignore') as f:
            in_entry = False
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_entry = True
                    continue
                if line.startswith('[') and line.endswith(']'):
                    in_entry = False
                    continue
                if in_entry and '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value
        return info
    
    def _launch_xdg_app(self, app_info):
        """Launch an XDG application"""
        print(f"[MenuManager] _launch_xdg_app: {app_info.get('Name')}")
        try:
            exec_cmd = app_info.get("Exec", "")
            if exec_cmd:
                # Remove field codes like %f, %F, %u, %U, etc.
                exec_cmd = re.sub(r'%[fFuUdDnNickvm]', '', exec_cmd).strip()
                
                # Run in terminal if needed
                if app_info.get("Terminal") == "true":
                    print(f"[MenuManager]  Running in terminal: xterm -e {exec_cmd}")
                    subprocess.Popen(["xterm", "-e", exec_cmd])
                else:
                    print(f"[MenuManager]  Running: {exec_cmd}")
                    subprocess.Popen(exec_cmd, shell=True)
        except Exception as e:
            print(f"[MenuManager] Error launching app: {e}")
            QMessageBox.critical(
                self.parent,
                "Error",
                f"Failed to launch {app_info.get('Name', 'application')}:\n{e}"
            )
    
    def _populate_menu(self, menu, items):
        """Populate a menu with items"""
        print(f"[MenuManager] _populate_menu with {len(items)} items")
        for item in items:
            item_type = item.get("type")
            item_name = item.get("name")
            print(f"[MenuManager]  Processing: {item_name} (type={item_type})")
            
            if item_type == "separator":
                menu.addSeparator()
            elif item_type == "branch":
                # Create nested submenu
                submenu = menu.addMenu(item_name)
                self._populate_menu(submenu, item.get("items", []))
            elif item_type == "xdgmenumaker":
                # Generate XDG menu dynamically
                print(f"[MenuManager]   Generating xdgmenumaker for: {item_name}")
                xdg_menu = self._generate_xdg_menu(item)
                # Copy actions from xdg_menu to current menu
                for action in xdg_menu.actions():
                    if action.menu():
                        # It's a submenu (category)
                        new_submenu = menu.addMenu(action.text())
                        for subaction in action.menu().actions():
                            new_submenu.addAction(subaction)
                    elif action.isSeparator():
                        menu.addSeparator()
                    else:
                        menu.addAction(action)
                print(f"[MenuManager]   xdgmenumaker populated with {len(xdg_menu.actions())} actions")
            elif item_type == "script":
                # Python script - run with optional venv
                action = menu.addAction(item_name)
                script_path = item.get("path", "")
                venv_path = item.get("venv", "")
                action.triggered.connect(
                    lambda checked, p=script_path, v=venv_path: self._run_script(p, v)
                )
            elif item_type == "leaf":
                # Leaf menu - open content window
                action = menu.addAction(item_name)
                action.triggered.connect(
                    lambda checked, m=item: self._open_leaf_menu(m)
                )
