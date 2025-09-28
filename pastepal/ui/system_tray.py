"""
System tray functionality for PastePal
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from typing import Optional


class SystemTrayManager(QObject):
    """Manages system tray icon and menu"""
    
    show_window_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self.tray_menu = None
        self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Setup the system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_tray_icon())
        self.tray_icon.setToolTip("PastePal - Clipboard Manager")
        
        # Create context menu
        self.tray_menu = QMenu()
        
        # Show Clipboard action
        show_action = self.tray_menu.addAction("Show Clipboard")
        show_action.triggered.connect(self.show_window_requested.emit)
        
        # Separator
        self.tray_menu.addSeparator()
        
        # Settings action
        settings_action = self.tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_requested.emit)
        
        # Separator
        self.tray_menu.addSeparator()
        
        # Quit action
        quit_action = self.tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_requested.emit)
        
        # Set context menu
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Connect double-click to show window
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.tray_icon.show()
    
    def create_tray_icon(self) -> QIcon:
        """Create the system tray icon"""
        # Create a simple icon with "P" for PastePal
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background circle
        painter.setBrush(QColor(0, 120, 212))  # Blue background
        painter.setPen(QColor(255, 255, 255))  # White border
        painter.drawEllipse(2, 2, 28, 28)
        
        # Draw "P" letter
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(8, 22, "P")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()
    
    def show_message(self, title: str, message: str, icon_type: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information):
        """Show a system tray message"""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon_type, 3000)
    
    def set_tooltip(self, tooltip: str):
        """Set the tray icon tooltip"""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)
    
    def is_visible(self) -> bool:
        """Check if tray icon is visible"""
        return self.tray_icon and self.tray_icon.isVisible()
    
    def hide(self):
        """Hide the tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def show(self):
        """Show the tray icon"""
        if self.tray_icon:
            self.tray_icon.show()
    
    def update_menu(self, additional_actions: list = None):
        """Update the tray menu with additional actions"""
        if not self.tray_menu:
            return
        
        # Clear existing menu
        self.tray_menu.clear()
        
        # Add standard actions
        show_action = self.tray_menu.addAction("Show Clipboard")
        show_action.triggered.connect(self.show_window_requested.emit)
        
        self.tray_menu.addSeparator()
        
        settings_action = self.tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_requested.emit)
        
        # Add additional actions if provided
        if additional_actions:
            self.tray_menu.addSeparator()
            for action in additional_actions:
                self.tray_menu.addAction(action)
        
        self.tray_menu.addSeparator()
        
        quit_action = self.tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_requested.emit)
    
    def set_icon(self, icon: QIcon):
        """Set a custom icon for the tray"""
        if self.tray_icon:
            self.tray_icon.setIcon(icon)
    
    def create_status_icon(self, status: str) -> QIcon:
        """Create an icon with status indicator"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Choose color based on status
        if status == "active":
            bg_color = QColor(0, 120, 212)  # Blue
        elif status == "paused":
            bg_color = QColor(255, 140, 0)  # Orange
        elif status == "error":
            bg_color = QColor(232, 17, 35)  # Red
        else:
            bg_color = QColor(100, 100, 100)  # Gray
        
        # Draw background circle
        painter.setBrush(bg_color)
        painter.setPen(QColor(255, 255, 255))  # White border
        painter.drawEllipse(2, 2, 28, 28)
        
        # Draw "P" letter
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(8, 22, "P")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def update_status(self, status: str):
        """Update the tray icon status"""
        icon = self.create_status_icon(status)
        self.set_icon(icon)
