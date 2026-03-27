from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter
from core.config import CONTEXT_HISTORY_SIZE
from core.logger import get_logger
import json

logger = get_logger(__name__)

class ConversationContext:
    """Manages conversation history and context for context-aware responses."""
    
    def __init__(self, max_history=CONTEXT_HISTORY_SIZE):
        """
        Initialize conversation context.
        
        Args:
            max_history: Maximum number of exchanges to keep in history
        """
        self.max_history = max_history
        self.history: List[Dict] = []
        self.user_preferences: Dict = {}
        self.session_start = datetime.now()
        self.command_patterns: Counter = Counter()
        
    def add_exchange(self, user_input: str, assistant_response: str, intent: Optional[Dict] = None):
        """
        Add a conversation exchange to history.
        
        Args:
            user_input: What the user said
            assistant_response: What the assistant responded
            intent: Recognized intent (optional)
        """
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response,
            "intent": intent
        }
        
        self.history.append(exchange)
        
        # Track command patterns
        if intent:
            intent_type = intent.get("intent", "unknown")
            self.command_patterns[intent_type] += 1
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        logger.debug(f"Added exchange to context. History size: {len(self.history)}")
    
    def get_context_prompt(self) -> str:
        """
        Generate context prompt for LLM.
        
        Returns:
            str: Formatted conversation history
        """
        if not self.history:
            return ""
        
        context_lines = ["Recent conversation history:"]
        
        for exchange in self.history[-5:]:  # Last 5 exchanges
            context_lines.append(f"User: {exchange['user']}")
            context_lines.append(f"Assistant: {exchange['assistant']}")
        
        context_lines.append("\nCurrent user request:")
        
        return "\n".join(context_lines)
    
    def get_last_user_input(self) -> Optional[str]:
        """Get the last thing the user said."""
        if self.history:
            return self.history[-1]["user"]
        return None
    
    def get_last_intent(self) -> Optional[Dict]:
        """Get the last recognized intent."""
        if self.history:
            return self.history[-1].get("intent")
        return None

    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response."""
        if self.history:
            return self.history[-1].get("assistant")
        return None
    
    def get_most_common_commands(self, limit=5) -> List[tuple]:
        """
        Get most frequently used commands.
        
        Args:
            limit: Number of commands to return
            
        Returns:
            List of (command, count) tuples
        """
        return self.command_patterns.most_common(limit)
    
    def get_suggestions(self) -> List[str]:
        """
        Get proactive suggestions based on patterns.
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Suggest based on time of day
        hour = datetime.now().hour
        if 9 <= hour < 12:
            suggestions.append("Good morning! Ready to start work mode?")
        elif 17 <= hour < 20:
            suggestions.append("End of day? I can help you wrap up.")
        
        # Suggest based on common commands
        common = self.get_most_common_commands(3)
        if common:
            most_used = common[0][0]
            if most_used == "open_app":
                suggestions.append("You often open apps. Try 'work mode' shortcut!")
        
        return suggestions
    
    def set_preference(self, key: str, value: any):
        """
        Store a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.user_preferences[key] = value
        logger.info(f"Set user preference: {key} = {value}")
    
    def get_preference(self, key: str, default=None):
        """
        Get a user preference.
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Stored preference or default
        """
        return self.user_preferences.get(key, default)
    
    def clear_history(self):
        """Clear conversation history."""
        self.history = []
        self.command_patterns.clear()
        logger.info("Conversation history cleared")
    
    def get_session_duration(self) -> float:
        """Get session duration in minutes."""
        delta = datetime.now() - self.session_start
        return delta.total_seconds() / 60
    
    def to_dict(self) -> Dict:
        """Export context as dictionary."""
        return {
            "history": self.history,
            "preferences": self.user_preferences,
            "patterns": dict(self.command_patterns),
            "session_start": self.session_start.isoformat(),
            "session_duration_minutes": self.get_session_duration()
        }
    
    def save_to_file(self, filepath: str):
        """Save context to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Context saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
    
    def load_from_file(self, filepath: str):
        """Load context from JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.history = data.get("history", [])
            self.user_preferences = data.get("preferences", {})
            self.command_patterns = Counter(data.get("patterns", {}))
            
            logger.info(f"Context loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
