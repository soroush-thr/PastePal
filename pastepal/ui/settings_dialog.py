"""
Settings dialog for PastePal
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QCheckBox, QSpinBox, QLineEdit, QGroupBox,
    QFormLayout, QDialogButtonBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .themes import ThemeManager
from ..database import DatabaseManager


class SettingsDialog(QDialog):
    """Settings dialog window"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, db_manager: DatabaseManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.theme_manager = theme_manager
        self.setup_ui()
        self.load_settings()
        self.apply_theme()
        
        # Connect theme changes
        self.theme_manager.theme_changed.connect(self.apply_theme)
    
    def setup_ui(self):
        """Setup the settings UI"""
        self.setWindowTitle("PastePal Settings")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Appearance tab
        appearance_tab = self.create_appearance_tab()
        tab_widget.addTab(appearance_tab, "Appearance")
        
        # Hotkeys tab
        hotkeys_tab = self.create_hotkeys_tab()
        tab_widget.addTab(hotkeys_tab, "Hotkeys")
        
        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Advanced")
        
        main_layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)
    
    def create_general_tab(self) -> QWidget:
        """Create the general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout()
        
        self.start_minimized_cb = QCheckBox("Start minimized to system tray")
        startup_layout.addRow(self.start_minimized_cb)
        
        self.start_with_windows_cb = QCheckBox("Start with Windows")
        startup_layout.addRow(self.start_with_windows_cb)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # History settings
        history_group = QGroupBox("History")
        history_layout = QFormLayout()
        
        self.max_history_spin = QSpinBox()
        self.max_history_spin.setRange(10, 10000)
        self.max_history_spin.setSuffix(" items")
        history_layout.addRow("Maximum history items:", self.max_history_spin)
        
        self.auto_clear_cb = QCheckBox("Auto-clear old items")
        history_layout.addRow(self.auto_clear_cb)
        
        self.clear_on_exit_cb = QCheckBox("Clear history on exit")
        history_layout.addRow(self.clear_on_exit_cb)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Monitoring settings
        monitor_group = QGroupBox("Clipboard Monitoring")
        monitor_layout = QFormLayout()
        
        self.monitor_enabled_cb = QCheckBox("Enable clipboard monitoring")
        monitor_layout.addRow(self.monitor_enabled_cb)
        
        self.monitor_interval_spin = QSpinBox()
        self.monitor_interval_spin.setRange(100, 5000)
        self.monitor_interval_spin.setSuffix(" ms")
        monitor_layout.addRow("Check interval:", self.monitor_interval_spin)
        
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_appearance_tab(self) -> QWidget:
        """Create the appearance settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        theme_names = self.theme_manager.get_theme_names()
        for key, name in theme_names.items():
            self.theme_combo.addItem(name, key)
        theme_layout.addRow("Theme:", self.theme_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(400, 1200)
        self.window_width_spin.setSuffix(" px")
        window_layout.addRow("Window width:", self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(300, 800)
        self.window_height_spin.setSuffix(" px")
        window_layout.addRow("Window height:", self.window_height_spin)
        
        self.always_on_top_cb = QCheckBox("Always on top")
        window_layout.addRow(self.always_on_top_cb)
        
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        # Display settings
        display_group = QGroupBox("Display")
        display_layout = QFormLayout()
        
        self.show_preview_cb = QCheckBox("Show content preview")
        display_layout.addRow(self.show_preview_cb)
        
        self.preview_length_spin = QSpinBox()
        self.preview_length_spin.setRange(20, 200)
        self.preview_length_spin.setSuffix(" characters")
        display_layout.addRow("Preview length:", self.preview_length_spin)
        
        self.show_timestamps_cb = QCheckBox("Show timestamps")
        display_layout.addRow(self.show_timestamps_cb)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_hotkeys_tab(self) -> QWidget:
        """Create the hotkeys settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Global hotkeys
        hotkeys_group = QGroupBox("Global Hotkeys")
        hotkeys_layout = QFormLayout()
        
        self.show_hotkey_edit = QLineEdit()
        self.show_hotkey_edit.setPlaceholderText("e.g., Alt+V")
        hotkeys_layout.addRow("Show window:", self.show_hotkey_edit)
        
        self.paste_hotkey_edit = QLineEdit()
        self.paste_hotkey_edit.setPlaceholderText("e.g., Ctrl+Shift+Enter")
        hotkeys_layout.addRow("Paste as plain text:", self.paste_hotkey_edit)
        
        self.quick_paste_hotkey_edit = QLineEdit()
        self.quick_paste_hotkey_edit.setPlaceholderText("e.g., Ctrl+Alt+V")
        hotkeys_layout.addRow("Quick paste:", self.quick_paste_hotkey_edit)
        
        hotkeys_group.setLayout(hotkeys_layout)
        layout.addWidget(hotkeys_group)
        
        # Hotkey help
        help_group = QGroupBox("Available Keys")
        help_layout = QVBoxLayout()
        
        help_text = QLabel("""
        <b>Modifier keys:</b> Ctrl, Alt, Shift, Win<br>
        <b>Special keys:</b> Enter, Space, Tab, Escape, F1-F12<br>
        <b>Arrow keys:</b> Up, Down, Left, Right<br>
        <b>Examples:</b><br>
        • Alt+V (show window)<br>
        • Ctrl+Shift+Enter (paste plain text)<br>
        • Ctrl+Alt+V (quick paste)
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        help_group.setLayout(help_layout)
        layout.addWidget(help_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Create the advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Database settings
        db_group = QGroupBox("Database")
        db_layout = QFormLayout()
        
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        db_layout.addRow("Database path:", self.db_path_edit)
        
        self.clear_db_btn = QPushButton("Clear Database")
        self.clear_db_btn.clicked.connect(self.clear_database)
        db_layout.addRow("", self.clear_db_btn)
        
        db_group.setLayout(db_layout)
        layout.addWidget(db_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout()
        
        self.enable_caching_cb = QCheckBox("Enable content caching")
        perf_layout.addRow(self.enable_caching_cb)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        perf_layout.addRow("Cache size:", self.cache_size_spin)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # Debug settings
        debug_group = QGroupBox("Debug")
        debug_layout = QFormLayout()
        
        self.enable_logging_cb = QCheckBox("Enable debug logging")
        debug_layout.addRow(self.enable_logging_cb)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        debug_layout.addRow("Log level:", self.log_level_combo)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def load_settings(self):
        """Load settings from database"""
        # General settings
        self.start_minimized_cb.setChecked(
            self.db_manager.get_setting('start_minimized', 'true') == 'true'
        )
        self.start_with_windows_cb.setChecked(
            self.db_manager.get_setting('start_with_windows', 'false') == 'true'
        )
        self.max_history_spin.setValue(
            int(self.db_manager.get_setting('max_history', '1000'))
        )
        self.auto_clear_cb.setChecked(
            self.db_manager.get_setting('auto_clear', 'true') == 'true'
        )
        self.clear_on_exit_cb.setChecked(
            self.db_manager.get_setting('clear_on_exit', 'false') == 'true'
        )
        self.monitor_enabled_cb.setChecked(
            self.db_manager.get_setting('monitor_enabled', 'true') == 'true'
        )
        self.monitor_interval_spin.setValue(
            int(self.db_manager.get_setting('monitor_interval', '500'))
        )
        
        # Appearance settings
        current_theme = self.db_manager.get_setting('theme', 'light')
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        self.window_width_spin.setValue(
            int(self.db_manager.get_setting('window_width', '600'))
        )
        self.window_height_spin.setValue(
            int(self.db_manager.get_setting('window_height', '500'))
        )
        self.always_on_top_cb.setChecked(
            self.db_manager.get_setting('always_on_top', 'true') == 'true'
        )
        self.show_preview_cb.setChecked(
            self.db_manager.get_setting('show_preview', 'true') == 'true'
        )
        self.preview_length_spin.setValue(
            int(self.db_manager.get_setting('preview_length', '100'))
        )
        self.show_timestamps_cb.setChecked(
            self.db_manager.get_setting('show_timestamps', 'true') == 'true'
        )
        
        # Hotkey settings
        self.show_hotkey_edit.setText(
            self.db_manager.get_setting('hotkey', 'alt+v')
        )
        self.paste_hotkey_edit.setText(
            self.db_manager.get_setting('paste_hotkey', 'ctrl+shift+enter')
        )
        self.quick_paste_hotkey_edit.setText(
            self.db_manager.get_setting('quick_paste_hotkey', 'ctrl+alt+v')
        )
        
        # Advanced settings
        self.db_path_edit.setText(self.db_manager.db_path)
        self.enable_caching_cb.setChecked(
            self.db_manager.get_setting('enable_caching', 'true') == 'true'
        )
        self.cache_size_spin.setValue(
            int(self.db_manager.get_setting('cache_size', '100'))
        )
        self.enable_logging_cb.setChecked(
            self.db_manager.get_setting('enable_logging', 'false') == 'true'
        )
        
        log_level = self.db_manager.get_setting('log_level', 'INFO')
        log_index = self.log_level_combo.findText(log_level)
        if log_index >= 0:
            self.log_level_combo.setCurrentIndex(log_index)
    
    def apply_settings(self):
        """Apply current settings to database"""
        # General settings
        self.db_manager.set_setting('start_minimized', str(self.start_minimized_cb.isChecked()).lower())
        self.db_manager.set_setting('start_with_windows', str(self.start_with_windows_cb.isChecked()).lower())
        self.db_manager.set_setting('max_history', str(self.max_history_spin.value()))
        self.db_manager.set_setting('auto_clear', str(self.auto_clear_cb.isChecked()).lower())
        self.db_manager.set_setting('clear_on_exit', str(self.clear_on_exit_cb.isChecked()).lower())
        self.db_manager.set_setting('monitor_enabled', str(self.monitor_enabled_cb.isChecked()).lower())
        self.db_manager.set_setting('monitor_interval', str(self.monitor_interval_spin.value()))
        
        # Appearance settings
        current_theme = self.theme_combo.currentData()
        self.db_manager.set_setting('theme', current_theme)
        self.theme_manager.set_theme(current_theme)
        
        self.db_manager.set_setting('window_width', str(self.window_width_spin.value()))
        self.db_manager.set_setting('window_height', str(self.window_height_spin.value()))
        self.db_manager.set_setting('always_on_top', str(self.always_on_top_cb.isChecked()).lower())
        self.db_manager.set_setting('show_preview', str(self.show_preview_cb.isChecked()).lower())
        self.db_manager.set_setting('preview_length', str(self.preview_length_spin.value()))
        self.db_manager.set_setting('show_timestamps', str(self.show_timestamps_cb.isChecked()).lower())
        
        # Hotkey settings
        self.db_manager.set_setting('hotkey', self.show_hotkey_edit.text().lower())
        self.db_manager.set_setting('paste_hotkey', self.paste_hotkey_edit.text().lower())
        self.db_manager.set_setting('quick_paste_hotkey', self.quick_paste_hotkey_edit.text().lower())
        
        # Advanced settings
        self.db_manager.set_setting('enable_caching', str(self.enable_caching_cb.isChecked()).lower())
        self.db_manager.set_setting('cache_size', str(self.cache_size_spin.value()))
        self.db_manager.set_setting('enable_logging', str(self.enable_logging_cb.isChecked()).lower())
        self.db_manager.set_setting('log_level', self.log_level_combo.currentText())
        
        self.settings_changed.emit()
    
    def clear_database(self):
        """Clear the database"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            "Clear Database", 
            "Are you sure you want to clear all clipboard history? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.clear_history(keep_pinned=False)
            QMessageBox.information(self, "Database Cleared", "All clipboard history has been cleared.")
    
    def apply_theme(self):
        """Apply current theme to the dialog"""
        theme = self.theme_manager.current_theme
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.get('window_bg', '#ffffff')};
                color: {theme.get('window_text', '#000000')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme.get('border', '#e0e0e0')};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {theme.get('input_bg', '#ffffff')};
                color: {theme.get('input_text', '#000000')};
                border: 1px solid {theme.get('input_border', '#e0e0e0')};
                border-radius: 3px;
                padding: 4px;
            }}
            QPushButton {{
                background-color: {theme.get('button_bg', '#f0f0f0')};
                color: {theme.get('button_text', '#000000')};
                border: 1px solid {theme.get('button_border', '#d0d0d0')};
                border-radius: 3px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {theme.get('button_hover', '#e0e0e0')};
            }}
            QCheckBox {{
                color: {theme.get('item_text', '#000000')};
            }}
        """)
    
    def accept(self):
        """Handle OK button click"""
        self.apply_settings()
        super().accept()
