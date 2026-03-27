"""
Personality and conversational responses for David AI.
Makes David more human-friendly and natural.
"""

import random
from typing import Optional

class Personality:
    """Manages David's personality and conversational responses."""
    
    # Casual acknowledgments
    ACKNOWLEDGMENTS = [
        "Got it!",
        "On it!",
        "Sure thing!",
        "You got it!",
        "No problem!",
        "Right away!",
        "Consider it done!",
    ]
    
    # Success messages
    SUCCESS = [
        "Done!",
        "All set!",
        "There you go!",
        "Finished!",
        "Complete!",
    ]
    
    # Thinking/processing
    THINKING = [
        "Let me check...",
        "One moment...",
        "Working on it...",
        "Give me a sec...",
        "Let me see...",
    ]
    
    # Error messages (helpful, not technical)
    ERRORS = {
        "not_found": [
            "Hmm, I couldn't find that.",
            "I don't see that anywhere.",
            "Can't seem to locate that.",
        ],
        "failed": [
            "Oops, that didn't work.",
            "Something went wrong there.",
            "I couldn't do that.",
        ],
        "unclear": [
            "I'm not sure what you mean.",
            "Could you say that differently?",
            "I didn't quite catch that.",
        ],
    }
    
    # Greetings based on time
    GREETINGS = {
        "morning": ["Good morning!", "Morning!", "Hey, good morning!"],
        "afternoon": ["Good afternoon!", "Hey there!", "Afternoon!"],
        "evening": ["Good evening!", "Evening!", "Hey!"],
        "night": ["Hey there!", "Hello!", "Hi!"],
    }
    
    # Follow-up questions
    FOLLOW_UPS = [
        "Anything else?",
        "What else can I do?",
        "Need anything else?",
        "What's next?",
        "Can I help with anything else?",
    ]
    
    @staticmethod
    def acknowledge() -> str:
        """Get a casual acknowledgment."""
        return random.choice(Personality.ACKNOWLEDGMENTS)
    
    @staticmethod
    def success(add_followup: bool = True) -> str:
        """Get a success message."""
        msg = random.choice(Personality.SUCCESS)
        if add_followup and random.random() > 0.5:
            msg += " " + random.choice(Personality.FOLLOW_UPS)
        return msg
    
    @staticmethod
    def thinking() -> str:
        """Get a thinking message."""
        return random.choice(Personality.THINKING)
    
    @staticmethod
    def error(error_type: str = "failed") -> str:
        """Get a helpful error message."""
        errors = Personality.ERRORS.get(error_type, Personality.ERRORS["failed"])
        return random.choice(errors)
    
    @staticmethod
    def greeting(time_of_day: str = "morning") -> str:
        """Get a time-appropriate greeting."""
        greetings = Personality.GREETINGS.get(time_of_day, Personality.GREETINGS["morning"])
        return random.choice(greetings)
    
    @staticmethod
    def get_time_of_day() -> str:
        """Determine time of day."""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    @staticmethod
    def make_friendly(response: str) -> str:
        """
        Make a response more friendly and conversational.
        
        Args:
            response: Original response
            
        Returns:
            Friendlier version
        """
        # Replace technical terms
        replacements = {
            "Command executed": Personality.success(),
            "Error": Personality.error("failed"),
            "Not found": Personality.error("not_found"),
            "Unknown": Personality.error("unclear"),
            "Processing": Personality.thinking(),
        }
        
        for old, new in replacements.items():
            if old.lower() in response.lower():
                return new
        
        return response

# Global personality instance
_personality = Personality()

def get_personality() -> Personality:
    """Get the global personality instance."""
    return _personality
