"""Window control plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
from core.logger import get_logger

logger = get_logger(__name__)

class WindowControlPlugin(BasePlugin):
    """Control application windows."""
    
    def get_intents(self) -> List[str]:
        return ["list_windows", "switch_window", "minimize_window", 
                "maximize_window", "close_window"]
    
    def get_description(self) -> str:
        return "Window control: list, switch, minimize, maximize, close windows"
    
    def get_prompt_examples(self) -> str:
        return """list_windows:
{
  "intent": "list_windows"
}

switch_window:
{
  "intent": "switch_window",
  "window_name": "Chrome"
}

minimize_window:
{
  "intent": "minimize_window",
  "window_name": "Notepad"
}

maximize_window:
{
  "intent": "maximize_window",
  "window_name": "Chrome"
}

close_window:
{
  "intent": "close_window",
  "window_name": "Calculator"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute window control operation."""
        intent_type = intent.get("intent")
        
        try:
            import pygetwindow as gw
            
            if intent_type == "list_windows":
                windows = gw.getAllTitles()
                # Filter out empty titles
                windows = [w for w in windows if w.strip()][:10]
                
                if not windows:
                    return "No windows found."
                
                result = "Open windows: "
                for i, window in enumerate(windows, 1):
                    result += f"{i}. {window[:30]}. "
                
                return result
            
            elif intent_type == "switch_window":
                window_name = intent.get("window_name", "").lower()
                if not window_name:
                    return "Please specify a window name."
                
                windows = gw.getWindowsWithTitle(window_name)
                if not windows:
                    # Try partial match
                    all_windows = gw.getAllWindows()
                    windows = [w for w in all_windows if window_name in w.title.lower()]
                
                if windows:
                    windows[0].activate()
                    logger.info(f"Switched to window: {windows[0].title}")
                    return f"Switched to {windows[0].title}"
                else:
                    return f"Window not found: {window_name}"
            
            elif intent_type == "minimize_window":
                window_name = intent.get("window_name", "").lower()
                if not window_name:
                    return "Please specify a window name."
                
                windows = gw.getWindowsWithTitle(window_name)
                if not windows:
                    all_windows = gw.getAllWindows()
                    windows = [w for w in all_windows if window_name in w.title.lower()]
                
                if windows:
                    windows[0].minimize()
                    logger.info(f"Minimized window: {windows[0].title}")
                    return f"Minimized {windows[0].title}"
                else:
                    return f"Window not found: {window_name}"
            
            elif intent_type == "maximize_window":
                window_name = intent.get("window_name", "").lower()
                if not window_name:
                    return "Please specify a window name."
                
                windows = gw.getWindowsWithTitle(window_name)
                if not windows:
                    all_windows = gw.getAllWindows()
                    windows = [w for w in all_windows if window_name in w.title.lower()]
                
                if windows:
                    windows[0].maximize()
                    logger.info(f"Maximized window: {windows[0].title}")
                    return f"Maximized {windows[0].title}"
                else:
                    return f"Window not found: {window_name}"
            
            elif intent_type == "close_window":
                window_name = intent.get("window_name", "").lower()
                if not window_name:
                    return "Please specify a window name."
                
                windows = gw.getWindowsWithTitle(window_name)
                if not windows:
                    all_windows = gw.getAllWindows()
                    windows = [w for w in all_windows if window_name in w.title.lower()]
                
                if windows:
                    windows[0].close()
                    logger.info(f"Closed window: {windows[0].title}")
                    return f"Closed {windows[0].title}"
                else:
                    return f"Window not found: {window_name}"
            
            else:
                return "Unknown window control command."
                
        except ImportError:
            return "Window control requires pygetwindow. Please install it."
        except Exception as e:
            logger.error(f"Window control plugin error: {e}")
            return "Sorry, I couldn't perform the window operation."
