#!/usr/bin/env python3
"""
Notices Gadget for KosDWM PyQt5
"""

import json
import uuid
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QMessageBox, QInputDialog, QDialog, QVBoxLayout, QListWidget, 
    QListWidgetItem, QPushButton, QApplication, QLabel, QHBoxLayout, 
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, 
    QToolBar, QColorDialog, QFontComboBox, QSpinBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QColor

# Import GadgetBase - add parent dir to path first
sys.path.insert(0, str(Path(__file__).parent))
from gadgets_pyqt5 import GadgetBase


def strip_html(html):
    """Strip HTML tags from text for plain text display"""
    if not html:
        return ""
    # Remove style and script blocks first
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    # Clean up whitespace
    return ' '.join(text.split())


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


class RichTextEditorDialog(QDialog):
    """Dialog with rich text editor for notice content"""
    
    def __init__(self, parent=None, title="", content="", priority="medium", due_date=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Notice" if not title else f"Edit: {title}")
        self.setGeometry(100, 100, 600, 500)
        
        self.initial_title = title
        self.initial_content = content
        self.initial_priority = priority
        self.initial_due_date = due_date
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title input
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit(self.initial_title)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # Toolbar for formatting
        toolbar = QHBoxLayout()
        
        # Bold button
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Bold")
        self.bold_btn.setFixedWidth(30)
        self.bold_btn.setStyleSheet("font-weight: bold;")
        self.bold_btn.clicked.connect(self._toggle_bold)
        toolbar.addWidget(self.bold_btn)
        
        # Italic button
        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("Italic")
        self.italic_btn.setFixedWidth(30)
        self.italic_btn.setStyleSheet("font-style: italic;")
        self.italic_btn.clicked.connect(self._toggle_italic)
        toolbar.addWidget(self.italic_btn)
        
        # Underline button
        self.underline_btn = QPushButton("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("Underline")
        self.underline_btn.setFixedWidth(30)
        self.underline_btn.setStyleSheet("text-decoration: underline;")
        self.underline_btn.clicked.connect(self._toggle_underline)
        toolbar.addWidget(self.underline_btn)
        
        toolbar.addSpacing(10)
        
        # Font size
        toolbar.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.valueChanged.connect(self._change_font_size)
        toolbar.addWidget(self.size_spin)
        
        toolbar.addSpacing(10)
        
        # Font family
        toolbar.addWidget(QLabel("Font:"))
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self._change_font)
        toolbar.addWidget(self.font_combo)
        
        toolbar.addSpacing(10)
        
        # Color picker
        self.color_btn = QPushButton("Color")
        self.color_btn.setToolTip("Text Color")
        self.color_btn.clicked.connect(self._change_color)
        toolbar.addWidget(self.color_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Rich text editor
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.setHtml(self.initial_content)
        self.editor.setMinimumHeight(200)
        layout.addWidget(self.editor)
        
        # Priority and Due date row
        options_layout = QHBoxLayout()
        
        options_layout.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high"])
        self.priority_combo.setCurrentText(self.initial_priority)
        options_layout.addWidget(self.priority_combo)
        
        options_layout.addSpacing(20)
        
        options_layout.addWidget(QLabel("Due Date:"))
        self.due_edit = QDateTimeEdit()
        if self.initial_due_date:
            self.due_edit.setDateTime(self.initial_due_date)
        else:
            self.due_edit.setDateTime(datetime.now())
        self.due_edit.setCalendarPopup(True)
        options_layout.addWidget(self.due_edit)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Connect cursor position change to update toolbar
        self.editor.cursorPositionChanged.connect(self._update_toolbar)
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QDateTimeEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
            }
            QFontComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
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
            QPushButton:checked {
                background-color: #4a90d9;
            }
        """)
    
    def _toggle_bold(self):
        if self.bold_btn.isChecked():
            self.editor.setFontWeight(QFont.Bold)
        else:
            self.editor.setFontWeight(QFont.Normal)
    
    def _toggle_italic(self):
        self.editor.setFontItalic(self.italic_btn.isChecked())
    
    def _toggle_underline(self):
        self.editor.setFontUnderline(self.underline_btn.isChecked())
    
    def _change_font_size(self, size):
        self.editor.setFontPointSize(size)
    
    def _change_font(self, font):
        self.editor.setFontFamily(font.family())
    
    def _change_color(self):
        color = QColorDialog.getColor(self.editor.textColor(), self)
        if color.isValid():
            self.editor.setTextColor(color)
    
    def _update_toolbar(self):
        """Update toolbar buttons based on current cursor format"""
        fmt = self.editor.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.underline_btn.setChecked(fmt.fontUnderline())
        self.size_spin.setValue(int(fmt.fontPointSize()) if fmt.fontPointSize() > 0 else 12)
    
    def get_data(self):
        """Return the notice data"""
        return {
            "title": self.title_edit.text(),
            "content": self.editor.toHtml(),
            "priority": self.priority_combo.currentText(),
            "due_date": self.due_edit.dateTime().toPyDateTime()
        }


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
        self.list_widget = None
        
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
        
        # Create dialog with proper parent - store as instance variable to prevent garbage collection
        self.notices_dialog = QDialog(parent)
        dialog = self.notices_dialog
        dialog.setWindowTitle("Notices")
        dialog.setGeometry(100, 100, 500, 400)
        
        # Dark theme stylesheet (consistent with other dialogs)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444444;
            }
            QListWidget::item:selected {
                background-color: #4a90d9;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
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
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("Your Notices")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(header)
        
        # List of notices
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(200)
        
        # Connect click and double-click handlers
        self.list_widget.itemClicked.connect(self._on_notice_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_notice_double_clicked)
        
        layout.addWidget(self.list_widget)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        
        # Add button
        add_btn = QPushButton("Add Notice")
        add_btn.clicked.connect(lambda: self._add_notice())
        btn_layout.addWidget(add_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_selected_notice)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Refresh the list AFTER all widgets are created
        self._refresh_notices_list()
        
        # Show dialog non-modally to prevent freezing
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()
    
    def _refresh_notices_list(self):
        """Refresh the notices list widget"""
        if self.list_widget is None:
            return
        
        self.list_widget.clear()
        
        for notice in self.store.get_active():
            # Strip HTML for list display
            plain_content = strip_html(notice.content)
            # Show title and preview of content
            item_text = notice.title
            if plain_content:
                preview = plain_content[:40] + "..." if len(plain_content) > 40 else plain_content
                item_text += f" - {preview}"
            if notice.priority != "medium":
                item_text += f" [{notice.priority}]"
            
            # Create item and set data properly
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, notice.id)
            self.list_widget.addItem(item)
    
    def _on_notice_clicked(self, item):
        """Handle single click on notice - just select the item"""
        # Selection happens automatically, no action needed
        pass
    
    def _on_notice_double_clicked(self, item):
        """Handle double click on notice - open full edit dialog"""
        notice_id = item.data(Qt.UserRole)
        if not notice_id:
            return
        
        notice = self._get_notice_by_id(notice_id)
        if not notice:
            return
        
        # Open edit dialog with rich text editor
        self._edit_notice(notice)
        self._refresh_notices_list()
    
    def _get_notice_by_id(self, notice_id):
        """Get notice by ID"""
        for notice in self.store.notices:
            if notice.id == notice_id:
                return notice
        return None
    
    def _add_notice(self):
        """Add a new notice using rich text editor"""
        parent = self.notices_dialog if hasattr(self, 'notices_dialog') else None
        editor = RichTextEditorDialog(parent)
        if editor.exec_() == QDialog.Accepted:
            data = editor.get_data()
            notice = Notice(
                title=data["title"],
                content=data["content"],
                due_date=data["due_date"],
                priority=data["priority"]
            )
            self.store.add(notice)
            self._refresh_notices_list()
            self.update_badge()
    
    def _delete_selected_notice(self):
        """Delete the selected notice"""
        if self.list_widget is None:
            return
        
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            return
        
        item = self.list_widget.item(current_row)
        notice_id = item.data(Qt.UserRole)
        
        if notice_id:
            reply = QMessageBox.question(
                self.list_widget.window(),
                "Confirm Delete",
                "Delete this notice?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.store.remove(notice_id)
                self._refresh_notices_list()
                self.update_badge()
    
    def _edit_notice(self, notice):
        """Edit an existing notice with rich text editor"""
        parent = self.notices_dialog if hasattr(self, 'notices_dialog') else None
        
        editor = RichTextEditorDialog(
            parent,
            title=notice.title,
            content=notice.content,
            priority=notice.priority,
            due_date=notice.due_date
        )
        
        if editor.exec_() == QDialog.Accepted:
            data = editor.get_data()
            notice.title = data["title"]
            notice.content = data["content"]
            notice.priority = data["priority"]
            notice.due_date = data["due_date"]
            self.store.save()
            self._refresh_notices_list()
            self.update_badge()
    
    def update_badge(self):
        """Update the badge count and refresh panel icon"""
        self.active_count = len(self.store.get_active())
        self.refresh_icon()
