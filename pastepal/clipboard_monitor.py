"""
Clipboard monitoring service for PastePal
"""

import time
import threading
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QClipboard
from PIL import Image
import io
import os
import win32clipboard
import win32con
from .database import DatabaseManager, ClipboardItem, ContentType


class ClipboardMonitor(QObject):
    """Monitors system clipboard for changes"""
    
    # Signal emitted when new clipboard content is detected
    clipboard_changed = pyqtSignal(ClipboardItem)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.last_content = None
        self.last_content_type = None
        self.monitoring = False
        self.monitor_thread = None
        self.check_interval = 0.5  # Check every 500ms
        
    def start_monitoring(self):
        """Start clipboard monitoring in a separate thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_clipboard()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in clipboard monitoring: {e}")
                time.sleep(1.0)
    
    def _check_clipboard(self):
        """Check if clipboard content has changed"""
        try:
            clipboard = QApplication.clipboard()
            if not clipboard:
                return
                
            # Check for text content
            text_content = clipboard.text()
            if text_content and text_content != self.last_content:
                self._process_text_content(text_content)
                self.last_content = text_content
                return
            
            # Check for image content
            image = clipboard.image()
            if not image.isNull():
                image_data = self._image_to_bytes(image)
                if image_data != self.last_content:
                    self._process_image_content(image_data)
                    self.last_content = image_data
                    return
            
            # Check for file content
            file_paths = self._get_file_paths()
            if file_paths and file_paths != self.last_content:
                self._process_file_content(file_paths)
                self.last_content = file_paths
                return
                
        except Exception as e:
            print(f"Error checking clipboard: {e}")
    
    def _process_text_content(self, text: str):
        """Process text clipboard content"""
        if not text.strip():
            return
            
        # Determine if it's rich text by checking for HTML tags
        is_rich_text = '<' in text and '>' in text
        
        content_type = ContentType.RICH_TEXT if is_rich_text else ContentType.TEXT
        preview = self._create_text_preview(text)
        
        from datetime import datetime
        item = ClipboardItem(
            id=None,
            content=text,
            content_type=content_type,
            preview=preview,
            timestamp=datetime.now(),
            metadata={'length': len(text)}
        )
        
        self._save_and_emit_item(item)
    
    def _process_image_content(self, image_data: bytes):
        """Process image clipboard content"""
        try:
            # Create a preview using PIL
            image = Image.open(io.BytesIO(image_data))
            preview = f"Image ({image.size[0]}x{image.size[1]}, {image.mode})"
            
            # Convert to base64 for storage
            import base64
            content = base64.b64encode(image_data).decode('utf-8')
            
            from datetime import datetime
            item = ClipboardItem(
                id=None,
                content=content,
                content_type=ContentType.IMAGE,
                preview=preview,
                timestamp=datetime.now(),
                metadata={
                    'width': image.size[0],
                    'height': image.size[1],
                    'mode': image.mode,
                    'format': image.format
                }
            )
            
            self._save_and_emit_item(item)
            
        except Exception as e:
            print(f"Error processing image: {e}")
    
    def _process_file_content(self, file_paths: list):
        """Process file/folder clipboard content"""
        for path in file_paths:
            if os.path.isfile(path):
                content_type = ContentType.FILE
                preview = f"File: {os.path.basename(path)}"
            elif os.path.isdir(path):
                content_type = ContentType.FOLDER
                preview = f"Folder: {os.path.basename(path)}"
            else:
                continue
            
            from datetime import datetime
            item = ClipboardItem(
                id=None,
                content=path,
                content_type=content_type,
                preview=preview,
                timestamp=datetime.now(),
                metadata={'path': path, 'exists': os.path.exists(path)}
            )
            
            self._save_and_emit_item(item)
    
    def _create_text_preview(self, text: str, max_length: int = 100) -> str:
        """Create a preview of text content"""
        # Remove HTML tags for preview
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Replace newlines with spaces
        clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
        
        # Truncate if too long
        if len(clean_text) > max_length:
            return clean_text[:max_length] + "..."
        return clean_text
    
    def _image_to_bytes(self, image) -> bytes:
        """Convert QImage to bytes"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _get_file_paths(self) -> list:
        """Get file paths from clipboard"""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                data = win32clipboard.GetClipboardData(win32con.CF_HDROP)
                return list(data)
            return []
        except:
            return []
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
    
    def _save_and_emit_item(self, item: ClipboardItem):
        """Save item to database and emit signal"""
        try:
            item.id = self.db_manager.add_item(item)
            self.clipboard_changed.emit(item)
            
            # Cleanup old items
            max_items = int(self.db_manager.get_setting('max_history', '1000'))
            self.db_manager.cleanup_old_items(max_items)
            
        except Exception as e:
            print(f"Error saving clipboard item: {e}")
    
    def get_clipboard_content(self) -> Optional[ClipboardItem]:
        """Get current clipboard content as ClipboardItem"""
        try:
            clipboard = QApplication.clipboard()
            if not clipboard:
                return None
            
            # Check text first
            text_content = clipboard.text()
            if text_content:
                is_rich_text = '<' in text_content and '>' in text_content
                content_type = ContentType.RICH_TEXT if is_rich_text else ContentType.TEXT
                preview = self._create_text_preview(text_content)
                
                from datetime import datetime
                return ClipboardItem(
                    id=None,
                    content=text_content,
                    content_type=content_type,
                    preview=preview,
                    timestamp=datetime.now(),
                    metadata={'length': len(text_content)}
                )
            
            # Check image
            image = clipboard.image()
            if not image.isNull():
                image_data = self._image_to_bytes(image)
                image_obj = Image.open(io.BytesIO(image_data))
                preview = f"Image ({image_obj.size[0]}x{image_obj.size[1]}, {image_obj.mode})"
                
                import base64
                content = base64.b64encode(image_data).decode('utf-8')
                
                from datetime import datetime
                return ClipboardItem(
                    id=None,
                    content=content,
                    content_type=ContentType.IMAGE,
                    preview=preview,
                    timestamp=datetime.now(),
                    metadata={
                        'width': image_obj.size[0],
                        'height': image_obj.size[1],
                        'mode': image_obj.mode,
                        'format': image_obj.format
                    }
                )
            
            # Check files
            file_paths = self._get_file_paths()
            if file_paths:
                path = file_paths[0]  # Take first file
                if os.path.isfile(path):
                    content_type = ContentType.FILE
                    preview = f"File: {os.path.basename(path)}"
                elif os.path.isdir(path):
                    content_type = ContentType.FOLDER
                    preview = f"Folder: {os.path.basename(path)}"
                else:
                    return None
                
                from datetime import datetime
                return ClipboardItem(
                    id=None,
                    content=path,
                    content_type=content_type,
                    preview=preview,
                    timestamp=datetime.now(),
                    metadata={'path': path, 'exists': os.path.exists(path)}
                )
            
            return None
            
        except Exception as e:
            print(f"Error getting clipboard content: {e}")
            return None
