"""Base plugin class for David AI Assistant plugins."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from core.logger import get_logger

logger = get_logger(__name__)

class BasePlugin(ABC):
    """Base class for all David AI plugins."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.name = self.__class__.__name__
        self.enabled = True
        
    @abstractmethod
    def get_intents(self) -> List[str]:
        """
        Return list of intent names this plugin handles.
        
        Returns:
            List of intent names (e.g., ['weather', 'forecast'])
        """
        pass
    
    @abstractmethod
    def execute(self, intent: Dict) -> str:
        """
        Execute the plugin action.
        
        Args:
            intent: Intent dictionary with 'intent' and optional parameters
            
        Returns:
            str: Response message
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get plugin description.
        
        Returns:
            str: Human-readable description
        """
        pass
    
    def get_prompt_examples(self) -> str:
        """
        Get example prompts for LLM intent extraction.
        
        Returns:
            str: Formatted examples for system prompt
        """
        return ""
    
    def validate_intent(self, intent: Dict) -> bool:
        """
        Validate if intent is properly formatted.
        
        Args:
            intent: Intent dictionary
            
        Returns:
            bool: True if valid
        """
        return intent.get("intent") in self.get_intents()
    
    def on_load(self):
        """Called when plugin is loaded."""
        logger.info(f"Plugin loaded: {self.name}")
    
    def on_unload(self):
        """Called when plugin is unloaded."""
        logger.info(f"Plugin unloaded: {self.name}")
