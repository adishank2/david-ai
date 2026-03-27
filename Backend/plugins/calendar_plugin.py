"""Calendar and reminders plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import json
import os
import uuid
from datetime import datetime, timedelta
from core.logger import get_logger
from core.config import CALENDAR_SAVE_PATH

logger = get_logger(__name__)

class CalendarPlugin(BasePlugin):
    """Manage calendar events and reminders."""
    
    def __init__(self):
        super().__init__()
        self.events = []
        self.load_events()
    
    def get_intents(self) -> List[str]:
        return ["create_event", "list_events", "delete_event", "create_reminder",
                "export_calendar", "sync_calendar"]
    
    def get_description(self) -> str:
        return "Calendar management: create events, set reminders, view schedule, export/import ICS"
    
    def get_prompt_examples(self) -> str:
        return """create_event:
{
  "intent": "create_event",
  "title": "Team Meeting",
  "date": "2026-02-15",
  "time": "14:00",
  "duration": 60 (optional, in minutes)
}

list_events:
{
  "intent": "list_events",
  "days": 7 (optional, default 7)
}

delete_event:
{
  "intent": "delete_event",
  "title": "Team Meeting"
}

create_reminder:
{
  "intent": "create_reminder",
  "title": "Call mom",
  "time": "17:00"
}

export_calendar:
{
  "intent": "export_calendar"
}

sync_calendar:
{
  "intent": "sync_calendar",
  "path": "Downloads/calendar.ics"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute calendar operation."""
        intent_type = intent.get("intent")
        
        try:
            if intent_type == "create_event":
                title = intent.get("title", "")
                date_str = intent.get("date", "")
                time_str = intent.get("time", "")
                duration = intent.get("duration", 60)
                
                if not title:
                    return "Please provide an event title."
                
                # Parse date and time
                try:
                    if date_str and time_str:
                        event_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                    elif time_str:
                        # Today at specified time
                        today = datetime.now().strftime("%Y-%m-%d")
                        event_datetime = datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")
                    else:
                        return "Please provide a time for the event."
                except ValueError:
                    return "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
                
                event = {
                    "id": len(self.events) + 1,
                    "title": title,
                    "datetime": event_datetime.isoformat(),
                    "duration": duration,
                    "created": datetime.now().isoformat()
                }
                
                self.events.append(event)
                self.save_events()
                
                logger.info(f"Created event: {title} at {event_datetime}")
                return f"Created event: {title} on {event_datetime.strftime('%B %d at %I:%M %p')}"
            
            elif intent_type == "list_events":
                days = intent.get("days", 7)
                now = datetime.now()
                future_date = now + timedelta(days=days)
                
                upcoming = []
                for event in self.events:
                    event_dt = datetime.fromisoformat(event["datetime"])
                    if now <= event_dt <= future_date:
                        upcoming.append(event)
                
                if not upcoming:
                    return f"No events in the next {days} days."
                
                # Sort by datetime
                upcoming.sort(key=lambda x: x["datetime"])
                
                result = f"Upcoming events in next {days} days: "
                for event in upcoming[:5]:
                    event_dt = datetime.fromisoformat(event["datetime"])
                    result += f"{event['title']} on {event_dt.strftime('%B %d at %I:%M %p')}. "
                
                return result
            
            elif intent_type == "delete_event":
                title = intent.get("title", "").lower()
                if not title:
                    return "Please provide an event title."
                
                original_count = len(self.events)
                self.events = [e for e in self.events if title not in e["title"].lower()]
                
                if len(self.events) < original_count:
                    self.save_events()
                    logger.info(f"Deleted event: {title}")
                    return f"Deleted event: {title}"
                else:
                    return f"Event not found: {title}"
            
            elif intent_type == "create_reminder":
                title = intent.get("title", "")
                time_str = intent.get("time", "")
                
                if not title:
                    return "Please provide a reminder title."
                
                # Parse time
                try:
                    if time_str:
                        today = datetime.now().strftime("%Y-%m-%d")
                        reminder_datetime = datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")
                        
                        # If time has passed today, set for tomorrow
                        if reminder_datetime < datetime.now():
                            reminder_datetime += timedelta(days=1)
                    else:
                        return "Please provide a time for the reminder."
                except ValueError:
                    return "Invalid time format. Use HH:MM format."
                
                reminder = {
                    "id": len(self.events) + 1,
                    "title": title,
                    "datetime": reminder_datetime.isoformat(),
                    "duration": 0,
                    "type": "reminder",
                    "created": datetime.now().isoformat()
                }
                
                self.events.append(reminder)
                self.save_events()
                
                logger.info(f"Created reminder: {title} at {reminder_datetime}")
                return f"Reminder set: {title} at {reminder_datetime.strftime('%I:%M %p')}"
            
            elif intent_type == "export_calendar":
                if not self.events:
                    return "No events to export."
                try:
                    path = self.export_to_ics()
                    return f"Calendar exported to Desktop as david_calendar.ics with {len(self.events)} events. You can import this into Google Calendar or Outlook."
                except Exception as e:
                    logger.error(f"Export failed: {e}")
                    return f"Failed to export calendar: {e}"
            
            elif intent_type == "sync_calendar":
                ics_path = intent.get("path", "")
                if not ics_path:
                    return "Please provide the path to a .ics file."
                
                # Resolve path
                userprofile = os.environ.get("USERPROFILE", "")
                if not os.path.isabs(ics_path):
                    ics_path = os.path.join(userprofile, ics_path)
                
                if not os.path.exists(ics_path):
                    return f"File not found: {ics_path}"
                
                try:
                    count = self.import_from_ics(ics_path)
                    return f"Imported {count} events from the calendar file."
                except Exception as e:
                    logger.error(f"Import failed: {e}")
                    return f"Failed to import calendar: {e}"
            
            else:
                return "Unknown calendar command."
                
        except Exception as e:
            logger.error(f"Calendar plugin error: {e}")
            return "Sorry, I couldn't perform the calendar operation."
    
    def load_events(self):
        """Load events from file."""
        try:
            if os.path.exists(CALENDAR_SAVE_PATH):
                with open(CALENDAR_SAVE_PATH, 'r') as f:
                    self.events = json.load(f)
                logger.info(f"Loaded {len(self.events)} events")
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            self.events = []
    
    def save_events(self):
        """Save events to file."""
        try:
            with open(CALENDAR_SAVE_PATH, 'w') as f:
                json.dump(self.events, f, indent=2)
            logger.info(f"Saved {len(self.events)} events")
        except Exception as e:
            logger.error(f"Error saving events: {e}")

    def export_to_ics(self) -> str:
        """Export all events to an ICS file."""
        userprofile = os.environ.get("USERPROFILE", "")
        export_path = os.path.join(userprofile, "Desktop", "david_calendar.ics")
        
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//David AI//Calendar//EN",
            "CALSCALE:GREGORIAN",
        ]
        
        for event in self.events:
            event_dt = datetime.fromisoformat(event["datetime"])
            duration = event.get("duration", 60)
            end_dt = event_dt + timedelta(minutes=duration)
            uid = event.get("id", uuid.uuid4().hex)
            
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}@david-ai",
                f"DTSTART:{event_dt.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{event['title']}",
                f"DESCRIPTION:Created by David AI",
                "END:VEVENT",
            ])
        
        lines.append("END:VCALENDAR")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write("\r\n".join(lines))
        
        logger.info(f"Exported {len(self.events)} events to {export_path}")
        return export_path

    def import_from_ics(self, ics_path: str) -> int:
        """Import events from an ICS file. Returns count of imported events."""
        imported = 0
        
        with open(ics_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple ICS parser
        events_raw = content.split("BEGIN:VEVENT")
        
        for event_block in events_raw[1:]:  # Skip calendar header
            title = ""
            dt_start = None
            duration = 60
            
            for line in event_block.split("\n"):
                line = line.strip()
                if line.startswith("SUMMARY:"):
                    title = line[8:].strip()
                elif line.startswith("DTSTART"):
                    dt_str = line.split(":")[-1].strip()
                    try:
                        dt_start = datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
                    except ValueError:
                        try:
                            dt_start = datetime.strptime(dt_str, "%Y%m%d")
                        except ValueError:
                            continue
                elif line.startswith("DTEND"):
                    dt_end_str = line.split(":")[-1].strip()
                    try:
                        dt_end = datetime.strptime(dt_end_str, "%Y%m%dT%H%M%S")
                        if dt_start:
                            duration = int((dt_end - dt_start).total_seconds() / 60)
                    except ValueError:
                        pass
            
            if title and dt_start:
                # Check for duplicates
                if not any(e["title"] == title and e["datetime"] == dt_start.isoformat() 
                          for e in self.events):
                    self.events.append({
                        "id": len(self.events) + 1,
                        "title": title,
                        "datetime": dt_start.isoformat(),
                        "duration": duration,
                        "created": datetime.now().isoformat(),
                    })
                    imported += 1
        
        if imported > 0:
            self.save_events()
        
        logger.info(f"Imported {imported} events from {ics_path}")
        return imported
