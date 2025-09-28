"""
Global hotkey management for PastePal
"""

import threading
import time
from typing import Dict, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal
import keyboard


class HotkeyManager(QObject):
    """Manages global hotkeys for the application"""
    
    hotkey_triggered = pyqtSignal(str)  # Emits the hotkey name when triggered
    
    def __init__(self):
        super().__init__()
        self.hotkeys = {}
        self.hotkey_thread = None
        self.running = False
        self.hotkey_callbacks = {}
        
    def register_hotkey(self, name: str, key_combination: str, callback: Callable = None):
        """Register a global hotkey"""
        try:
            # Convert key combination to keyboard format
            formatted_keys = self._format_key_combination(key_combination)
            
            # Register with keyboard library
            keyboard.add_hotkey(formatted_keys, self._on_hotkey_triggered, args=[name])
            
            self.hotkeys[name] = {
                'combination': key_combination,
                'formatted': formatted_keys,
                'callback': callback
            }
            
            print(f"Registered hotkey: {name} -> {key_combination}")
            return True
            
        except Exception as e:
            print(f"Failed to register hotkey {name}: {e}")
            return False
    
    def unregister_hotkey(self, name: str):
        """Unregister a global hotkey"""
        if name in self.hotkeys:
            try:
                keyboard.remove_hotkey(self.hotkeys[name]['formatted'])
                del self.hotkeys[name]
                print(f"Unregistered hotkey: {name}")
                return True
            except Exception as e:
                print(f"Failed to unregister hotkey {name}: {e}")
                return False
        return False
    
    def unregister_all_hotkeys(self):
        """Unregister all hotkeys"""
        for name in list(self.hotkeys.keys()):
            self.unregister_hotkey(name)
    
    def _format_key_combination(self, combination: str) -> str:
        """Convert key combination string to keyboard library format"""
        # Convert common formats
        combination = combination.lower().strip()
        
        # Replace common modifiers
        combination = combination.replace('ctrl', 'ctrl')
        combination = combination.replace('alt', 'alt')
        combination = combination.replace('shift', 'shift')
        combination = combination.replace('win', 'win')
        
        # Replace common special keys
        combination = combination.replace('enter', 'enter')
        combination = combination.replace('space', 'space')
        combination = combination.replace('tab', 'tab')
        combination = combination.replace('escape', 'esc')
        combination = combination.replace('esc', 'esc')
        
        # Replace function keys
        for i in range(1, 13):
            combination = combination.replace(f'f{i}', f'f{i}')
        
        # Replace arrow keys
        combination = combination.replace('up', 'up')
        combination = combination.replace('down', 'down')
        combination = combination.replace('left', 'left')
        combination = combination.replace('right', 'right')
        
        return combination
    
    def _on_hotkey_triggered(self, name: str):
        """Handle hotkey trigger"""
        print(f"Hotkey triggered: {name}")
        
        # Emit signal
        self.hotkey_triggered.emit(name)
        
        # Call callback if available
        if name in self.hotkeys and self.hotkeys[name]['callback']:
            try:
                self.hotkeys[name]['callback']()
            except Exception as e:
                print(f"Error in hotkey callback for {name}: {e}")
    
    def is_hotkey_registered(self, name: str) -> bool:
        """Check if a hotkey is registered"""
        return name in self.hotkeys
    
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """Get all registered hotkeys"""
        return {name: info['combination'] for name, info in self.hotkeys.items()}
    
    def update_hotkey(self, name: str, new_combination: str, callback: Callable = None):
        """Update an existing hotkey"""
        if name in self.hotkeys:
            # Unregister old hotkey
            self.unregister_hotkey(name)
            
            # Register new hotkey
            return self.register_hotkey(name, new_combination, callback)
        else:
            # Register new hotkey
            return self.register_hotkey(name, new_combination, callback)
    
    def start_monitoring(self):
        """Start hotkey monitoring (this is handled automatically by keyboard library)"""
        self.running = True
        print("Hotkey monitoring started")
    
    def stop_monitoring(self):
        """Stop hotkey monitoring"""
        self.running = False
        self.unregister_all_hotkeys()
        print("Hotkey monitoring stopped")
    
    def validate_key_combination(self, combination: str) -> bool:
        """Validate if a key combination is valid"""
        try:
            formatted = self._format_key_combination(combination)
            # Try to register and immediately unregister to test validity
            test_name = f"test_{int(time.time())}"
            if self.register_hotkey(test_name, combination):
                self.unregister_hotkey(test_name)
                return True
            return False
        except:
            return False
    
    def get_available_keys(self) -> list:
        """Get list of available keys for hotkey combinations"""
        return [
            # Letters
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            # Numbers
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            # Special keys
            'enter', 'space', 'tab', 'escape', 'backspace', 'delete',
            # Function keys
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            # Arrow keys
            'up', 'down', 'left', 'right',
            # Modifier keys
            'ctrl', 'alt', 'shift', 'win'
        ]
    
    def get_example_combinations(self) -> list:
        """Get example hotkey combinations"""
        return [
            'alt+v',
            'ctrl+shift+v',
            'ctrl+alt+v',
            'win+v',
            'ctrl+shift+enter',
            'alt+space',
            'ctrl+alt+space',
            'f1',
            'ctrl+f1'
        ]


class HotkeyValidator:
    """Utility class for validating hotkey combinations"""
    
    @staticmethod
    def is_valid_combination(combination: str) -> bool:
        """Check if a key combination is valid"""
        if not combination or not isinstance(combination, str):
            return False
        
        combination = combination.lower().strip()
        
        # Must not be empty
        if not combination:
            return False
        
        # Split by + to get individual keys
        keys = [key.strip() for key in combination.split('+')]
        
        # Must have at least one key
        if not keys:
            return False
        
        # Check for valid keys
        valid_keys = HotkeyManager().get_available_keys()
        
        for key in keys:
            if key not in valid_keys:
                return False
        
        # Check for reasonable combination length (max 4 keys)
        if len(keys) > 4:
            return False
        
        # Check for duplicate keys
        if len(keys) != len(set(keys)):
            return False
        
        return True
    
    @staticmethod
    def suggest_combination(base_key: str) -> list:
        """Suggest hotkey combinations based on a base key"""
        suggestions = []
        
        # Single key
        if HotkeyValidator.is_valid_combination(base_key):
            suggestions.append(base_key)
        
        # With modifiers
        modifiers = ['ctrl', 'alt', 'shift', 'win']
        
        for modifier in modifiers:
            combination = f"{modifier}+{base_key}"
            if HotkeyValidator.is_valid_combination(combination):
                suggestions.append(combination)
        
        # With two modifiers
        for i, mod1 in enumerate(modifiers):
            for mod2 in modifiers[i+1:]:
                combination = f"{mod1}+{mod2}+{base_key}"
                if HotkeyValidator.is_valid_combination(combination):
                    suggestions.append(combination)
        
        return suggestions[:5]  # Return top 5 suggestions
