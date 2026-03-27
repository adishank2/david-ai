"""
Proactive Assistant Mode for David AI.
Runs in the background and proactively notifies the user about system warnings,
upcoming events, or schedule disruptions without being prompted.
"""
import time
import threading
import psutil
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.logger import get_logger
from ai.llm import ask_llm

logger = get_logger(__name__)

# Track things we have already warned about to prevent spam
_warned_state: Dict[str, any] = {
    "battery_low": False,
    "cpu_high": False,
    "ram_high": False,
    "events_notified": set(),
}

class ProactiveAgent(threading.Thread):
    def __init__(self, check_interval_sec=300):
        super().__init__(daemon=True)
        self.check_interval_sec = check_interval_sec
        self.running = False
        
        # Load config
        from core.config import CALENDAR_SAVE_PATH
        self.calendar_path = CALENDAR_SAVE_PATH
        
    def start_agent(self):
        if not self.running:
            self.running = True
            self.start()
            logger.info("Proactive Agent started.")
            
    def stop_agent(self):
        self.running = False
        
    def run(self):
        """Main proactive loop."""
        # Initial wait to let the system boot up and the user start working
        time.sleep(30)
        
        while self.running:
            try:
                self._check_system()
                self._check_calendar()
            except Exception as e:
                logger.error(f"Proactive agent error: {e}")
                
            # Sleep in chunks to allow for clean shutdown
            for _ in range(self.check_interval_sec):
                if not self.running:
                    break
                time.sleep(1)

    def _speak_proactively(self, message: str, priority_prompt: Optional[bool] = None):
        """Speak a proactive message, optionally using the LLM for natural phrasing."""
        from voice.tts import speak
        try:
            if priority_prompt:
                # Ask LLM to rephrase dynamically
                prompt = (
                    "You are David, a proactive AI assistant. "
                    "Make this warning/notification sound natural and conversational, 1-2 sentences maximum. "
                    f"Notification: {message}"
                )
                phrased = ask_llm(prompt, temperature=0.7, num_predict=100)
                if phrased and len(phrased) > 5:
                    speak(phrased)
                    return
            # Fallback to direct speaking
            speak(message)
        except Exception as e:
            logger.error(f"Failed to speak proactively: {e}")

    def _check_system(self):
        """Check system vitals."""
        # Check battery
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                pct = battery.percent
                plugged = battery.power_plugged
                
                if pct <= 15 and not plugged and not _warned_state["battery_low"]:
                    logger.info("Proactive: Low battery detected.")
                    self._speak_proactively(
                        f"Your battery is at {pct} percent and not plugged in.",
                        priority_prompt=True
                    )
                    _warned_state["battery_low"] = True
                elif plugged or pct > 20:
                    _warned_state["battery_low"] = False

        # Check CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 95 and not _warned_state["cpu_high"]:
            logger.info("Proactive: High CPU detected.")
            self._speak_proactively(
                f"Your CPU usage is very high, at {cpu_usage} percent.",
                priority_prompt=True
            )
            _warned_state["cpu_high"] = True
        elif cpu_usage < 80:
            _warned_state["cpu_high"] = False
            
        # Check RAM
        ram_usage = psutil.virtual_memory().percent
        if ram_usage > 95 and not _warned_state["ram_high"]:
            logger.info("Proactive: High RAM detected.")
            self._speak_proactively(
                f"Your memory usage is critical, at {ram_usage} percent.",
                priority_prompt=True
            )
            _warned_state["ram_high"] = True
        elif ram_usage < 85:
            _warned_state["ram_high"] = False

    def _check_calendar(self):
        """Check upcoming events and remind proactively 10 minutes before."""
        if not os.path.exists(self.calendar_path):
            return
            
        try:
            with open(self.calendar_path, 'r', encoding='utf-8') as f:
                events = json.load(f)
                
            now = datetime.now()
            
            for event in events:
                evt_id = str(event.get("id"))
                if evt_id in _warned_state["events_notified"]:
                    continue
                    
                evt_time = datetime.fromisoformat(event["datetime"])
                
                # If event is in the next 15 minutes, notify once
                if evt_time > now and (evt_time - now).total_seconds() <= 900:  # 15 mins
                    delta_mins = int((evt_time - now).total_seconds() / 60)
                    logger.info(f"Proactive: Upcoming event - {event['title']}")
                    
                    self._speak_proactively(
                        f"You have an upcoming event: {event['title']} in {delta_mins} minutes.",
                        priority_prompt=True
                    )
                    _warned_state["events_notified"].add(evt_id)
                    
        except Exception as e:
            logger.error(f"Proactive calendar check failed: {e}")

# Global agent instance
_agent = None

def start_proactive_agent():
    global _agent
    if _agent is None:
        _agent = ProactiveAgent(check_interval_sec=120)  # Check every 2 minutes
        _agent.start_agent()

def stop_proactive_agent():
    global _agent
    if _agent:
        _agent.stop_agent()
        _agent = None
