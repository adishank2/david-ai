"""
Agentic Auto-Pilot Plugin for David AI.
Uses PyAutoGUI and Keyboard automation to physically control the PC.
"""
import time
import pyautogui # pyre-ignore
from typing import Dict, Any, List
from core.logger import get_logger
from plugins.base import BasePlugin

logger = get_logger(__name__)

# Failsafe: moving mouse to 0,0 kills PyAutoGUI
pyautogui.FAILSAFE = True

class AutoPilotPlugin(BasePlugin):
    """
    Handles physical mouse and keyboard automation.
    """
    
    def __init__(self):
        super().__init__()
        
    def get_intents(self) -> List[str]:
        return ["autopilot_type", "autopilot_key", "autopilot_scroll"]
        
    def get_description(self) -> str:
        return "Agentic physical control of mouse/keyboard."
        
    def get_prompt_examples(self) -> str:
        return """
AGENTIC AUTO-PILOT HANDLER:
If the user specifically asks to physically "type [text]", "press enter", "click", or "scroll":
`{"intent": "autopilot_type", "text": "exact text to type", "press_enter": true}`
`{"intent": "autopilot_key", "key": "enter/tab/escape/space"}`
`{"intent": "autopilot_scroll", "direction": "down/up"}`
"""

    def execute(self, intent_data: Dict[str, Any]) -> str:
        intent = intent_data.get("intent")
        
        try:
            if intent == "autopilot_type":
                text = intent_data.get("text", "")
                press_enter = intent_data.get("press_enter", False)
                logger.info(f"🤖 [AutoPilot] Typing: {text}")
                pyautogui.write(text, interval=0.02)
                if press_enter:
                    pyautogui.press('enter')
                return f"Agent typed exactly: '{text}'"
                
            elif intent == "autopilot_key":
                key = intent_data.get("key", "enter").lower()
                logger.info(f"🤖 [AutoPilot] Pressing {key}")
                pyautogui.press(key)
                return f"Agent pressed the {key} key."
                
            elif intent == "autopilot_scroll":
                direction = intent_data.get("direction", "down")
                scroll_amount = -500 if direction == "down" else 500
                logger.info(f"🤖 [AutoPilot] Scrolling {direction}")
                pyautogui.scroll(scroll_amount)
                return f"Agent scrolled {direction}."
                
        except Exception as e:
            logger.error(f"AutoPilot failed: {e}")
            return f"Agent encountered a physical control error: {e}"
            
        return "Unknown command for autopilot."
