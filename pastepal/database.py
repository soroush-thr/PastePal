"""
Database models and operations for PastePal
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Types of clipboard content"""
    TEXT = "text"
    RICH_TEXT = "rich_text"
    IMAGE = "image"
    FILE = "file"
    FOLDER = "folder"


@dataclass
class ClipboardItem:
    """Represents a clipboard item"""
    id: Optional[int]
    content: str
    content_type: ContentType
    preview: str
    timestamp: datetime
    is_pinned: bool = False
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'content': self.content,
            'content_type': self.content_type.value,
            'preview': self.preview,
            'timestamp': self.timestamp.isoformat(),
            'is_pinned': self.is_pinned,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClipboardItem':
        """Create from dictionary loaded from database"""
        return cls(
            id=data['id'],
            content=data['content'],
            content_type=ContentType(data['content_type']),
            preview=data['preview'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            is_pinned=bool(data['is_pinned']),
            metadata=json.loads(data['metadata']) if data['metadata'] else None
        )


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "pastepal.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create clipboard_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    is_pinned BOOLEAN DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Create settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Insert default settings
            cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value) VALUES 
                ('theme', 'light'),
                ('max_history', '1000'),
                ('hotkey', 'alt+v'),
                ('paste_hotkey', 'ctrl+shift+enter')
            """)
            
            conn.commit()
    
    def add_item(self, item: ClipboardItem) -> int:
        """Add a new clipboard item"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clipboard_items 
                (content, content_type, preview, timestamp, is_pinned, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item.content,
                item.content_type.value,
                item.preview,
                item.timestamp.isoformat(),
                item.is_pinned,
                json.dumps(item.metadata) if item.metadata else None
            ))
            return cursor.lastrowid
    
    def get_items(self, limit: int = 100, search_query: str = None, 
                  include_pinned: bool = True) -> List[ClipboardItem]:
        """Get clipboard items with optional filtering"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, content, content_type, preview, timestamp, is_pinned, metadata
                FROM clipboard_items
                WHERE 1=1
            """
            params = []
            
            if search_query:
                query += " AND (preview LIKE ? OR content LIKE ?)"
                search_term = f"%{search_query}%"
                params.extend([search_term, search_term])
            
            if not include_pinned:
                query += " AND is_pinned = 0"
            
            query += " ORDER BY is_pinned DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            items = []
            for row in rows:
                item_data = {
                    'id': row[0],
                    'content': row[1],
                    'content_type': row[2],
                    'preview': row[3],
                    'timestamp': row[4],
                    'is_pinned': row[5],
                    'metadata': row[6]
                }
                items.append(ClipboardItem.from_dict(item_data))
            
            return items
    
    def pin_item(self, item_id: int, pinned: bool = True):
        """Pin or unpin an item"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clipboard_items 
                SET is_pinned = ? 
                WHERE id = ?
            """, (pinned, item_id))
            conn.commit()
    
    def delete_item(self, item_id: int):
        """Delete an item"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
            conn.commit()
    
    def clear_history(self, keep_pinned: bool = True):
        """Clear clipboard history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if keep_pinned:
                cursor.execute("DELETE FROM clipboard_items WHERE is_pinned = 0")
            else:
                cursor.execute("DELETE FROM clipboard_items")
            conn.commit()
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a setting value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value) 
                VALUES (?, ?)
            """, (key, value))
            conn.commit()
    
    def cleanup_old_items(self, max_items: int = 1000):
        """Remove old items to keep database size manageable"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get count of unpinned items
            cursor.execute("SELECT COUNT(*) FROM clipboard_items WHERE is_pinned = 0")
            unpinned_count = cursor.fetchone()[0]
            
            if unpinned_count > max_items:
                # Delete oldest unpinned items
                cursor.execute("""
                    DELETE FROM clipboard_items 
                    WHERE is_pinned = 0 
                    AND id IN (
                        SELECT id FROM clipboard_items 
                        WHERE is_pinned = 0 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                """, (unpinned_count - max_items,))
                conn.commit()
