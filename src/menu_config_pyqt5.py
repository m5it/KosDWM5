#!/usr/bin/env python3
"""
Menu Configuration Dialog for KosDWM PyQt5

Allows managing auto-generative menus from the Menus directory
"""

import json
import os
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit,
    QFormLayout, QGroupBox, QMessageBox, QInputDialog, QFileDialog,
    QSplitter, QWidget, QComboBox, QSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt


class MenuConfigDialog(QDialog):
    """
    Configuration dialog for managing auto-generative menus
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 Menu Configuration")
        self.setGeometry(100, 100, 800, 600)
        
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
            QPushButton#danger {
                background-color: #d9534f;
            }
            QPushButton#danger:hover {
                background-color: #c9302c;
            }
            QTreeWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            QTreeWidget::item:selected {
                background-color: #4a90d9;
                color: white;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
                font-family: monospace;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        self.menus_dir = Path.home() / ".config" / "KosDWM" / "Menus"
        self.current_item = None
        
        self.setup_ui()
        self.refresh_tree()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Auto-Generative Menu Manager")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        layout.addWidget(header)
        
        desc = QLabel("Manage menus in: " + str(self.menus_dir))
        desc.setStyleSheet("color: #666666;")
        layout.addWidget(desc)
        
        # Splitter for tree and editor
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Tree view
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Menu Structure")
        self.tree.setMinimumWidth(250)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.tree)
        
        # Tree buttons
        tree_btn_layout = QHBoxLayout()
        
        new_menu_btn = QPushButton("➕ New Menu")
        new_menu_btn.clicked.connect(self.new_menu)
        tree_btn_layout.addWidget(new_menu_btn)
        
        new_folder_btn = QPushButton("📁 New Folder")
        new_folder_btn.clicked.connect(self.new_folder)
        tree_btn_layout.addWidget(new_folder_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_item)
        tree_btn_layout.addWidget(delete_btn)
        
        left_layout.addLayout(tree_btn_layout)
        
        splitter.addWidget(left_widget)
        
        # Right side - Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Editor group
        self.editor_group = QGroupBox("Menu Item Editor")
        editor_layout = QVBoxLayout(self.editor_group)
        
        # Form for config
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Menu name")
        form_layout.addRow("Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Branch (submenu)", "Leaf (content window)", "Script (.py file)"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addRow("Type:", self.type_combo)
        
        # Leaf config
        self.leaf_group = QGroupBox("Leaf Menu Configuration")
        leaf_layout = QFormLayout(self.leaf_group)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Window title")
        leaf_layout.addRow("Window Title:", self.title_edit)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText("content.html")
        leaf_layout.addRow("Content File:", self.content_edit)
        
        self.script_edit = QLineEdit()
        self.script_edit.setPlaceholderText("lsof -i")
        leaf_layout.addRow("Window Script:", self.script_edit)
        
        self.loop_spin = QSpinBox()
        self.loop_spin.setRange(0, 3600)
        self.loop_spin.setValue(0)
        self.loop_spin.setSuffix(" seconds")
        leaf_layout.addRow("Loop Interval:", self.loop_spin)
        
        editor_layout.addLayout(form_layout)
        editor_layout.addWidget(self.leaf_group)
        
        # Content preview
        editor_layout.addWidget(QLabel("Content Preview:"))
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Select a menu item to preview content...")
        editor_layout.addWidget(self.preview)
        
        # Save button
        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_changes)
        editor_layout.addWidget(save_btn)
        
        right_layout.addWidget(self.editor_group)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        
        reload_btn = QPushButton("🔄 Reload from Disk")
        reload_btn.clicked.connect(self.refresh_tree)
        btn_layout.addWidget(reload_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Initially disable editor
        self.editor_group.setEnabled(False)
    
    def refresh_tree(self):
        """Refresh the tree from disk"""
        self.tree.clear()
        
        if not self.menus_dir.exists():
            self.menus_dir.mkdir(parents=True)
            return
        
        # Scan directories
        for item_path in sorted(self.menus_dir.iterdir()):
            if item_path.is_dir() and item_path.name != '__pycache__':
                self._add_tree_item(self.tree.invisibleRootItem(), item_path)
        
        self.tree.expandAll()
    
    def _add_tree_item(self, parent, path):
        """Recursively add items to tree"""
        item = QTreeWidgetItem(parent)
        item.setText(0, path.name)
        item.setData(0, Qt.UserRole, str(path))
        
        # Determine type
        config_file = path / "config.json"
        if config_file.exists():
            item.setIcon(0, self.style().standardIcon(self.style().SP_DialogOpenButton))
            item.setToolTip(0, "Leaf menu (click to open window)")
        elif any(f.suffix == '.py' for f in path.iterdir() if f.is_file()):
            item.setIcon(0, self.style().standardIcon(self.style().SP_FileIcon))
            item.setToolTip(0, "Script menu")
        else:
            item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))
            item.setToolTip(0, "Branch menu (submenu)")
        
        # Recurse into subdirectories
        if path.is_dir():
            for subpath in sorted(path.iterdir()):
                if subpath.is_dir() and subpath.name != '__pycache__':
                    self._add_tree_item(item, subpath)
    
    def on_tree_item_clicked(self, item, column):
        """Handle tree item selection"""
        path_str = item.data(0, Qt.UserRole)
        if not path_str:
            return
        
        path = Path(path_str)
        self.current_item = path
        
        self.editor_group.setEnabled(True)
        self.name_edit.setText(path.name)
        
        # Determine type and load config
        config_file = path / "config.json"
        py_files = list(path.glob("*.py"))
        
        if config_file.exists():
            # Leaf menu
            self.type_combo.setCurrentIndex(1)
            try:
                with open(config_file) as f:
                    config = json.load(f)
                self.title_edit.setText(config.get("title", ""))
                self.content_edit.setText(config.get("windowContent", ""))
                self.script_edit.setText(config.get("windowScript", ""))
                self.loop_spin.setValue(config.get("loop", 0))
                
                # Show preview
                content_file = path / config.get("windowContent", "")
                if content_file.exists():
                    try:
                        with open(content_file) as f:
                            self.preview.setText(f.read()[:1000])
                    except:
                        self.preview.setText("Unable to read content file")
                else:
                    self.preview.setText("Content file not found")
            except Exception as e:
                self.preview.setText(f"Error loading config: {e}")
        elif py_files:
            # Script menu
            self.type_combo.setCurrentIndex(2)
            self.leaf_group.setVisible(False)
            self.preview.setText(f"Python script: {py_files[0].name}")
        else:
            # Branch menu
            self.type_combo.setCurrentIndex(0)
            self.leaf_group.setVisible(False)
            self.preview.setText("Branch menu (contains sub-items)")
    
    def on_type_changed(self, index):
        """Handle type change"""
        self.leaf_group.setVisible(index == 1)  # Show only for leaf
    
    def new_menu(self):
        """Create a new top-level menu"""
        name, ok = QInputDialog.getText(self, "New Menu", "Enter menu name:")
        if ok and name:
            new_path = self.menus_dir / name
            try:
                new_path.mkdir(parents=True)
                self.refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create menu:\n{e}")
    
    def new_folder(self):
        """Create a new folder in selected menu"""
        current = self.tree.currentItem()
        if not current:
            QMessageBox.information(self, "Info", "Select a menu first")
            return
        
        path_str = current.data(0, Qt.UserRole)
        if not path_str:
            return
        
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            new_path = Path(path_str) / name
            try:
                new_path.mkdir(parents=True)
                
                # Create default config.json for leaf menu
                config = {
                    "title": name,
                    "windowContent": "content.html"
                }
                with open(new_path / "config.json", 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Create sample content
                with open(new_path / "content.html", 'w') as f:
                    f.write(f"<h1>{name}</h1>\n<p>Content for {name}</p>\n")
                
                self.refresh_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder:\n{e}")
    
    def delete_item(self):
        """Delete selected menu item"""
        current = self.tree.currentItem()
        if not current:
            QMessageBox.information(self, "Info", "Select an item to delete")
            return
        
        path_str = current.data(0, Qt.UserRole)
        if not path_str:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete '{current.text(0)}' and all its contents?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(path_str)
                self.refresh_tree()
                self.editor_group.setEnabled(False)
                self.preview.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{e}")
    
    def save_changes(self):
        """Save changes to config.json"""
        if not self.current_item:
            return
        
        config_file = self.current_item / "config.json"
        
        try:
            config = {
                "title": self.title_edit.text(),
                "windowContent": self.content_edit.text(),
                "windowScript": self.script_edit.text(),
                "loop": self.loop_spin.value(),
                "looptype": "second"
            }
            
            # Remove empty values
            config = {k: v for k, v in config.items() if v}
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(self, "Success", "Configuration saved!")
            self.refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")
