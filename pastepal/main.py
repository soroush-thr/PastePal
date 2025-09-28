"""
Main application entry point for PastePal
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QIcon

from .database import DatabaseManager
from .clipboard_monitor import ClipboardMonitor
from .hotkeys import HotkeyManager
from .ui.main_window import MainWindow
from .ui.system_tray import SystemTrayManager
from .ui.themes import ThemeManager
from .ui.settings_dialog import SettingsDialog


class PastePalApp(QObject):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.theme_manager = ThemeManager()
        self.hotkey_manager = HotkeyManager()
        self.clipboard_monitor = ClipboardMonitor(self.db_manager)
        self.main_window = None
        self.system_tray = None
        self.settings_dialog = None
        
        # Application state
        self.is_running = False
        self.start_minimized = True
        
        # Setup application
        self.setup_application()
        self.setup_connections()
        self.load_settings()
        self.setup_hotkeys()
        self.setup_system_tray()
        
        # Start monitoring
        self.start_services()
    
    def setup_application(self):
        """Setup the Qt application"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.app.setApplicationName("PastePal")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("PastePal Team")
        
        # Set application icon
        self.set_application_icon()
    
    def set_application_icon(self):
        """Set the application icon"""
        # Create a simple icon
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
        from PyQt6.QtCore import QSize
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background circle
        painter.setBrush(QColor(0, 120, 212))  # Blue background
        painter.setPen(QColor(255, 255, 255))  # White border
        painter.drawEllipse(4, 4, 56, 56)
        
        # Draw "P" letter
        painter.setPen(QColor(255, 255, 255))  # White text
        painter.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        painter.drawText(16, 44, "P")
        
        painter.end()
        
        icon = QIcon(pixmap)
        self.app.setWindowIcon(icon)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Clipboard monitor signals
        self.clipboard_monitor.clipboard_changed.connect(self.on_clipboard_changed)
        
        # Hotkey signals
        self.hotkey_manager.hotkey_triggered.connect(self.on_hotkey_triggered)
    
    def load_settings(self):
        """Load settings from database"""
        # Load theme
        theme_name = self.db_manager.get_setting('theme', 'light')
        self.theme_manager.set_theme(theme_name)
        
        # Load startup settings
        self.start_minimized = self.db_manager.get_setting('start_minimized', 'true') == 'true'
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        # Get hotkey settings
        show_hotkey = self.db_manager.get_setting('hotkey', 'alt+v')
        paste_hotkey = self.db_manager.get_setting('paste_hotkey', 'ctrl+shift+enter')
        quick_paste_hotkey = self.db_manager.get_setting('quick_paste_hotkey', 'ctrl+alt+v')
        
        # Register hotkeys
        self.hotkey_manager.register_hotkey('show_window', show_hotkey)
        self.hotkey_manager.register_hotkey('paste_plain', paste_hotkey)
        self.hotkey_manager.register_hotkey('quick_paste', quick_paste_hotkey)
        
        # Start monitoring
        self.hotkey_manager.start_monitoring()
    
    def setup_system_tray(self):
        """Setup system tray"""
        self.system_tray = SystemTrayManager()
        self.system_tray.show_window_requested.connect(self.show_main_window)
        self.system_tray.settings_requested.connect(self.show_settings)
        self.system_tray.quit_requested.connect(self.quit_application)
    
    def start_services(self):
        """Start background services"""
        # Start clipboard monitoring
        monitor_enabled = self.db_manager.get_setting('monitor_enabled', 'true') == 'true'
        if monitor_enabled:
            self.clipboard_monitor.start_monitoring()
            self.system_tray.update_status('active')
        else:
            self.system_tray.update_status('paused')
        
        self.is_running = True
    
    def stop_services(self):
        """Stop background services"""
        self.is_running = False
        
        # Stop clipboard monitoring
        self.clipboard_monitor.stop_monitoring()
        
        # Stop hotkey monitoring
        self.hotkey_manager.stop_monitoring()
        
        # Clear clipboard history on exit if setting is enabled
        clear_on_exit = self.db_manager.get_setting('clear_on_exit', 'false') == 'true'
        if clear_on_exit:
            self.db_manager.clear_history(keep_pinned=True)
    
    def show_main_window(self):
        """Show the main window"""
        if self.main_window is None:
            self.main_window = MainWindow(self.db_manager, self.theme_manager)
            self.main_window.hideEvent = self.on_main_window_hide
        
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
    
    def hide_main_window(self):
        """Hide the main window"""
        if self.main_window and self.main_window.isVisible():
            self.main_window.hide()
    
    def on_main_window_hide(self, event):
        """Handle main window hide event"""
        # Keep the window hidden but don't quit the application
        event.accept()
    
    def show_settings(self):
        """Show settings dialog"""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.db_manager, self.theme_manager)
            self.settings_dialog.settings_changed.connect(self.on_settings_changed)
        
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def on_settings_changed(self):
        """Handle settings changes"""
        # Reload settings
        self.load_settings()
        
        # Update hotkeys
        self.hotkey_manager.unregister_all_hotkeys()
        self.setup_hotkeys()
        
        # Update clipboard monitoring
        monitor_enabled = self.db_manager.get_setting('monitor_enabled', 'true') == 'true'
        if monitor_enabled:
            if not self.clipboard_monitor.monitoring:
                self.clipboard_monitor.start_monitoring()
            self.system_tray.update_status('active')
        else:
            if self.clipboard_monitor.monitoring:
                self.clipboard_monitor.stop_monitoring()
            self.system_tray.update_status('paused')
        
        # Update main window if it exists
        if self.main_window:
            self.main_window.load_clipboard_history()
    
    def on_clipboard_changed(self, item):
        """Handle clipboard content change"""
        # Update status in system tray
        self.system_tray.set_tooltip(f"PastePal - {item.content_type.value.title()}: {item.preview[:50]}...")
        
        # Show notification if enabled
        show_notifications = self.db_manager.get_setting('show_notifications', 'true') == 'true'
        if show_notifications and self.system_tray.tray_icon:
            from PyQt6.QtWidgets import QSystemTrayIcon
            self.system_tray.show_message(
                "Clipboard Updated",
                f"New {item.content_type.value} content captured",
                QSystemTrayIcon.MessageIcon.Information
            )
    
    def on_hotkey_triggered(self, hotkey_name):
        """Handle hotkey trigger"""
        if hotkey_name == 'show_window':
            self.show_main_window()
        elif hotkey_name == 'paste_plain':
            self.paste_as_plain_text()
        elif hotkey_name == 'quick_paste':
            self.quick_paste()
    
    def paste_as_plain_text(self):
        """Paste current clipboard content as plain text"""
        if self.main_window and self.main_window.isVisible():
            self.main_window.paste_selected_item_plain()
        else:
            # Get current clipboard content and paste as plain text
            current_item = self.clipboard_monitor.get_clipboard_content()
            if current_item and current_item.content_type in ['text', 'rich_text']:
                import re
                plain_text = re.sub(r'<[^>]+>', '', current_item.content)
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(plain_text)
                self.simulate_paste()
    
    def quick_paste(self):
        """Quick paste the most recent item"""
        if self.main_window and self.main_window.isVisible():
            self.main_window.paste_selected_item()
        else:
            # Get most recent item and paste it
            items = self.db_manager.get_items(limit=1)
            if items:
                self.main_window = MainWindow(self.db_manager, self.theme_manager)
                self.main_window.current_selected_item = items[0]
                self.main_window.paste_selected_item()
    
    def simulate_paste(self):
        """Simulate Ctrl+V keypress"""
        import keyboard
        keyboard.send('ctrl+v')
    
    def quit_application(self):
        """Quit the application"""
        self.stop_services()
        
        # Close all windows
        if self.main_window:
            self.main_window.close()
        if self.settings_dialog:
            self.settings_dialog.close()
        
        # Quit application
        self.app.quit()
    
    def run(self):
        """Run the application"""
        try:
            # Show main window if not starting minimized
            if not self.start_minimized:
                self.show_main_window()
            
            # Run the application
            return self.app.exec()
            
        except Exception as e:
            print(f"Error running application: {e}")
            return 1
        finally:
            self.stop_services()


def main():
    """Main entry point"""
    try:
        # Create and run the application
        app = PastePalApp()
        return app.run()
    except Exception as e:
        print(f"Failed to start PastePal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
