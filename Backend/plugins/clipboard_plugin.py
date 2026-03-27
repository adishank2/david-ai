"""Clipboard manager plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import pyperclip
from core.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

class ClipboardPlugin(BasePlugin):
    """Manage clipboard operations and history."""
    
    def __init__(self):
        super().__init__()
        self.history = []  # Store clipboard history
        self.max_history = 10
    
    def get_intents(self) -> List[str]:
        return ["copy_to_clipboard", "read_clipboard", "clipboard_history", "clear_clipboard"]
    
    def get_description(self) -> str:
        return "Manage clipboard: copy text, read content, view history"
    
    def get_prompt_examples(self) -> str:
        return """copy_to_clipboard:
{
  "intent": "copy_to_clipboard",
  "text": "text to copy"
}

read_clipboard:
{
  "intent": "read_clipboard"
}

clipboard_history:
{
  "intent": "clipboard_history"
}

clear_clipboard:
{
  "intent": "clear_clipboard"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute clipboard operation."""
        intent_type = intent.get("intent")
        
        try:
            if intent_type == "copy_to_clipboard":
                text = intent.get("text", "")
                if not text:
                    return "No text provided to copy."
                
                pyperclip.copy(text)
                self._add_to_history(text)
                logger.info(f"Copied to clipboard: {text[:50]}...")
                return f"Copied to clipboard: {text[:50]}..."
            
            elif intent_type == "read_clipboard":
                content = pyperclip.paste()
                if not content:
                    return "Clipboard is empty."
                logger.info(f"Read clipboard: {content[:50]}...")
                return f"Clipboard contains: {content}"
            
            elif intent_type == "clipboard_history":
                if not self.history:
                    return "Clipboard history is empty."
                
                history_text = "Recent clipboard items: "
                for i, item in enumerate(self.history[-5:], 1):
                    preview = item['text'][:30] + "..." if len(item['text']) > 30 else item['text']
                    history_text += f"{i}. {preview}. "
                
                return history_text
            
            elif intent_type == "clear_clipboard":
                pyperclip.copy("")
                logger.info("Clipboard cleared")
                return "Clipboard cleared."
            
            else:
                return "Unknown clipboard command."
                
        except Exception as e:
            logger.error(f"Clipboard plugin error: {e}")
            return "Sorry, I couldn't perform the clipboard operation."
    
    def _add_to_history(self, text: str):
        """Add item to clipboard history."""
        self.history.append({
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last N items
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
