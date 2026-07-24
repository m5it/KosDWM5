
"""
About Dialog for KosDWM
Dark-themed dialog showing version, credits, and system info
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About KosDWM")
        self.setFixedSize(400, 300)
        self.setup_ui()
        self.apply_dark_theme()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("KosDWM")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version from AUTOVERSION
        version = QLabel(f"Version: {self.get_version()}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Credits
        credits_text = QLabel(
            "Created by B.K., OpenCode, and contributors.\n"
            "Licensed under MIT License."
        )
        credits_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_text.setWordWrap(True)
        layout.addWidget(credits_text)
        
        # System Info
        sys_info = QLabel(self.get_system_info())
        sys_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sys_info.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(sys_info)
        
        layout.addStretch()
        
        # Close button
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
    
    def get_version(self):
        try:
            from kosdwm.version import VERSION
            return VERSION
        except ImportError:
            return "Unknown"
    
    def get_system_info(self):
        import sys
        from PyQt6.QtCore import QT_VERSION_STR
        return f"Python {sys.version.split()[0]} | Qt {QT_VERSION_STR}"
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
  