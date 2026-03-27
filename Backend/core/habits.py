"""
David AI 2.0 — Habit Tracker & Smart Suggestions Engine
Learns user patterns (app usage, command times) and proactively suggests actions.
"""
import os
import json
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional
from core.logger import get_logger
from core.config import BASE_DIR

logger = get_logger(__name__)

HABITS_FILE = os.path.join(BASE_DIR, "user_habits.json")


class HabitTracker:
    """
    Tracks user actions with timestamps to learn behavioral patterns.
    Example: user opens Chrome every day at 10AM, or always asks for weather at 8AM.
    """
    
    def __init__(self):
        self.habits: List[Dict] = []
        self.patterns: Dict[str, Dict] = {}   # computed patterns
        self._lock = threading.Lock()
        self._load()
    
    # ── Persistence ──────────────────────────────────────
    def _load(self):
        if os.path.exists(HABITS_FILE):
            try:
                with open(HABITS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.habits = data.get("habits", [])
                    self.patterns = data.get("patterns", {})
                logger.info(f"Loaded {len(self.habits)} habit records.")
            except Exception as e:
                logger.error(f"Failed to load habits: {e}")
    
    def _save(self):
        try:
            with open(HABITS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "habits": self.habits[-500:],  # Keep last 500 entries max
                    "patterns": self.patterns
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save habits: {e}")
    
    # ── Record Actions ───────────────────────────────────
    def record_action(self, action: str, category: str = "command"):
        """Record a user action with timestamp for pattern learning."""
        now = datetime.now()
        entry = {
            "action": action.lower().strip(),
            "category": category,
            "timestamp": now.isoformat(),
            "hour": now.hour,
            "minute": now.minute,
            "weekday": now.strftime("%A"),
            "date": now.strftime("%Y-%m-%d")
        }
        
        with self._lock:
            self.habits.append(entry)
            
            # Recompute patterns every 20 recorded actions
            if len(self.habits) % 20 == 0:
                self._analyze_patterns()
            
            self._save()
    
    # ── Pattern Analysis ─────────────────────────────────
    def _analyze_patterns(self):
        """Analyze habits to find recurring time-based patterns."""
        logger.info("Analyzing user habit patterns...")
        
        # Group actions by hour of day
        hourly = defaultdict(lambda: defaultdict(int))
        # Group by weekday + hour
        weekly = defaultdict(lambda: defaultdict(int))
        
        for h in self.habits:
            action = h["action"]
            hour = h["hour"]
            weekday = h.get("weekday", "Unknown")
            
            hourly[action][hour] += 1
            weekly[action][f"{weekday}_{hour}"] += 1
        
        # Find patterns: actions that happen 3+ times at the same hour
        detected = {}
        for action, hours in hourly.items():
            for hour, count in hours.items():
                if count >= 3:  # Minimum 3 occurrences to call it a pattern
                    key = f"{action}_at_{hour}"
                    detected[key] = {
                        "action": action,
                        "hour": hour,
                        "frequency": count,
                        "type": "daily_pattern",
                        "suggestion": self._generate_suggestion(action, hour)
                    }
        
        self.patterns = detected
        logger.info(f"Found {len(detected)} habit patterns.")
    
    def _generate_suggestion(self, action: str, hour: int) -> str:
        """Generate a human-readable suggestion from a pattern."""
        period = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
        time_str = f"{hour}:00" if hour > 9 else f"0{hour}:00"
        
        # Detect common apps
        app_keywords = {
            "chrome": "open Chrome",
            "code": "open VS Code",
            "spotify": "play music on Spotify",
            "youtube": "watch YouTube",
            "mail": "check your email",
            "weather": "check the weather",
            "news": "read the news",
            "whatsapp": "check WhatsApp",
        }
        
        friendly_action = action
        for kw, phrase in app_keywords.items():
            if kw in action:
                friendly_action = phrase
                break
        
        return f"You usually {friendly_action} around {time_str} every {period}. Should I do that now?"
    
    # ── Smart Suggestions ────────────────────────────────
    def get_suggestions(self, max_suggestions: int = 3) -> List[Dict]:
        """Get suggestions based on current time and learned patterns."""
        now = datetime.now()
        current_hour = now.hour
        suggestions = []
        
        for key, pattern in self.patterns.items():
            # Suggest if the pattern hour is within ±1 of current hour
            if abs(pattern["hour"] - current_hour) <= 1:
                suggestions.append({
                    "action": pattern["action"],
                    "suggestion": pattern["suggestion"],
                    "confidence": min(pattern["frequency"] * 15, 95),  # Cap at 95%
                    "hour": pattern["hour"]
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:max_suggestions]
    
    def get_stats(self) -> Dict:
        """Return habit tracking statistics."""
        return {
            "total_actions": len(self.habits),
            "patterns_found": len(self.patterns),
            "tracking_since": self.habits[0]["timestamp"] if self.habits else None
        }


# ── Singleton ────────────────────────────────────────────
_tracker = None

def get_habit_tracker() -> HabitTracker:
    global _tracker
    if _tracker is None:
        _tracker = HabitTracker()
    return _tracker


class SmartSuggestionAgent(threading.Thread):
    """Background agent that checks habits and suggests actions proactively."""
    
    def __init__(self, check_interval_sec=600):
        super().__init__(daemon=True)
        self.check_interval_sec = check_interval_sec
        self.running = False
        self._last_suggested = set()
    
    def start_agent(self):
        if not self.running:
            self.running = True
            self.start()
            logger.info("Smart Suggestion Agent started.")
    
    def stop_agent(self):
        self.running = False
    
    def run(self):
        time.sleep(60)  # Wait for system boot
        
        while self.running:
            try:
                tracker = get_habit_tracker()
                suggestions = tracker.get_suggestions()
                
                for s in suggestions:
                    # Only suggest once per session per action
                    key = f"{s['action']}_{datetime.now().strftime('%Y-%m-%d_%H')}"
                    if key not in self._last_suggested and s["confidence"] >= 60:
                        self._last_suggested.add(key)
                        
                        # Speak the suggestion
                        try:
                            from voice.tts import speak
                            speak(s["suggestion"])
                        except Exception as e:
                            logger.error(f"Failed to speak suggestion: {e}")
                        
                        break  # Only one suggestion at a time
                        
            except Exception as e:
                logger.error(f"Suggestion agent error: {e}")
            
            for _ in range(self.check_interval_sec):
                if not self.running:
                    break
                time.sleep(1)


# ── Global agent ─────────────────────────────────────────
_suggestion_agent = None

def start_suggestion_agent():
    global _suggestion_agent
    if _suggestion_agent is None:
        _suggestion_agent = SmartSuggestionAgent(check_interval_sec=300)
        _suggestion_agent.start_agent()

def stop_suggestion_agent():
    global _suggestion_agent
    if _suggestion_agent:
        _suggestion_agent.stop_agent()
        _suggestion_agent = None
