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
            "<b>Created by:</b> B.K. (w4d4f4k)<br><br>"
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
                exec(version_file.read_text(), namespace)
                return namespace.get("VERSION", "unknown")
            return "unknown"
        except Exception as e:
            return f"unknown ({e})"
    
    def get_system_info(self):
        """Get system information"""
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            qt_version = QT_VERSION_STR
        except:
            qt_version = "unknown"
        
        return (
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} | "
            f"Qt {qt_version} | "
            f"{platform.system()} {platform.release()}"
        )
    
    def apply_dark_theme(self):
        """Apply dark theme styling to the dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                border: 1px solid #444444;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5aa0e9;
            }
            QPushButton:pressed {
                background-color: #3a80c9;
            }
        """)
