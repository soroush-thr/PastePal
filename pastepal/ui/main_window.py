"""
Main window UI for PastePal
"""

import os
import base64
import io
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QListWidget, QListWidgetItem, QLabel, QPushButton, QMenu,
    QApplication, QFrame, QSplitter, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import (
    QIcon, QPixmap, QFont, QPalette, QColor, QAction, 
    QKeySequence, QClipboard, QPainter, QPen
)
from PIL import Image
from .themes import ThemeManager
from ..database import ClipboardItem, ContentType, DatabaseManager
from ..clipboard_monitor import ClipboardMonitor


class ClipboardItemWidget(QWidget):
    """Custom widget for displaying clipboard items"""
    
    item_selected = pyqtSignal(ClipboardItem)
    item_double_clicked = pyqtSignal(ClipboardItem)
    item_right_clicked = pyqtSignal(ClipboardItem, QPoint)
    
    def __init__(self, item: ClipboardItem, theme_manager: ThemeManager):
        super().__init__()
        self.item = item
        self.theme_manager = theme_manager
        self.is_selected = False
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the UI for this item"""
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(3)
        
        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(6)
        
        # Icon based on content type
        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.item.content_type == ContentType.TEXT or self.item.content_type == ContentType.RICH_TEXT:
            icon_label.setText("📝")
        elif self.item.content_type == ContentType.IMAGE:
            icon_label.setText("🖼️")
        elif self.item.content_type == ContentType.FILE:
            icon_label.setText("📄")
        elif self.item.content_type == ContentType.FOLDER:
            icon_label.setText("📁")
        
        content_layout.addWidget(icon_label)
        
        # Content preview
        preview_label = QLabel(self.item.preview)
        preview_label.setWordWrap(True)
        preview_label.setMaximumHeight(32)
        preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Style the preview based on content type
        if self.item.content_type == ContentType.TEXT:
            preview_label.setFont(QFont("Consolas", 9))
        elif self.item.content_type == ContentType.RICH_TEXT:
            preview_label.setFont(QFont("Arial", 9))
            preview_label.setStyleSheet("color: #0066cc;")
        
        content_layout.addWidget(preview_label)
        
        # Pin indicator
        if self.item.is_pinned:
            pin_label = QLabel("📌")
            pin_label.setFixedSize(16, 16)
            pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(pin_label)
        
        layout.addLayout(content_layout)
        
        # Timestamp
        timestamp_label = QLabel(self.item.timestamp.strftime("%H:%M:%S"))
        timestamp_label.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(timestamp_label)
        
        self.setLayout(layout)
        self.setFixedHeight(60)  # More compact height
        self.setMouseTracking(True)
    
    def apply_theme(self):
        """Apply current theme to this widget"""
        theme = self.theme_manager.current_theme
        
        if self.is_selected:
            bg_color = theme.get('selection_bg', '#0078d4')
            text_color = theme.get('selection_text', '#ffffff')
        else:
            bg_color = theme.get('item_bg', '#ffffff')
            text_color = theme.get('item_text', '#000000')
        
        self.setStyleSheet(f"""
            ClipboardItemWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {theme.get('border', '#e0e0e0')};
                border-radius: 6px;
                margin: 3px 2px;
            }}
            ClipboardItemWidget:hover {{
                background-color: {theme.get('hover_bg', '#f0f0f0')};
                border-color: {theme.get('accent', '#0078d4')};
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Immediate visual feedback
            self.set_selected(True)
            # Add a brief visual flash for click feedback
            self.flash_click_feedback()
            # Emit signal
            self.item_selected.emit(self.item)
        elif event.button() == Qt.MouseButton.RightButton:
            self.item_right_clicked.emit(self.item, event.globalPosition().toPoint())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.item_double_clicked.emit(self.item)
        super().mouseDoubleClickEvent(event)
    
    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self.apply_theme()
    
    def flash_click_feedback(self):
        """Provide visual feedback for click"""
        # Store original style
        original_style = self.styleSheet()
        
        # Create flash effect
        theme = self.theme_manager.current_theme
        flash_style = f"""
            ClipboardItemWidget {{
                background-color: {theme.get('accent', '#0078d4')};
                color: {theme.get('selection_text', '#ffffff')};
                border: 2px solid {theme.get('accent', '#0078d4')};
                border-radius: 6px;
                margin: 3px 2px;
            }}
        """
        
        # Apply flash style
        self.setStyleSheet(flash_style)
        
        # Reset after brief delay
        QTimer.singleShot(150, lambda: self.apply_theme())
    
    def enterEvent(self, event):
        """Handle mouse enter events"""
        if not self.is_selected:
            self.apply_theme()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        if not self.is_selected:
            self.apply_theme()
        super().leaveEvent(event)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, db_manager: DatabaseManager, theme_manager: ThemeManager):
        super().__init__()
        self.db_manager = db_manager
        self.theme_manager = theme_manager
        self.current_selected_item = None
        self.item_widgets = []
        
        self.setup_ui()
        self.setup_shortcuts()
        self.apply_theme()
        self.load_clipboard_history()
        
        # Connect theme changes
        self.theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("PastePal - Clipboard Manager")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(450, 350)  # More compact size
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clipboard history...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        # Search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.filter_history)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(28, 28)
        settings_btn.clicked.connect(self.show_settings)
        search_layout.addWidget(settings_btn)
        
        main_layout.addLayout(search_layout)
        
        # History list
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.setContentsMargins(2, 2, 2, 2)
        self.history_layout.setSpacing(4)  # Better spacing between items
        self.history_widget.setLayout(self.history_layout)
        
        self.history_scroll.setWidget(self.history_widget)
        main_layout.addWidget(self.history_scroll)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        
        # Set focus to search input
        self.search_input.setFocus()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Enter to paste
        paste_action = QAction(self)
        paste_action.setShortcut(QKeySequence(Qt.Key.Key_Return))
        paste_action.triggered.connect(self.paste_selected_item)
        self.addAction(paste_action)
        
        # Ctrl+Shift+Enter to paste as plain text
        paste_plain_action = QAction(self)
        paste_plain_action.setShortcut(QKeySequence("Ctrl+Shift+Return"))
        paste_plain_action.triggered.connect(self.paste_selected_item_plain)
        self.addAction(paste_plain_action)
        
        # Escape to hide
        hide_action = QAction(self)
        hide_action.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        hide_action.triggered.connect(self.hide)
        self.addAction(hide_action)
        
        # Ctrl+A to select all
        select_all_action = QAction(self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(self.select_all_items)
        self.addAction(select_all_action)
    
    def apply_theme(self):
        """Apply current theme to the window"""
        theme = self.theme_manager.current_theme
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme.get('window_bg', '#ffffff')};
                color: {theme.get('window_text', '#000000')};
            }}
            QLineEdit {{
                background-color: {theme.get('input_bg', '#ffffff')};
                color: {theme.get('input_text', '#000000')};
                border: 2px solid {theme.get('input_border', '#e0e0e0')};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {theme.get('accent', '#0078d4')};
            }}
            QPushButton {{
                background-color: {theme.get('button_bg', '#f0f0f0')};
                color: {theme.get('button_text', '#000000')};
                border: 1px solid {theme.get('button_border', '#d0d0d0')};
                border-radius: 4px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme.get('button_hover', '#e0e0e0')};
            }}
            QScrollArea {{
                border: 1px solid {theme.get('border', '#e0e0e0')};
                border-radius: 4px;
                background-color: {theme.get('scroll_bg', '#ffffff')};
            }}
        """)
    
    def load_clipboard_history(self, search_query: str = None):
        """Load clipboard history from database"""
        # Clear existing widgets more efficiently
        for widget in self.item_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.item_widgets.clear()
        
        # Get items from database (reduced limit for better performance)
        items = self.db_manager.get_items(limit=50, search_query=search_query)
        
        # Create widgets for each item
        for item in items:
            widget = ClipboardItemWidget(item, self.theme_manager)
            widget.item_selected.connect(self.on_item_selected)
            widget.item_double_clicked.connect(self.paste_selected_item)
            widget.item_right_clicked.connect(self.show_item_context_menu)
            
            self.history_layout.addWidget(widget)
            self.item_widgets.append(widget)
        
        # Update status
        self.status_label.setText(f"Loaded {len(items)} items")
    
    def on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing"""
        # Stop previous timer
        self.search_timer.stop()
        # Start new timer (300ms delay)
        self.search_timer.start(300)
    
    def filter_history(self):
        """Filter history based on current search query"""
        query = self.search_input.text().strip() if self.search_input.text() else None
        self.load_clipboard_history(query)
    
    def on_item_selected(self, item: ClipboardItem):
        """Handle item selection"""
        # Deselect previous item
        if self.current_selected_item:
            for widget in self.item_widgets:
                if widget.item.id == self.current_selected_item.id:
                    widget.set_selected(False)
                    break
        
        # Select new item
        self.current_selected_item = item
        for widget in self.item_widgets:
            if widget.item.id == item.id:
                widget.set_selected(True)
                break
    
    def paste_selected_item(self):
        """Paste the selected item"""
        if not self.current_selected_item:
            return
        
        try:
            self.copy_item_to_clipboard(self.current_selected_item)
            self.hide()
            self.simulate_paste()
            self.status_label.setText("Item pasted successfully")
        except Exception as e:
            self.status_label.setText(f"Error pasting item: {str(e)}")
    
    def paste_selected_item_plain(self):
        """Paste the selected item as plain text"""
        if not self.current_selected_item:
            return
        
        try:
            # Convert to plain text if it's rich text
            if self.current_selected_item.content_type == ContentType.RICH_TEXT:
                import re
                plain_text = re.sub(r'<[^>]+>', '', self.current_selected_item.content)
                clipboard = QApplication.clipboard()
                clipboard.setText(plain_text)
            else:
                self.copy_item_to_clipboard(self.current_selected_item)
            
            self.hide()
            self.simulate_paste()
            self.status_label.setText("Item pasted as plain text")
        except Exception as e:
            self.status_label.setText(f"Error pasting item: {str(e)}")
    
    def copy_item_to_clipboard(self, item: ClipboardItem):
        """Copy item content to system clipboard"""
        clipboard = QApplication.clipboard()
        
        if item.content_type == ContentType.TEXT or item.content_type == ContentType.RICH_TEXT:
            clipboard.setText(item.content)
        elif item.content_type == ContentType.IMAGE:
            # Convert base64 back to image
            image_data = base64.b64decode(item.content)
            image = Image.open(io.BytesIO(image_data))
            # Convert PIL image to QPixmap
            from PyQt6.QtGui import QImage
            # Convert PIL image to RGBA if needed
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            qimage = QImage(image.tobytes(), image.size[0], image.size[1], QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            clipboard.setPixmap(pixmap)
        elif item.content_type in [ContentType.FILE, ContentType.FOLDER]:
            # For files, we can't directly set file paths to clipboard
            # Instead, copy the path as text
            clipboard.setText(item.content)
    
    def simulate_paste(self):
        """Simulate Ctrl+V keypress to paste"""
        import keyboard
        keyboard.send('ctrl+v')
    
    def select_all_items(self):
        """Select all visible items"""
        if self.item_widgets:
            self.on_item_selected(self.item_widgets[0].item)
    
    def show_item_context_menu(self, item: ClipboardItem, position: QPoint):
        """Show context menu for an item"""
        menu = QMenu(self)
        
        # Pin/Unpin action
        if item.is_pinned:
            pin_action = QAction("Unpin Item", self)
            pin_action.triggered.connect(lambda: self.toggle_pin_item(item))
        else:
            pin_action = QAction("Pin Item", self)
            pin_action.triggered.connect(lambda: self.toggle_pin_item(item))
        menu.addAction(pin_action)
        
        # Copy action
        copy_action = QAction("Copy to Clipboard", self)
        copy_action.triggered.connect(lambda: self.copy_item_to_clipboard(item))
        menu.addAction(copy_action)
        
        # Text transformation actions
        if item.content_type in [ContentType.TEXT, ContentType.RICH_TEXT]:
            menu.addSeparator()
            
            transform_menu = QMenu("Transform Text", self)
            
            uppercase_action = QAction("UPPERCASE", self)
            uppercase_action.triggered.connect(lambda: self.transform_text(item, 'uppercase'))
            transform_menu.addAction(uppercase_action)
            
            lowercase_action = QAction("lowercase", self)
            lowercase_action.triggered.connect(lambda: self.transform_text(item, 'lowercase'))
            transform_menu.addAction(lowercase_action)
            
            titlecase_action = QAction("Title Case", self)
            titlecase_action.triggered.connect(lambda: self.transform_text(item, 'titlecase'))
            transform_menu.addAction(titlecase_action)
            
            trim_action = QAction("Trim Whitespace", self)
            trim_action.triggered.connect(lambda: self.transform_text(item, 'trim'))
            transform_menu.addAction(trim_action)
            
            menu.addMenu(transform_menu)
        
        # Delete action
        menu.addSeparator()
        delete_action = QAction("Delete Item", self)
        delete_action.triggered.connect(lambda: self.delete_item(item))
        menu.addAction(delete_action)
        
        menu.exec(position)
    
    def toggle_pin_item(self, item: ClipboardItem):
        """Toggle pin status of an item"""
        new_pinned = not item.is_pinned
        self.db_manager.pin_item(item.id, new_pinned)
        item.is_pinned = new_pinned
        
        # Refresh the display
        self.load_clipboard_history(self.search_input.text())
        self.status_label.setText(f"Item {'pinned' if new_pinned else 'unpinned'}")
    
    def transform_text(self, item: ClipboardItem, transform_type: str):
        """Transform text content"""
        if item.content_type not in [ContentType.TEXT, ContentType.RICH_TEXT]:
            return
        
        original_text = item.content
        transformed_text = original_text
        
        if transform_type == 'uppercase':
            transformed_text = original_text.upper()
        elif transform_type == 'lowercase':
            transformed_text = original_text.lower()
        elif transform_type == 'titlecase':
            transformed_text = original_text.title()
        elif transform_type == 'trim':
            transformed_text = original_text.strip()
        
        if transformed_text != original_text:
            # Update the item in database
            item.content = transformed_text
            item.preview = self._create_text_preview(transformed_text)
            
            # Save to database (we need to add an update method to DatabaseManager)
            # For now, we'll create a new item
            new_item = ClipboardItem(
                id=None,
                content=transformed_text,
                content_type=item.content_type,
                preview=item.preview,
                timestamp=item.timestamp,
                is_pinned=item.is_pinned,
                metadata=item.metadata
            )
            
            self.db_manager.add_item(new_item)
            self.load_clipboard_history(self.search_input.text())
            self.status_label.setText("Text transformed and saved")
    
    def delete_item(self, item: ClipboardItem):
        """Delete an item"""
        self.db_manager.delete_item(item.id)
        self.load_clipboard_history(self.search_input.text())
        self.status_label.setText("Item deleted")
    
    def _create_text_preview(self, text: str, max_length: int = 100) -> str:
        """Create a preview of text content"""
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = clean_text.replace('\n', ' ').replace('\r', ' ')
        
        if len(clean_text) > max_length:
            return clean_text[:max_length] + "..."
        return clean_text
    
    def show_settings(self):
        """Show settings dialog"""
        # This will be implemented in the settings module
        pass
    
    def position_near_middle_right(self):
        """Position the window near the middle-right of the screen"""
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # Position in the middle-right area
        x = screen_geometry.width() - self.width() - 50  # 50px from right edge
        y = screen_geometry.height() // 2 - self.height() // 2  # Middle vertically
        
        self.move(x, y)
    
    def showEvent(self, event):
        """Handle show events"""
        super().showEvent(event)
        self.position_near_middle_right()
        self.search_input.setFocus()
        self.search_input.selectAll()
