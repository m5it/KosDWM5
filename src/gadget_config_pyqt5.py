#!/usr/bin/env python3
"""
Gadget Configuration Dialog for KosDWM PyQt5

Configuration dialog for enabling/disabling gadgets
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
from PyQt5.QtWidgets import QPushButton, QScrollArea, QWidget, QFrame, QMessageBox
from PyQt5.QtCore import Qt


class GadgetConfigDialog(QDialog):
    """
    Configuration dialog for enabling/disabling gadgets
    """
    
    def __init__(self, gadget_manager, parent=None):
        super().__init__(parent)
        self.gadget_manager = gadget_manager
        self.checkboxes = {}
        
        self.setWindowTitle("Gadget Configuration")
        self.setGeometry(100, 100, 600, 500)
        
        # Dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QLabel#header {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
            }
            QLabel#description {
                color: #aaaaaa;
                font-size: 13px;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #6a6a6a;
            }
            QScrollArea {
                border: 1px solid #444444;
                background-color: #2d2d2d;
            }
            QFrame#gadgetItem {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 10px;
            }
            QFrame#gadgetItem:hover {
                background-color: #3d3d3d;
                border-color: #555555;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("⚙️ Gadget Configuration")
        header.setObjectName("header")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Enable or disable gadgets to customize your panel")
        desc.setObjectName("description")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Scroll area for gadgets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for gadgets
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(10)
        container_layout.setAlignment(Qt.AlignTop)
        
        # Get available gadgets
        available = self.gadget_manager.get_all_gadgets()
        
        if not available:
            label = QLabel("No gadgets available")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #888888; font-style: italic; padding: 50px;")
            container_layout.addWidget(label)
        else:
            for gadget_name in available:
                info = self.gadget_manager.get_gadget_info(gadget_name)
                if info:
                    self._create_gadget_item(container_layout, info)
        
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        reload_btn = QPushButton("🔄 Reload")
        reload_btn.setToolTip("Reload gadgets from disk")
        reload_btn.clicked.connect(self.reload_gadgets)
        btn_layout.addWidget(reload_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_gadget_item(self, layout, info):
        """Create a widget for a single gadget"""
        frame = QFrame()
        frame.setObjectName("gadgetItem")
        frame_layout = QHBoxLayout(frame)
        frame_layout.setSpacing(10)
        
        # Checkbox for enabling
        checkbox = QCheckBox(f"{info['icon']} {info['name']}")
        checkbox.setChecked(info['enabled'])
        checkbox.setToolTip(info['description'])
        self.checkboxes[info['name']] = checkbox
        frame_layout.addWidget(checkbox)
        
        frame_layout.addStretch()
        
        # Source label
        source = info.get('source', 'unknown')
        source_label = QLabel(f"[{source}]")
        source_label.setStyleSheet("color: #888888; font-size: 11px;")
        frame_layout.addWidget(source_label)
        
        layout.addWidget(frame)
        
        # Description below
        if info.get('description'):
            desc = QLabel(info['description'])
            desc.setObjectName("description")
            desc.setWordWrap(True)
            desc.setIndent(30)  # Align with checkbox
            layout.addWidget(desc)
    
    def save_config(self):
        """Save the configuration"""
        for gadget_name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                self.gadget_manager.enable_gadget(gadget_name)
            else:
                self.gadget_manager.disable_gadget(gadget_name)
        
        self.accept()
    
    def reload_gadgets(self):
        """Reload gadgets from disk"""
        reply = QMessageBox.question(
            self,
            "Reload Gadgets",
            "This will reload all gadgets from disk. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.gadget_manager.reload_gadgets()
            # Refresh UI
            self.close()
            dialog = GadgetConfigDialog(self.gadget_manager, self.parent())
            dialog.exec_()
