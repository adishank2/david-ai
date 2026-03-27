"""Alarm and Timer plugin for David AI Assistant."""

import threading
import time
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List
from plugins.base import BasePlugin
from core.logger import get_logger

logger = get_logger(__name__)


class TimerPlugin(BasePlugin):
    """Set alarms, timers, and countdowns."""

    def __init__(self):
        super().__init__()
        self.active_timers: List[Dict] = []
        self._timer_threads: List[threading.Thread] = []

    def get_intents(self) -> List[str]:
        return ["set_timer", "set_alarm", "list_timers", "cancel_timer"]

    def get_description(self) -> str:
        return "Set timers, alarms, and countdowns with audio notifications"

    def get_prompt_examples(self) -> str:
        return """set_timer:
{
  "intent": "set_timer",
  "duration": 5,
  "unit": "minutes",
  "label": "pasta timer" (optional)
}

set_alarm:
{
  "intent": "set_alarm",
  "time": "14:30",
  "label": "meeting" (optional)
}

list_timers:
{
  "intent": "list_timers"
}

cancel_timer:
{
  "intent": "cancel_timer",
  "label": "pasta timer"
}"""

    def execute(self, intent: Dict) -> str:
        """Execute timer/alarm operation."""
        intent_type = intent.get("intent")

        try:
            if intent_type == "set_timer":
                duration = intent.get("duration", 0)
                unit = intent.get("unit", "minutes").lower()
                label = intent.get("label", f"Timer {len(self.active_timers) + 1}")

                if not duration or duration <= 0:
                    return "Please specify a valid duration."

                # Convert to seconds
                if unit in ["second", "seconds", "sec", "s"]:
                    seconds = int(duration)
                elif unit in ["minute", "minutes", "min", "m"]:
                    seconds = int(duration) * 60
                elif unit in ["hour", "hours", "hr", "h"]:
                    seconds = int(duration) * 3600
                else:
                    seconds = int(duration) * 60  # default to minutes

                timer_info = {
                    "label": label,
                    "seconds": seconds,
                    "end_time": (datetime.now() + timedelta(seconds=seconds)).isoformat(),
                    "active": True,
                }
                self.active_timers.append(timer_info)

                # Start background timer
                t = threading.Thread(
                    target=self._timer_worker,
                    args=(label, seconds),
                    daemon=True,
                )
                t.start()
                self._timer_threads.append(t)

                human_time = self._format_duration(seconds)
                logger.info(f"Timer set: {label} for {human_time}")
                return f"Timer '{label}' set for {human_time}."

            elif intent_type == "set_alarm":
                time_str = intent.get("time", "")
                label = intent.get("label", f"Alarm {len(self.active_timers) + 1}")

                if not time_str:
                    return "Please specify a time for the alarm (e.g., 14:30)."

                try:
                    today = datetime.now().strftime("%Y-%m-%d")
                    alarm_dt = datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")

                    # If time has passed today, set for tomorrow
                    if alarm_dt < datetime.now():
                        alarm_dt += timedelta(days=1)

                    seconds_until = int((alarm_dt - datetime.now()).total_seconds())

                    timer_info = {
                        "label": label,
                        "seconds": seconds_until,
                        "end_time": alarm_dt.isoformat(),
                        "active": True,
                    }
                    self.active_timers.append(timer_info)

                    t = threading.Thread(
                        target=self._timer_worker,
                        args=(label, seconds_until),
                        daemon=True,
                    )
                    t.start()
                    self._timer_threads.append(t)

                    logger.info(f"Alarm set: {label} at {alarm_dt.strftime('%I:%M %p')}")
                    return f"Alarm '{label}' set for {alarm_dt.strftime('%I:%M %p')}."

                except ValueError:
                    return "Invalid time format. Please use HH:MM (24-hour format)."

            elif intent_type == "list_timers":
                active = [t for t in self.active_timers if t["active"]]
                if not active:
                    return "No active timers or alarms."

                result = f"{len(active)} active timer(s): "
                for t in active:
                    end_dt = datetime.fromisoformat(t["end_time"])
                    remaining = max(0, int((end_dt - datetime.now()).total_seconds()))
                    result += f"{t['label']} ({self._format_duration(remaining)} remaining). "
                return result

            elif intent_type == "cancel_timer":
                label = intent.get("label", "").lower()
                if not label:
                    return "Please specify which timer to cancel."

                for t in self.active_timers:
                    if t["label"].lower() == label and t["active"]:
                        t["active"] = False
                        logger.info(f"Timer cancelled: {label}")
                        return f"Cancelled timer: {label}"

                return f"No active timer found with label: {label}"

            else:
                return "Unknown timer command."

        except Exception as e:
            logger.error(f"Timer plugin error: {e}")
            return f"Timer error: {e}"

    def _timer_worker(self, label: str, seconds: int):
        """Background worker that waits and then triggers the alarm."""
        try:
            # Sleep in 1-second increments so we can check for cancellation
            for _ in range(seconds):
                time.sleep(1)
                # Check if cancelled
                timer = next((t for t in self.active_timers if t["label"] == label), None)
                if timer and not timer["active"]:
                    return  # Cancelled

            # Timer finished — trigger notification
            timer = next((t for t in self.active_timers if t["label"] == label), None)
            if timer and not timer["active"]:
                return  # Cancelled during last second

            logger.info(f"Timer finished: {label}")

            # Play system beep notification
            self._play_notification(label)

            # Speak the notification
            try:
                from voice.tts import speak
                speak(f"Time's up! {label} is done.")
            except Exception as e:
                logger.error(f"TTS notification failed: {e}")

            # Mark as inactive
            if timer:
                timer["active"] = False

        except Exception as e:
            logger.error(f"Timer worker error: {e}")

    def _play_notification(self, label: str):
        """Play an audio notification."""
        try:
            import winsound
            # Play 3 beeps
            for _ in range(3):
                winsound.Beep(1000, 500)
                time.sleep(0.2)
        except Exception:
            # Fallback: use PowerShell to play a system sound
            try:
                subprocess.Popen(
                    ["powershell", "-Command",
                     "[System.Media.SystemSounds]::Exclamation.Play()"],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            except Exception:
                pass

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds into human readable duration."""
        if seconds < 60:
            return f"{seconds} second{'s' if seconds != 1 else ''}"
        elif seconds < 3600:
            mins = seconds // 60
            return f"{mins} minute{'s' if mins != 1 else ''}"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            result = f"{hours} hour{'s' if hours != 1 else ''}"
            if mins > 0:
                result += f" {mins} minute{'s' if mins != 1 else ''}"
            return result
