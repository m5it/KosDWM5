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
            return menus
        
        # Scan each directory in Menus as a top-level menu
        for menu_dir in sorted(self.menus_dir.iterdir()):
            if menu_dir.is_dir() and menu_dir.name != '__pycache__':
                menu_data = self._scan_menu_directory(menu_dir)
                if menu_data:
                    menus.append(menu_data)
        
        return menus
    
    def _scan_menu_directory(self, directory):
        """Recursively scan a menu directory"""
        items = []
        
        for item_path in sorted(directory.iterdir()):
            if item_path.name == '__pycache__':
                continue
            
            if item_path.is_dir():
                # Check if this subfolder has config.json (leaf menu)
                config_file = item_path / "config.json"
                if config_file.exists():
                    # Leaf menu - add as clickable item
                    try:
                        with open(config_file) as f:
                            config = json.load(f)
                        items.append({
                            "name": item_path.name,
                            "type": "leaf",
                            "config": config,
                            "path": item_path
                        })
                    except Exception as e:
                        print(f"Error loading config {config_file}: {e}")
                else:
                    # Branch menu - recurse
                    submenu = self._scan_menu_directory(item_path)
                    if submenu:
                        submenu["name"] = item_path.name
                        submenu["type"] = "branch"
                        items.append(submenu)
            elif item_path.suffix == '.py' and item_path.name != '__init__.py':
                # Python script - add as runnable script
                items.append({
                    "name": item_path.stem,
                    "type": "script",
                    "path": str(item_path)
                })
        
        # Return as branch menu if has items
        if items:
            return {
                "name": directory.name,
                "type": "branch",
                "items": items
            }
        
        return None
    
    def _run_script(self, script_path):
        """Run a menu script with run() function"""
        try:
            spec = importlib.util.spec_from_file_location("menu_script", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'run'):
                # Pass parent window to script
                module.run(self.parent)
            else:
                print(f"No run() function in {script_path}")
        except Exception as e:
            print(f"Error running script {script_path}: {e}")
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
        
        # Dark terminal-like theme for script output, light for content
        if script_cmd:
            dialog.setStyleSheet("""
                QDialog { background-color: #1a1a1a; }
                QTextEdit { 
                    background-color: #000000; 
                    color: #00ff00; 
                    border: none;
                    font-family: monospace;
                    font-size: 11px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                }
                QPushButton:hover { background-color: #555555; }
            """)
        else:
            dialog.setStyleSheet("""
                QDialog { background-color: #f5f5f5; }
                QTextEdit { 
                    background-color: white; 
                    color: #333333; 
                    border: 1px solid #cccccc;
                    font-family: monospace;
                    font-size: 12px;
                }
                QPushButton {
                    background-color: #4a90d9;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #357abd; }
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
            print(f"Error running ok.py: {e}")
            window.accept()
    
    def _populate_menu(self, menu, items):
        """Populate a menu with items"""
        for item in items:
            if item.get("type") == "separator":
                menu.addSeparator()
            elif item.get("type") == "branch":
                # Create nested submenu
                submenu = menu.addMenu(item["name"])
                self._populate_menu(submenu, item.get("items", []))
            elif item.get("type") == "script":
                # Python script - run with run()
                action = menu.addAction(item["name"])
                script_path = item["path"]
                action.triggered.connect(
                    lambda checked, p=script_path: self._run_script(p)
                )
            elif item.get("type") == "leaf":
                # Leaf menu - open content window with queued connection
                action = menu.addAction(item["name"])
                action.triggered.connect(
                    lambda checked, m=item: self._open_leaf_menu(m),
                    type=Qt.QueuedConnection
                )
