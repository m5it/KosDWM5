"""
Notices Store Module
====================

Handles persistent storage and CRUD operations for notices.
Notices are stored in ~/.config/KosDWM/notices.json
"""

import json
import uuid
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class Notice:
    """
    Represents a single notice with all its properties.
    """
    
    def __init__(self, 
                 title: str,
                 content: str = "",
                 due_date: Optional[datetime] = None,
                 reminder_time: Optional[datetime] = None,
                 priority: str = "medium",
                 notice_id: Optional[str] = None,
                 created_date: Optional[datetime] = None,
                 completed: bool = False):
        """
        Initialize a Notice.
        
        Args:
            title: The notice title (required)
            content: Detailed content/description
            due_date: When the notice is due (optional)
            reminder_time: When to show reminder (optional)
            priority: 'low', 'medium', or 'high'
            notice_id: Unique ID (auto-generated if not provided)
            created_date: Creation timestamp (auto-generated if not provided)
            completed: Whether the notice is completed
        """
        self.id = notice_id or str(uuid.uuid4())
        self.title = title
        self.content = content
        self.created_date = created_date or datetime.now()
        self.due_date = due_date
        self.reminder_time = reminder_time
        self.priority = priority if priority in ("low", "medium", "high") else "medium"
        self.completed = completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notice to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None,
            "priority": self.priority,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notice':
        """Create Notice from dictionary."""
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            notice_id=data.get("id"),
            created_date=datetime.fromisoformat(data["created_date"]) if data.get("created_date") else None,
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            reminder_time=datetime.fromisoformat(data["reminder_time"]) if data.get("reminder_time") else None,
            priority=data.get("priority", "medium"),
            completed=data.get("completed", False)
        )
    
    def is_overdue(self) -> bool:
        """Check if notice is overdue."""
        if self.completed or not self.due_date:
            return False
        return datetime.now() > self.due_date
    
    def is_due_today(self) -> bool:
        """Check if notice is due today."""
        if self.completed or not self.due_date:
            return False
        today = datetime.now().date()
        return self.due_date.date() == today
    
    def is_upcoming(self, days: int = 7) -> bool:
        """Check if notice is due within specified days."""
        if self.completed or not self.due_date:
            return False
        future = datetime.now() + timedelta(days=days)
        return datetime.now() <= self.due_date <= future
    
    def is_reminder_due(self) -> bool:
        """Check if reminder time has been reached."""
        if self.completed or not self.reminder_time:
            return False
        return datetime.now() >= self.reminder_time
    
    def __repr__(self) -> str:
        return f"Notice(id={self.id[:8]}, title='{self.title[:30]}', completed={self.completed})"


class NoticesStore:
    """
    Manages persistent storage of notices with thread-safe operations.
    """
    
    def __init__(self):
        self._data_path = Path.home() / ".config" / "KosDWM" / "notices.json"
        self._notices: Dict[str, Notice] = {}
        self._lock = threading.RLock()
        self._ensure_directory()
        self._load()
    
    def _ensure_directory(self):
        """Ensure the config directory exists."""
        try:
            self._data_path.parent.mkdir(parents=True, exist_ok=True)
        except IOError as e:
            print(f"Error creating notices directory: {e}")
    
    def _load(self):
        """Load notices from JSON file."""
        if not self._data_path.exists():
            self._notices = {}
            return
        
        try:
            with open(self._data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self._lock:
                self._notices = {}
                for item in data.get("notices", []):
                    try:
                        notice = Notice.from_dict(item)
                        self._notices[notice.id] = notice
                    except Exception as e:
                        print(f"Error loading notice: {e}")
            
            print(f"Loaded {len(self._notices)} notices")
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading notices file: {e}")
            self._notices = {}
    
    def _save(self):
        """Save notices to JSON file."""
        try:
            with self._lock:
                data = {
                    "notices": [n.to_dict() for n in self._notices.values()],
                    "last_saved": datetime.now().isoformat()
                }
            
            with open(self._data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except IOError as e:
            print(f"Error saving notices: {e}")
            raise
    
    # CRUD Operations
    
    def create(self, title: str, **kwargs) -> Notice:
        """
        Create a new notice.
        
        Args:
            title: Notice title (required)
            **kwargs: Other notice fields (content, due_date, reminder_time, priority)
        
        Returns:
            The created Notice object
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        notice = Notice(title=title.strip(), **kwargs)
        
        with self._lock:
            self._notices[notice.id] = notice
        
        self._save()
        return notice
    
    def get(self, notice_id: str) -> Optional[Notice]:
        """Get a notice by ID."""
        with self._lock:
            return self._notices.get(notice_id)
    
    def get_all(self) -> List[Notice]:
        """Get all notices."""
        with self._lock:
            return list(self._notices.values())
    
    def update(self, notice_id: str, **kwargs) -> Optional[Notice]:
        """
        Update a notice.
        
        Args:
            notice_id: ID of notice to update
            **kwargs: Fields to update
        
        Returns:
            Updated Notice or None if not found
        """
        with self._lock:
            notice = self._notices.get(notice_id)
            if not notice:
                return None
            
            for key, value in kwargs.items():
                if hasattr(notice, key):
                    setattr(notice, key, value)
        
        self._save()
        return self.get(notice_id)
    
    def delete(self, notice_id: str) -> bool:
        """
        Delete a notice.
        
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if notice_id not in self._notices:
                return False
            del self._notices[notice_id]
        
        self._save()
        return True
    
    def mark_completed(self, notice_id: str, completed: bool = True) -> Optional[Notice]:
        """Mark a notice as completed or uncompleted."""
        return self.update(notice_id, completed=completed)
    
    # Query Operations
    
    def get_active(self) -> List[Notice]:
        """Get all non-completed notices."""
        with self._lock:
            return [n for n in self._notices.values() if not n.completed]
    
    def get_completed(self) -> List[Notice]:
        """Get all completed notices."""
        with self._lock:
            return [n for n in self._notices.values() if n.completed]
    
    def get_overdue(self) -> List[Notice]:
        """Get overdue notices."""
        with self._lock:
            return [n for n in self._notices.values() if n.is_overdue()]
    
    def get_due_today(self) -> List[Notice]:
        """Get notices due today."""
        with self._lock:
            return [n for n in self._notices.values() if n.is_due_today()]
    
    def get_upcoming(self, days: int = 7) -> List[Notice]:
        """Get notices due within specified days."""
        with self._lock:
            return [n for n in self._notices.values() if n.is_upcoming(days)]
    
    def get_by_priority(self, priority: str) -> List[Notice]:
        """Get notices by priority level."""
        with self._lock:
            return [n for n in self._notices.values() if n.priority == priority]
    
    def get_reminders_due(self) -> List[Notice]:
        """Get notices with reminders that are due."""
        with self._lock:
            return [n for n in self._notices.values() if n.is_reminder_due()]
    
    def search(self, query: str) -> List[Notice]:
        """
        Search notices by title or content.
        
        Args:
            query: Search string
        
        Returns:
            List of matching notices
        """
        query = query.lower()
        with self._lock:
            return [
                n for n in self._notices.values()
                if query in n.title.lower() or query in n.content.lower()
            ]
    
    # Statistics
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about notices."""
        with self._lock:
            notices = list(self._notices.values())
            return {
                "total": len(notices),
                "active": len([n for n in notices if not n.completed]),
                "completed": len([n for n in notices if n.completed]),
                "overdue": len([n for n in notices if n.is_overdue()]),
                "due_today": len([n for n in notices if n.is_due_today()]),
                "high_priority": len([n for n in notices if n.priority == "high" and not n.completed])
            }
    
    def get_count(self) -> int:
        """Get total number of notices."""
        with self._lock:
            return len(self._notices)
    
    def get_active_count(self) -> int:
        """Get count of active (non-completed) notices."""
        with self._lock:
            return len([n for n in self._notices.values() if not n.completed])
    
    # Import/Export
    
    def export_to_json(self, file_path: str):
        """Export all notices to a JSON file."""
        with self._lock:
            data = {
                "notices": [n.to_dict() for n in self._notices.values()],
                "exported": datetime.now().isoformat()
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, file_path: str, merge: bool = False):
        """
        Import notices from a JSON file.
        
        Args:
            file_path: Path to JSON file
            merge: If True, merge with existing; if False, replace all
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        imported = []
        for item in data.get("notices", []):
            try:
                notice = Notice.from_dict(item)
                # Generate new ID to avoid conflicts
                notice.id = str(uuid.uuid4())
                imported.append(notice)
            except Exception as e:
                print(f"Error importing notice: {e}")
        
        with self._lock:
            if not merge:
                self._notices.clear()
            
            for notice in imported:
                self._notices[notice.id] = notice
        
        self._save()
