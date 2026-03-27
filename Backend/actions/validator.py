import json
import re
from actions.intents import ALLOWED_INTENTS
from core.logger import get_logger

logger = get_logger(__name__)

def extract_json(text):
    """Extract JSON from text that might contain extra content."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group() if match else None

def validate_intent(text):
    """
    Validate and extract intent from LLM response.
    
    Returns:
        dict: Valid intent or None
    """
    json_text = extract_json(text)
    if not json_text:
        logger.debug("No JSON found in LLM response")
        return None

    try:
        intent = json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in LLM response: {e}")
        return None

    name = intent.get("intent")
    
    # Check if intent name exists
    if not name:
        logger.debug("No intent field in JSON")
        return None
    
    # If intent is "none", return None
    if name == "none":
        return None
    
    # Volume controls (no parameters needed)
    if name in ["volume_up", "volume_down", "mute", "unmute"]:
        return intent
    
    # Shutdown (no parameters needed)
    if name == "shutdown_request":
        return intent

    # Open app - validate against allowed apps
    if name == "open_app":
        app = intent.get("app")
        if app in ALLOWED_INTENTS["open_app"]:
            return intent
        logger.debug(f"Unknown app: {app}")
        return None

    # Open folder - validate against allowed folders
    if name == "open_folder":
        folder = intent.get("folder")
        if folder in ALLOWED_INTENTS["open_folder"]:
            return intent
        logger.debug(f"Unknown folder: {folder}")
        return None
    
    # For all other intents (plugins), accept them as valid
    # The plugin manager will handle validation
    logger.debug(f"Accepting intent for plugin handling: {name}")
    return intent

