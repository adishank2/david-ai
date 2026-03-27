"""
David AI 3.0 — Task Automation Workflow Engine
Create, schedule, and execute multi-step automated workflows.
Example: "Every morning at 9AM, open Chrome, check email, play music"
"""
import os
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
from core.logger import get_logger
from core.config import BASE_DIR

logger = get_logger(__name__)

WORKFLOWS_FILE = os.path.join(BASE_DIR, "workflows.json")


# ── Built-in Action Registry ────────────────────────
ACTIONS = {
    "open_chrome": {
        "label": "Open Chrome",
        "icon": "🌐",
        "run": lambda params: subprocess.Popen(["cmd", "/c", "start", "chrome"] + ([params.get("url", "")] if params.get("url") else []), shell=False)
    },
    "open_notepad": {
        "label": "Open Notepad",
        "icon": "📝",
        "run": lambda params: subprocess.Popen(["notepad"])
    },
    "open_calculator": {
        "label": "Open Calculator",
        "icon": "🔢",
        "run": lambda params: subprocess.Popen(["calc"])
    },
    "open_vscode": {
        "label": "Open VS Code",
        "icon": "💻",
        "run": lambda params: subprocess.Popen(["cmd", "/c", "code"] + ([params.get("folder", "")] if params.get("folder") else []), shell=False)
    },
    "open_spotify": {
        "label": "Open Spotify",
        "icon": "🎵",
        "run": lambda params: subprocess.Popen(["cmd", "/c", "start", "spotify:"], shell=False)
    },
    "open_whatsapp": {
        "label": "Open WhatsApp",
        "icon": "💬",
        "run": lambda params: subprocess.Popen(["cmd", "/c", "start", "whatsapp:"], shell=False)
    },
    "open_url": {
        "label": "Open URL",
        "icon": "🔗",
        "run": lambda params: subprocess.Popen(["cmd", "/c", "start", params.get("url", "https://google.com")], shell=False)
    },
    "open_folder": {
        "label": "Open Folder",
        "icon": "📁",
        "run": lambda params: subprocess.Popen(["explorer", params.get("path", os.path.expanduser("~\\Desktop"))])
    },
    "speak": {
        "label": "David Speaks",
        "icon": "🗣️",
        "run": lambda params: _speak_action(params.get("text", ""))
    },
    "wait": {
        "label": "Wait / Delay",
        "icon": "⏳",
        "run": lambda params: time.sleep(int(params.get("seconds", 5)))
    },
    "volume_up": {
        "label": "Volume Up",
        "icon": "🔊",
        "run": lambda params: _volume_action("up")
    },
    "volume_down": {
        "label": "Volume Down",
        "icon": "🔉",
        "run": lambda params: _volume_action("down")
    },
    "mute": {
        "label": "Mute",
        "icon": "🔇",
        "run": lambda params: _volume_action("mute")
    },
    "play_music": {
        "label": "Play Music",
        "icon": "🎶",
        "run": lambda params: _play_music_action(params.get("query", ""))
    },
    "screenshot": {
        "label": "Take Screenshot",
        "icon": "📸",
        "run": lambda params: _screenshot_action()
    },
    "run_command": {
        "label": "Run Command",
        "icon": "⚡",
        "run": lambda params: subprocess.Popen(params.get("command", "echo hello"), shell=True)
    },
}


# ── Helper actions ───────────────────────────────────
def _speak_action(text):
    try:
        from voice.tts import speak
        speak(text)
    except Exception as e:
        logger.error(f"Speak action failed: {e}")

def _volume_action(direction):
    try:
        from actions.volume import volume_up, volume_down, mute
        if direction == "up": volume_up()
        elif direction == "down": volume_down()
        elif direction == "mute": mute()
    except Exception as e:
        logger.error(f"Volume action failed: {e}")

def _play_music_action(query):
    try:
        if query:
            subprocess.Popen(["cmd", "/c", f"start https://www.youtube.com/results?search_query={query}"], shell=True)
        else:
            subprocess.Popen(["cmd", "/c", "start spotify:"], shell=False)
    except Exception as e:
        logger.error(f"Play music action failed: {e}")

def _screenshot_action():
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        path = os.path.join(BASE_DIR, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        screenshot.save(path)
        logger.info(f"Screenshot saved: {path}")
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")


# ── Workflow Manager ─────────────────────────────────
class WorkflowManager:
    """Manages creation, scheduling, and execution of multi-step workflows."""
    
    def __init__(self):
        self.workflows: dict = {}
        self._lock = threading.Lock()
        self._load()
    
    def _load(self):
        if os.path.exists(WORKFLOWS_FILE):
            try:
                with open(WORKFLOWS_FILE, "r", encoding="utf-8") as f:
                    self.workflows = json.load(f)
                logger.info(f"Loaded {len(self.workflows)} workflows.")
            except Exception as e:
                logger.error(f"Failed to load workflows: {e}")
    
    def _save(self):
        try:
            with open(WORKFLOWS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.workflows, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workflows: {e}")
    
    def create_workflow(self, name: str, steps: List[Dict], schedule: Optional[Dict] = None) -> Dict:
        """
        Create a new workflow.
        
        Args:
            name: Human-readable name (e.g. "Morning Routine")
            steps: List of {action: str, params: dict, delay_after: int}
            schedule: Optional {hour: int, minute: int, days: list[str]}
        """
        wf_id = f"wf_{int(time.time())}"
        
        workflow = {
            "id": wf_id,
            "name": name,
            "steps": steps,
            "schedule": schedule,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0,
        }
        
        with self._lock:
            self.workflows[wf_id] = workflow
            self._save()
        
        logger.info(f"Workflow created: {name} ({len(steps)} steps)")
        return workflow
    
    def delete_workflow(self, wf_id: str) -> bool:
        with self._lock:
            if wf_id in self.workflows:
                self.workflows.pop(wf_id, None)
                self._save()
                return True
        return False
    
    def toggle_workflow(self, wf_id: str) -> bool:
        with self._lock:
            if wf_id in self.workflows:
                self.workflows[wf_id]["enabled"] = not self.workflows[wf_id]["enabled"]
                self._save()
                return self.workflows[wf_id]["enabled"]
        return False
    
    def execute_workflow(self, wf_id: str) -> Dict:
        """Execute all steps of a workflow sequentially."""
        wf = self.workflows.get(wf_id)
        if not wf:
            return {"success": False, "error": "Workflow not found"}
        
        logger.info(f"▶ Running workflow: {wf['name']}")
        results = []
        
        # Announce workflow start
        try:
            _speak_action(f"Starting workflow: {wf['name']}")
        except Exception:
            pass
        
        for i, step in enumerate(wf["steps"]):
            action_id = step.get("action")
            params = step.get("params", {})
            delay_after = step.get("delay_after", 2)
            
            action: Any = ACTIONS.get(action_id)
            if not action:
                results.append({"step": i+1, "action": action_id, "status": "skipped", "reason": "Unknown action"})
                continue
            
            try:
                logger.info(f"  Step {i+1}: {action['icon']} {action['label']}")
                run_fn = action.get("run")
                if callable(run_fn):
                    run_fn(params)
                results.append({"step": i+1, "action": action_id, "status": "success", "label": action["label"]})
            except Exception as e:
                logger.error(f"  Step {i+1} failed: {e}")
                results.append({"step": i+1, "action": action_id, "status": "error", "error": str(e)})
            
            # Delay between steps
            if delay_after > 0 and i < len(wf["steps"]) - 1:
                time.sleep(delay_after)
        
        # Update metadata
        with self._lock:
            self.workflows[wf_id]["last_run"] = datetime.now().isoformat()
            self.workflows[wf_id]["run_count"] = wf.get("run_count", 0) + 1
            self._save()
        
        logger.info(f"✓ Workflow complete: {wf['name']} ({len(results)} steps)")
        return {"success": True, "workflow": wf["name"], "results": results}
    
    def get_all(self) -> List[Dict]:
        return list(self.workflows.values())
    
    def get_available_actions(self) -> List[Dict]:
        """Return all registered actions for the UI."""
        return [
            {"id": k, "label": v["label"], "icon": v["icon"]}
            for k, v in ACTIONS.items()
        ]


# ── Scheduled Workflow Runner ────────────────────────
class WorkflowScheduler(threading.Thread):
    """Background thread that triggers scheduled workflows at the right time."""
    
    def __init__(self, manager: WorkflowManager):
        super().__init__(daemon=True)
        self.manager = manager
        self.running = False
        self._today_run: set = set()  # track which workflows already ran today
    
    def start_scheduler(self):
        if not self.running:
            self.running = True
            self.start()
            logger.info("Workflow Scheduler started.")
    
    def stop_scheduler(self):
        self.running = False
    
    def run(self):
        time.sleep(30)  # Initial boot delay
        
        while self.running:
            now = datetime.now()
            today_key = now.strftime("%Y-%m-%d")
            current_day = now.strftime("%A").lower()
            
            for wf_id, wf in self.manager.workflows.items():
                if not wf.get("enabled"):
                    continue
                    
                schedule = wf.get("schedule")
                if not schedule:
                    continue
                
                sched_hour = schedule.get("hour")
                sched_minute = schedule.get("minute", 0)
                sched_days = [d.lower() for d in schedule.get("days", ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])]
                
                # Check if current day matches
                if current_day not in sched_days:
                    continue
                
                # Check if it's the right time (within 1-minute window)
                if now.hour == sched_hour and now.minute == sched_minute:
                    run_key = f"{wf_id}_{today_key}_{sched_hour}_{sched_minute}"
                    if run_key not in self._today_run:
                        self._today_run.add(run_key)
                        logger.info(f"⏰ Scheduled workflow triggered: {wf['name']}")
                        threading.Thread(
                            target=self.manager.execute_workflow,
                            args=(wf_id,),
                            daemon=True
                        ).start()
            
            # Reset daily tracking at midnight
            if now.hour == 0 and now.minute == 0:
                self._today_run.clear()
            
            # Check every 30 seconds
            for _ in range(30):
                if not self.running:
                    break
                time.sleep(1)


# ── Singletons ───────────────────────────────────────
_manager = None
_scheduler = None

def get_workflow_manager() -> WorkflowManager:
    global _manager
    if _manager is None:
        _manager = WorkflowManager()
    return _manager

def start_workflow_scheduler():
    global _scheduler
    if _scheduler is None:
        mgr = get_workflow_manager()
        _scheduler = WorkflowScheduler(mgr)
        _scheduler.start_scheduler()

def stop_workflow_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.stop_scheduler()
        _scheduler = None
