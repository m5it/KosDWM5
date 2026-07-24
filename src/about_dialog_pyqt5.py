#!/usr/bin/env python3
"""
About Dialog for KosDWM PyQt5

Dark-themed dialog showing version, credits, and system information.
"""

import sys
import platform

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AboutDialog(QDialog):
    """
    About dialog for KosDWM with dark theme styling.
    
    Displays:
    - KosDWM version (from AUTOVERSION)
    - Credits (B.K., OpenCode, etc.)
    - System info (Python version, Qt version, Platform)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KosDWM")
        self.setFixedSize(420, 340)
        self.setup_ui()
        self.apply_dark_theme()
    
    def setup_ui(self):
        """Setup the dialog UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("KosDWM")
        title_font = QFont("Arial", 22, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #4a90d9;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version_text = self.get_version()
        version = QLabel(f"Version {version_text}")
        version.setStyleSheet("color: #aaaaaa; font-size: 13px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Separator line
        separator = QLabel("─" * 30)
        separator.setStyleSheet("color: #444444;")
        separator.setAlignment(Qt.AlignCenter)
        layout.addWidget(separator)
        
        # Description
        desc = QLabel(
            "A dynamic window manager with Python-based gadget system.\n"
            "Designed for flexibility and extensibility."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cccccc; font-size: 12px;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Separator
        separator2 = QLabel("─" * 30)
        separator2.setStyleSheet("color: #444444;")
        separator2.setAlignment(Qt.AlignCenter)
        layout.addWidget(separator2)
        
        # Credits section
        credits_label = QLabel("<b>Credits</b>")
        credits_label.setStyleSheet("color: #ffffff; font-size: 13px;")
        credits_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits_label)
        
        credits = QLabel(
            "<b>Created by:</b> B.K. (kosumosu)<br><br>"
            "<b>Contributors:</b><br>"
            "OpenCode (editor + BigPickle)<br>"
            "Ollama models"
        )
        credits.setWordWrap(True)
        credits.setStyleSheet("color: #cccccc; font-size: 12px; line-height: 1.4;")
        credits.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits)
        
        layout.addStretch()
        
        # System Info
        sys_info = QLabel(self.get_system_info())
        sys_info.setWordWrap(True)
        sys_info.setStyleSheet("color: #888888; font-size: 10px;")
        sys_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(sys_info)
        
        # OK button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(80)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def get_version(self):
        """Get KosDWM version from AUTOVERSION"""
        try:
            import sys
            from pathlib import Path
            # Look for AUTOVERSION.py in parent of src directory
            current = Path(__file__).parent
            version_file = current.parent / "AUTOVERSION.py"
            if version_file.exists():
                namespace = {}
                exec(open(version_file).read(), namespace)
                return namespace.get("VERSION", "unknown")
            return "unknown"
        except Exception:
            return "unknown"
    
    def get_system_info(self):
        """Get system information string"""
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            py_version = platform.python_version()
            qt_version = QT_VERSION_STR
            plat = f"{platform.system()} {platform.release()}"
            return f"Python {py_version} | Qt {qt_version} | {plat}"
        except Exception:
            return f"Python {platform.python_version()}"
    
    def apply_dark_theme(self):
        """Apply dark theme styling consistent with other dialogs"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
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
            QPushButton:pressed {
                background-color: #6a6a6a;
            }
        """)
