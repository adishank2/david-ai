"""
Custom command shortcuts for David AI.
Allows users to define custom voice commands that map to actions.
"""

import json
import os
from typing import Dict, Any, Optional
from core.logger import get_logger

logger = get_logger(__name__)

class ShortcutManager:
    """Manages custom command shortcuts."""
    
    def __init__(self, shortcuts_file="shortcuts.json"):
        self.shortcuts_file = shortcuts_file
        self.shortcuts: Dict[str, Dict[str, Any]] = {}
        self.load_shortcuts()
    
    def load_shortcuts(self):
        """Load shortcuts from file."""
        try:
            if os.path.exists(self.shortcuts_file):
                with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                    self.shortcuts = json.load(f)
                logger.info(f"Loaded {len(self.shortcuts)} shortcuts")
            else:
                # Create default shortcuts
                self.shortcuts = {
                    "work mode": {
                        "description": "Open work applications",
                        "actions": [
                            {"intent": "open_app", "app": "chrome"},
                            {"intent": "open_app", "app": "notepad"},
                            {"intent": "open_folder", "folder": "documents"}
                        ]
                    },
                    "focus mode": {
                        "description": "Minimize distractions",
                        "actions": [
                            {"intent": "mute"},
                            {"intent": "open_app", "app": "notepad"}
                        ]
                    },
                    "end day": {
                        "description": "Close everything and prepare to shutdown",
                        "actions": [
                            {"intent": "mute"}
                        ]
                    }
                }
                self.save_shortcuts()
        except Exception as e:
            logger.error(f"Failed to load shortcuts: {e}")
            self.shortcuts = {}
    
    def save_shortcuts(self):
        """Save shortcuts to file."""
        try:
            with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, indent=2)
            logger.info(f"Saved {len(self.shortcuts)} shortcuts")
        except Exception as e:
            logger.error(f"Failed to save shortcuts: {e}")
    
    def get_shortcut(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Get shortcut for a command.
        
        Args:
            command: Voice command
            
        Returns:
            Shortcut definition or None
        """
        command_lower = command.lower().strip()
        return self.shortcuts.get(command_lower)
    
    def add_shortcut(self, name: str, description: str, actions: list):
        """
        Add a new shortcut.
        
        Args:
            name: Shortcut name
            description: Description of what it does
            actions: List of actions to execute
        """
        self.shortcuts[name.lower()] = {
            "description": description,
            "actions": actions
        }
        self.save_shortcuts()
        logger.info(f"Added shortcut: {name}")
    
    def remove_shortcut(self, name: str) -> bool:
        """
        Remove a shortcut.
        
        Args:
            name: Shortcut name
            
        Returns:
            True if removed, False if not found
        """
        name_lower = name.lower()
        if name_lower in self.shortcuts:
            del self.shortcuts[name_lower]
            self.save_shortcuts()
            logger.info(f"Removed shortcut: {name}")
            return True
        return False
    
    def list_shortcuts(self) -> Dict[str, str]:
        """
        List all shortcuts.
        
        Returns:
            Dict of shortcut names to descriptions
        """
        return {name: data["description"] for name, data in self.shortcuts.items()}

# Global shortcut manager
_manager = ShortcutManager()

def get_shortcut_manager() -> ShortcutManager:
    """Get the global shortcut manager."""
    return _manager
