import os
import pyautogui
from plugins.base import BasePlugin
import tempfile
import time
import base64
import requests
from core.config import OLLAMA_URL, VISION_MODEL

def analyze_image(image_path: str, query: str) -> str:
    """Analyze an image using the Ollama vision model."""
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            "model": VISION_MODEL,
            "prompt": query,
            "images": [image_data],
            "stream": False
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("response", "I could not analyze the image.").strip()
    except Exception as e:
        return f"Vision analysis failed: {e}"


class VisionPlugin(BasePlugin):
    """Plugin for visual analysis of the screen."""

    def __init__(self):
        super().__init__()
        self.name = "Vision"

    def get_description(self) -> str:
        return "Analyzes the screen using a vision model to answer questions about what is visible."

    def get_intents(self) -> list:
        return ["analyze_screen", "read_screen"]
        
    def get_prompt_examples(self) -> str:
        return """
        "What is on my screen?" -> {"intent": "analyze_screen"}
        "Read this text" -> {"intent": "read_screen"}
        """
        
    def execute(self, intent: dict) -> str:
        # Take screenshot
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            temp_path = os.path.join(tempfile.gettempdir(), f"vision_capture_{timestamp}.png")
            
            # Capture
            screenshot = pyautogui.screenshot()
            screenshot.save(temp_path)
            
            # Get user query from intent dict
            query = intent.get("query", "Describe what you see on the screen in detail.")
            if not query:
                query = "Describe this screen."
                
            # Analyze
            result = analyze_image(temp_path, query)
            
            # Cleanup
            try:
                os.remove(temp_path)
            except:
                pass
                
            return result
            
        except Exception as e:
            return f"Failed to see screen: {e}"
