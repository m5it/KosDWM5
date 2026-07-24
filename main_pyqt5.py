#!/usr/bin/env python3
"""
KosDWM - PyQt5 Version
A simple window manager built with PyQt5
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from src.panel_pyqt5 import Panel

# Global debug flag
DEBUG = False

def debug_print(*args, **kwargs):
    """Print only in debug mode"""
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)


class KosDWM(QWidget):
    """
    Main KosDWM window manager - Top panel only
    """
    
    def __init__(self):
        super().__init__()
        
        # Make it a top-level window that stays on top
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        
        # Set fixed height for panel (30px)
        self.setFixedHeight(30)
        
        # Position at top of screen, full width
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), 30)
        
        # Style
        self.setStyleSheet("background-color: #333333;")
        
        # Create panel
        self.create_panel()
        
        debug_print("KosDWM PyQt5 panel initialized")
    
    def create_panel(self):
        """Create the top panel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.panel = Panel(self)
        layout.addWidget(self.panel)
        
        # Debug: list loaded gadgets
        if DEBUG and hasattr(self.panel, 'gadget_manager'):
            debug_print("Loaded gadgets:")
            for gadget in self.panel.gadget_manager.get_enabled_gadgets():
                debug_print(f"  - {gadget.get_name()}: {gadget.get_icon()}")


def main():
    """Main entry point"""
    global DEBUG
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='KosDWM - PyQt5 Window Manager')
    parser.add_argument('-d', '--debug', action='store_true', 
                        help='Enable debug output')
    args = parser.parse_args()
    
    DEBUG = args.debug
    
    if DEBUG:
        print("[DEBUG] Debug mode enabled")
    
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Create main window (panel)
    window = KosDWM()
    window.show()
    
    print("KosDWM PyQt5 panel started!")
    print(f"Position: {window.geometry()}")
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
