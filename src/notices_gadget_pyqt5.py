#!/usr/bin/env python3
"""
Notices Gadget for KosDWM PyQt5
"""

import json
import uuid
import sys
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox, QInputDialog, QDialog, QVBoxLayout, QListWidget, QPushButton, QApplication
from PyQt5.QtCore import QTimer

# Import GadgetBase - add parent dir to path first
sys.path.insert(0, str(Path(__file__).parent))
from gadgets_pyqt5 import GadgetBase


class Notice:
    """Represents a single notice/reminder"""
    
    def __init__(self, title, content="", due_date=None, priority="medium"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.content = content
        self.due_date = due_date
        self.priority = priority
        self.completed = False
        self.created = datetime.now()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "completed": self.completed,
            "created": self.created.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        notice = cls(data["title"], data.get("content", ""))
        notice.id = data.get("id", str(uuid.uuid4()))
        notice.priority = data.get("priority", "medium")
        notice.completed = data.get("completed", False)
        
        if data.get("due_date"):
            notice.due_date = datetime.fromisoformat(data["due_date"])
        
        return notice


class NoticesStore:
    """Manages notices storage"""
    
    def __init__(self):
        self.notices = []
        self.file_path = Path.home() / ".config" / "KosDWM" / "notices.json"
        self.load()
    
    def load(self):
        """Load notices from file"""
        if self.file_path.exists():
            try:
                with open(self.file_path) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.notices = [Notice.from_dict(n) for n in data]
            except Exception as e:
                print(f"Error loading notices: {e}")
    
    def save(self):
        """Save notices to file"""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump([n.to_dict() for n in self.notices], f, indent=2)
        except Exception as e:
            print(f"Error saving notices: {e}")
    
    def add(self, notice):
        """Add a new notice"""
        self.notices.append(notice)
        self.save()
    
    def remove(self, notice_id):
        """Remove a notice by ID"""
        self.notices = [n for n in self.notices if n.id != notice_id]
        self.save()
    
    def get_active(self):
        """Get active (not completed) notices"""
        return [n for n in self.notices if not n.completed]
    
    def get_overdue(self):
        """Get overdue notices"""
        now = datetime.now()
        return [n for n in self.notices if n.due_date and n.due_date < now and not n.completed]


class NoticesGadget(GadgetBase):
    """
    Notices gadget for managing reminders
    """
    
    def __init__(self):
        super().__init__()
        self.store = NoticesStore()
        self.active_count = len(self.store.get_active())
        
        # Timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_badge)
        self.timer.start(60000)  # Update every minute
    
    def get_name(self):
        return "notices"
    
    def get_icon(self):
        """Return icon with badge count"""
        active = len(self.store.get_active())
        if active > 0:
            return f"📝{active}"
        return "📝"
    
    def get_tooltip(self):
        active = len(self.store.get_active())
        overdue = len(self.store.get_overdue())
        if overdue > 0:
            return f"Notices: {active} active, {overdue} overdue"
        return f"Notices: {active} active"
    
    def get_description(self):
        return "Manage notices and reminders with due dates and priorities."
    
    def on_click(self):
        """Open notices dialog"""
        # Get parent window properly
        parent = QApplication.activeWindow()
        
        # Create dialog with proper parent and light background
        dialog = QDialog(parent)
        dialog.setWindowTitle("Notices")
        dialog.setGeometry(100, 100, 400, 300)
        
        # Light theme stylesheet
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
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
            QPushButton:pressed {
                background-color: #2a6299;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # List of notices
        list_widget = QListWidget()
        list_widget.setMinimumHeight(150)
        for notice in self.store.get_active():
            list_widget.addItem(f"{notice.title} ({notice.priority})")
        layout.addWidget(list_widget)
        
        # Add button
        add_btn = QPushButton("Add Notice")
        def add_notice():
            text, ok = QInputDialog.getText(dialog, "New Notice", "Enter notice title:")
            if ok and text:
                notice = Notice(text, priority="medium")
                self.store.add(notice)
                list_widget.addItem(f"{notice.title} ({notice.priority})")
        add_btn.clicked.connect(add_notice)
        layout.addWidget(add_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        # Show dialog
        dialog.setModal(True)
        result = dialog.exec_()
        print(f"Notices dialog closed with result: {result}")
    
    def update_badge(self):
        """Update the badge count"""
        self.active_count = len(self.store.get_active())
