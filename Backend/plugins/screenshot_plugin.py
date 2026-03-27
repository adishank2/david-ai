"""Screenshot and OCR plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
from PIL import ImageGrab, Image
import os
from datetime import datetime
from core.logger import get_logger
from core.config import SCREENSHOT_SAVE_DIR, SCREENSHOT_OCR_ENABLED

logger = get_logger(__name__)

class ScreenshotPlugin(BasePlugin):
    """Take screenshots and extract text using OCR."""
    
    def __init__(self):
        super().__init__()
        # Create screenshot directory if it doesn't exist
        if not os.path.exists(SCREENSHOT_SAVE_DIR):
            os.makedirs(SCREENSHOT_SAVE_DIR)
            logger.info(f"Created screenshot directory: {SCREENSHOT_SAVE_DIR}")
    
    def get_intents(self) -> List[str]:
        return ["take_screenshot"]
    
    def get_description(self) -> str:
        return "Take screenshots"
    
    def get_prompt_examples(self) -> str:
        return """take_screenshot:
{
  "intent": "take_screenshot",
  "save": true (optional, default true)
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute screenshot operation."""
        intent_type = intent.get("intent")
        
        try:
            if intent_type == "take_screenshot":
                save = intent.get("save", True)
                
                # Take screenshot
                screenshot = ImageGrab.grab()
                
                if save:
                    # Generate filename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(SCREENSHOT_SAVE_DIR, filename)
                    
                    # Save screenshot
                    screenshot.save(filepath)
                    logger.info(f"Screenshot saved: {filepath}")
                    
                    # Open the file on Windows so the user can immediately see it!
                    try:
                        os.startfile(filepath)
                    except Exception as e:
                        logger.error(f"Failed to open screenshot: {e}")
                        
                    return "Screenshot saved successfully"
                else:
                    return "Screenshot taken (not saved)"
            
            elif intent_type == "screenshot_ocr":
                if not SCREENSHOT_OCR_ENABLED:
                    return "OCR is disabled. Enable it in config."
                
                try:
                    import pytesseract
                except ImportError:
                    return "OCR requires pytesseract. Please install Tesseract OCR."
                
                # Take screenshot
                screenshot = ImageGrab.grab()
                
                # Extract text
                text = pytesseract.image_to_string(screenshot)
                
                if not text.strip():
                    return "No text found in screenshot."
                
                logger.info(f"OCR extracted {len(text)} characters")
                # Return first 200 characters
                preview = text[:200] + "..." if len(text) > 200 else text
                return f"Text from screenshot: {preview}"
            
            else:
                return "Unknown screenshot command."
                
        except Exception as e:
            logger.error(f"Screenshot plugin error: {e}")
            return "Sorry, I couldn't take the screenshot."
