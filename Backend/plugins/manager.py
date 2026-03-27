"""Plugin manager for loading and managing plugins."""

import os
import importlib
import inspect
from typing import Dict, List, Optional
from plugins.base import BasePlugin
from core.logger import get_logger

logger = get_logger(__name__)

class PluginManager:
    """Manages plugin loading, execution, and lifecycle."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialize plugin manager.
        
        Args:
            plugins_dir: Directory containing plugins
        """
        # Handle frozen state (PyInstaller)
        import sys
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_dir = sys._MEIPASS
            self.plugins_dir = os.path.join(base_dir, "plugins")
        else:
            self.plugins_dir = plugins_dir
            
        self.plugins: Dict[str, BasePlugin] = {}
        self.intent_map: Dict[str, str] = {}  # intent -> plugin_name
        
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugins directory.
        
        Returns:
            List of plugin module names
        """
        if not os.path.exists(self.plugins_dir):
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []
        
        plugin_files = []
        
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                if filename not in ['base.py', 'manager.py']:
                    plugin_files.append(filename[:-3])  # Remove .py
        
        logger.info(f"Discovered {len(plugin_files)} plugins: {plugin_files}")
        return plugin_files
    
    def load_plugin(self, module_name: str) -> bool:
        """
        Load a single plugin.
        
        Args:
            module_name: Plugin module name
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            # Import the module
            module = importlib.import_module(f"plugins.{module_name}")
            
            # Find plugin class (subclass of BasePlugin)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                    # Instantiate plugin
                    plugin = obj()
                    plugin_name = plugin.name
                    
                    # Register plugin
                    self.plugins[plugin_name] = plugin
                    
                    # Map intents to plugin
                    for intent in plugin.get_intents():
                        self.intent_map[intent] = plugin_name
                    
                    # Call on_load
                    plugin.on_load()
                    
                    logger.info(f"Loaded plugin: {plugin_name} (intents: {plugin.get_intents()})")
                    return True
            
            logger.warning(f"No plugin class found in {module_name}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load plugin {module_name}: {e}")
            return False
    
    def load_all_plugins(self):
        """Discover and load all available plugins."""
        plugin_modules = self.discover_plugins()
        
        loaded = 0
        for module_name in plugin_modules:
            if self.load_plugin(module_name):
                loaded += 1
        
        logger.info(f"Loaded {loaded}/{len(plugin_modules)} plugins")
    
    def execute_plugin(self, intent: Dict) -> Optional[str]:
        """
        Execute a plugin based on intent.
        
        Args:
            intent: Intent dictionary
            
        Returns:
            str: Plugin response or None if no plugin handles it
        """
        intent_name = intent.get("intent")
        
        if intent_name not in self.intent_map:
            return None
        
        plugin_name = self.intent_map[intent_name]
        plugin = self.plugins.get(plugin_name)
        
        if not plugin or not plugin.enabled:
            return None
        
        try:
            logger.debug(f"Executing plugin {plugin_name} for intent {intent_name}")
            return plugin.execute(intent)
        except Exception as e:
            logger.error(f"Plugin execution failed ({plugin_name}): {e}")
            return f"Plugin error: {e}"
    
    def get_all_intents(self) -> List[str]:
        """Get all intents from all loaded plugins."""
        return list(self.intent_map.keys())
    
    def get_plugin_prompts(self) -> str:
        """
        Get combined prompt examples from all plugins.
        
        Returns:
            str: Combined prompt examples for LLM
        """
        prompts = []
        
        for plugin in self.plugins.values():
            if plugin.enabled:
                example = plugin.get_prompt_examples()
                if example:
                    prompts.append(example)
        
        return "\n\n".join(prompts)
    
    def unload_all_plugins(self):
        """Unload all plugins."""
        for plugin in self.plugins.values():
            try:
                plugin.on_unload()
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin.name}: {e}")
        
        self.plugins.clear()
        self.intent_map.clear()
        logger.info("All plugins unloaded")
