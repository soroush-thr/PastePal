"""
Theme management for PastePal
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any


class ThemeManager(QObject):
    """Manages application themes"""
    
    theme_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.themes = {
            'light': {
                'name': 'Light Mode',
                'window_bg': '#ffffff',
                'window_text': '#000000',
                'item_bg': '#ffffff',
                'item_text': '#000000',
                'selection_bg': '#0078d4',
                'selection_text': '#ffffff',
                'hover_bg': '#f5f5f5',
                'input_bg': '#ffffff',
                'input_text': '#000000',
                'input_border': '#d0d0d0',
                'button_bg': '#f8f8f8',
                'button_text': '#000000',
                'button_border': '#c0c0c0',
                'button_hover': '#e8e8e8',
                'border': '#d0d0d0',
                'scroll_bg': '#ffffff',
                'accent': '#0078d4'
            },
            'dark': {
                'name': 'Dark Mode',
                'window_bg': '#2d2d30',
                'window_text': '#ffffff',
                'item_bg': '#3c3c3c',
                'item_text': '#ffffff',
                'selection_bg': '#0078d4',
                'selection_text': '#ffffff',
                'hover_bg': '#4a4a4a',
                'input_bg': '#3c3c3c',
                'input_text': '#ffffff',
                'input_border': '#555555',
                'button_bg': '#4a4a4a',
                'button_text': '#ffffff',
                'button_border': '#666666',
                'button_hover': '#5a5a5a',
                'border': '#555555',
                'scroll_bg': '#2d2d30',
                'accent': '#0078d4'
            }
        }
        self.current_theme_name = 'light'
        self.current_theme = self.themes[self.current_theme_name]
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def get_theme_names(self) -> Dict[str, str]:
        """Get theme names mapping"""
        return {key: theme['name'] for key, theme in self.themes.items()}
    
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.current_theme = self.themes[theme_name]
            self.theme_changed.emit()
    
    def get_current_theme_name(self) -> str:
        """Get current theme name"""
        return self.current_theme_name
    
    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """Get theme data"""
        if theme_name is None:
            return self.current_theme
        return self.themes.get(theme_name, self.current_theme)
    
    def add_custom_theme(self, name: str, theme_data: Dict[str, Any]):
        """Add a custom theme"""
        self.themes[name] = theme_data
    
    def export_theme(self, theme_name: str) -> Dict[str, Any]:
        """Export theme data"""
        return self.themes.get(theme_name, {}).copy()
    
    def import_theme(self, name: str, theme_data: Dict[str, Any]):
        """Import theme data"""
        self.themes[name] = theme_data
