import os
import json
import subprocess
from typing import List, Dict
from plugins.base import BasePlugin
from core.logger import get_logger

logger = get_logger(__name__)

ACTIONS_FILE = os.path.join(os.getcwd(), "actions.json")

class AutomationPlugin(BasePlugin):
    """
    Universal Action Engine.
    Executes custom scripts/commands defined in actions.json based on voice triggers.
    """
    
    def __init__(self):
        super().__init__()
        self.actions = []
        self.load_actions()
        
    def load_actions(self):
        """Load actions from JSON file."""
        if os.path.exists(ACTIONS_FILE):
            try:
                with open(ACTIONS_FILE, 'r') as f:
                    self.actions = json.load(f)
                logger.info(f"Loaded {len(self.actions)} custom automation actions")
            except Exception as e:
                logger.error(f"Failed to load actions.json: {e}")
                self.actions = []
        else:
            logger.warning("actions.json not found. Automation plugin inactive.")

    def get_intents(self) -> List[str]:
        # We return a generic 'automation_action' intent
        # The PluginManager/LLM usually maps intents.
        # However, for this to work robustly with 'phi3', we might need to 
        # extend the prompts dynamically.
        return ["automation_action"]
    
    def get_description(self) -> str:
        return "Execute custom automation actions (lights, scripts, apps)"
    
    def get_prompt_examples(self) -> str:
        # Dynamically build examples based on loaded actions
        if not self.actions:
            return ""
            
        examples = []
        for action in self.actions[:5]: # Limit to 5 examples to save context
            trigger = action['triggers'][0]
            example = f"""{trigger}:
{{
  "intent": "automation_action",
  "action_name": "{action['name']}"
}}"""
            examples.append(example)
            
        return "\n\n".join(examples)
    
    def execute(self, intent: Dict) -> str:
        """Execute the requested action."""
        action_name = intent.get("action_name")
        
        # Find the action
        target_action = next((a for a in self.actions if a["name"].lower() == action_name.lower()), None)
        
        if not target_action:
            # Fallback: Try to match trigger if LLM passed trigger text instead of name
            # (Just in case)
            return "Command not recognized in actions list."
            
        action_type = target_action.get("type", "command")
        payload = target_action.get("payload", "")
        response_text = target_action.get("response", "Action executed.")
        
        try:
            if action_type == "command":
                # Run shell command
                logger.info(f"Executing automation command: {payload}")
                subprocess.Popen(payload, shell=True)
                return response_text
                
            elif action_type == "script":
                # Run python script or similar
                path = os.path.abspath(payload)
                if os.path.exists(path):
                    logger.info(f"Executing automation script: {path}")
                    subprocess.Popen(f"python {path}", shell=True)
                    return response_text
                else:
                    return f"Script not found: {payload}"
                    
            elif action_type == "http":
                # TODO: Implement HTTP requests (GET/POST) for IoT
                return "HTTP actions not yet implemented."
                
            else:
                return f"Unknown action type: {action_type}"
                
        except Exception as e:
            logger.error(f"Automation execution failed: {e}")
            return f"Failed to execute action: {str(e)}"
