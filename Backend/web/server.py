"""
David AI — FastAPI WebSocket Server
Bridges the React web UI to the David core assistant.
"""
import asyncio
import threading
import webbrowser
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from web.auth_routes import router as auth_router

# ────────────────────────────────────────────
# Connected WebSocket clients
# ────────────────────────────────────────────
connected_clients: list[WebSocket] = []
_assistant_thread: threading.Thread | None = None


async def broadcast(event: str, payload: str = ""):
    """Send a JSON message to all connected browsers."""
    msg = {"event": event, "payload": payload}
    dead = []
    for ws in connected_clients:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.append(ws)
    for d in dead:
        connected_clients.remove(d)


def sync_broadcast(event: str, payload: str = ""):
    """Thread-safe broadcast from the assistant thread (sync context)."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — fall back
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            return
    if loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast(event, payload), loop)


# ────────────────────────────────────────────
# Monkey-patch signals so core.assistant emits
# events to the web UI instead of PyQt / Qt
# ────────────────────────────────────────────
def _patch_signals():
    from types import ModuleType

    class _Sig:
        def __init__(self, name):
            self._name = name

        def emit(self, data=""):
            mapping = {
                "assistant_response":  "response",
                "user_input_received": "user_input",
                "status_changed":      "status",
                "shutdown_requested":  "shutdown",
            }
            evt = mapping.get(self._name, self._name)
            sync_broadcast(evt, str(data) if data else "")

        def connect(self, *a): pass
        def disconnect(self, *a): pass

    class _Signals:
        assistant_response  = _Sig("assistant_response")
        user_input_received = _Sig("user_input_received")
        status_changed      = _Sig("status_changed")
        shutdown_requested  = _Sig("shutdown_requested")

    mock = ModuleType("gui.signals")
    mock.signals = _Signals()
    sys.modules["gui"]         = ModuleType("gui")
    sys.modules["gui.signals"] = mock


# ────────────────────────────────────────────
# Text command queue — browser → assistant
# ────────────────────────────────────────────
_pending_text: list[str] = []


def _inject_text_command(text: str):
    """Queue a text command to be picked up by the assistant thread."""
    _pending_text.append(text)


def get_pending_text() -> str | None:
    """Called by assistant thread to retrieve the next pending text command."""
    return _pending_text.pop(0) if _pending_text else None


def _run_assistant(_unused_queue=None):
    """Run David assistant in a background thread."""
    _patch_signals()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    from core.assistant import run
    run()


# ────────────────────────────────────────────
# FastAPI app
# ────────────────────────────────────────────
WEB_DIR    = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(WEB_DIR, "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import queue as _queue
    tq = _queue.Queue()
    t = threading.Thread(target=_run_assistant, args=(tq,), daemon=True)
    t.start()
    yield


app = FastAPI(title="David AI", lifespan=lifespan)

# ── CORS — allow React dev server + mobile app ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Open for mobile app connections
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Auth router
app.include_router(auth_router, prefix="/api")

# RAG Knowledge Base Endpoints
@app.get("/api/rag/status")
async def rag_status():
    from core.indexer import get_indexer_status
    status = get_indexer_status()
    return JSONResponse(status or {"is_indexing": False, "count": 0})

@app.post("/api/rag/index")
async def rag_index():
    from core.indexer import start_indexing_agent
    indexer = start_indexing_agent()
    # Force a scan now
    threading.Thread(target=indexer.perform_scan, daemon=True).start()
    return JSONResponse({"message": "Local knowledge scan initiated."})

@app.get("/api/rag/stats")
async def rag_stats():
    from core.rag_manager import get_rag
    stats = get_rag().get_stats()
    return JSONResponse(stats)


# ────────────────────────────────────────────
# Face Recognition Auth Endpoints
# ────────────────────────────────────────────
class FaceData(BaseModel):
    email: str
    image: str   # base64 encoded webcam frame

@app.post("/api/face/register")
async def face_register(data: FaceData):
    """Register a face for biometric login."""
    from core.face_auth import register_face
    result = register_face(data.email, data.image)
    status_code = 200 if result["success"] else 400
    return JSONResponse(result, status_code=status_code)

@app.post("/api/face/verify")
async def face_verify(data: FaceData):
    """Verify face for biometric login."""
    from core.face_auth import verify_face
    result = verify_face(data.email, data.image)
    status_code = 200 if result["success"] else 401
    return JSONResponse(result, status_code=status_code)

@app.get("/api/face/registered")
async def face_list():
    """List registered faces."""
    from core.face_auth import get_registered_faces
    return JSONResponse(get_registered_faces())


# ────────────────────────────────────────────
# Emotion Detection Endpoint
# ────────────────────────────────────────────
class EmotionData(BaseModel):
    image: str   # base64 webcam frame

@app.post("/api/emotion/detect")
async def emotion_detect(data: EmotionData):
    """Detect emotion from webcam frame."""
    from core.face_auth import detect_emotion
    result = detect_emotion(data.image)
    return JSONResponse(result)


# ────────────────────────────────────────────
# Habit Tracker & Smart Suggestions
# ────────────────────────────────────────────
@app.get("/api/habits/suggestions")
async def habit_suggestions():
    """Get smart suggestions based on learned habits."""
    from core.habits import get_habit_tracker
    tracker = get_habit_tracker()
    suggestions = tracker.get_suggestions()
    return JSONResponse({"suggestions": suggestions})

@app.get("/api/habits/stats")
async def habit_stats():
    """Get habit tracking statistics."""
    from core.habits import get_habit_tracker
    tracker = get_habit_tracker()
    return JSONResponse(tracker.get_stats())

class HabitAction(BaseModel):
    action: str
    category: str = "command"

@app.post("/api/habits/record")
async def habit_record(data: HabitAction):
    """Manually record a habit action."""
    from core.habits import get_habit_tracker
    tracker = get_habit_tracker()
    tracker.record_action(data.action, data.category)
    return JSONResponse({"recorded": True})


# ────────────────────────────────────────────
# Task Automation Workflows API
# ────────────────────────────────────────────
@app.get("/api/workflows")
async def list_workflows():
    """List all workflows."""
    from core.workflows import get_workflow_manager
    mgr = get_workflow_manager()
    return JSONResponse({"workflows": mgr.get_all()})

@app.get("/api/workflows/actions")
async def list_actions():
    """List all available actions for building workflows."""
    from core.workflows import get_workflow_manager
    mgr = get_workflow_manager()
    return JSONResponse({"actions": mgr.get_available_actions()})

class WorkflowCreate(BaseModel):
    name: str
    steps: list   # [{action: str, params: dict, delay_after: int}]
    schedule: dict = None   # {hour: int, minute: int, days: [str]}

@app.post("/api/workflows")
async def create_workflow(data: WorkflowCreate):
    """Create a new automation workflow."""
    from core.workflows import get_workflow_manager
    mgr = get_workflow_manager()
    wf = mgr.create_workflow(data.name, data.steps, data.schedule)
    return JSONResponse(wf)

@app.delete("/api/workflows/{wf_id}")
async def delete_workflow(wf_id: str):
    """Delete a workflow."""
    from core.workflows import get_workflow_manager
    mgr = get_workflow_manager()
    deleted = mgr.delete_workflow(wf_id)
    return JSONResponse({"deleted": deleted})

@app.post("/api/workflows/{wf_id}/toggle")
async def toggle_workflow(wf_id: str):
    """Enable/disable a workflow."""
    from core.workflows import get_workflow_manager
    mgr = get_workflow_manager()
    enabled = mgr.toggle_workflow(wf_id)
    return JSONResponse({"enabled": enabled})

@app.post("/api/workflows/{wf_id}/run")
async def run_workflow(wf_id: str):
    """Manually execute a workflow."""
    from core.workflows import get_workflow_manager
    mgr = get_workflow_manager()
    # Run in background thread to not block the API
    result_holder = {"result": None}
    def _run():
        result_holder["result"] = mgr.execute_workflow(wf_id)
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return JSONResponse({"message": f"Workflow execution started.", "wf_id": wf_id})


# Shared Pydantic models
class TextCommand(BaseModel):
    text: str

# ────────────────────────────────────────────
# Mobile Control API (Feature 5)
# ────────────────────────────────────────────
@app.get("/api/mobile/ping")
async def mobile_ping():
    """Mobile app connectivity check."""
    import psutil
    battery = psutil.sensors_battery()
    return JSONResponse({
        "status": "online",
        "device": os.environ.get("COMPUTERNAME", "David-PC"),
        "battery": battery.percent if battery else None,
        "plugged_in": battery.power_plugged if battery else None,
        "cpu_percent": psutil.cpu_percent(interval=0),
        "ram_percent": psutil.virtual_memory().percent,
        "connected_clients": len(connected_clients),
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

@app.post("/api/mobile/command")
async def mobile_command(cmd: TextCommand):
    """Execute a command from the mobile app."""
    text = cmd.text.strip()
    if not text:
        return JSONResponse({"error": "Empty command"}, status_code=400)
    try:
        from voice.tts import stop_speaking
        stop_speaking()
    except Exception:
        pass
    _inject_text_command(text)
    return JSONResponse({"queued": text, "source": "mobile"})

@app.post("/api/mobile/speak")
async def mobile_speak(cmd: TextCommand):
    """Make David speak text from the mobile app."""
    text = cmd.text.strip()
    if not text:
        return JSONResponse({"error": "Empty text"}, status_code=400)
    try:
        from voice.tts import speak as tts_speak
        threading.Thread(target=tts_speak, args=(text,), daemon=True).start()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"speaking": text})

@app.get("/api/mobile/system")
async def mobile_system():
    """Full system status for mobile dashboard."""
    import psutil
    from datetime import datetime
    
    # Disk usage
    disk = psutil.disk_usage('/')
    
    # Network
    net = psutil.net_io_counters()
    
    return JSONResponse({
        "cpu": psutil.cpu_percent(interval=0),
        "ram": psutil.virtual_memory().percent,
        "disk_used_gb": round(disk.used / (1024**3), 1),
        "disk_total_gb": round(disk.total / (1024**3), 1),
        "net_sent_mb": round(net.bytes_sent / (1024**2), 1),
        "net_recv_mb": round(net.bytes_recv / (1024**2), 1),
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else None,
        "uptime_hours": round((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600, 1),
        "timestamp": datetime.now().isoformat()
    })


# Static files (production build served from here)
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ────────────────────────────────────────────
# HTTP Endpoints
# ────────────────────────────────────────────
@app.get("/")
async def index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "David AI backend is running. Connect your React frontend at http://localhost:3000"})


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "clients": len(connected_clients)})


@app.get("/api/status")
async def api_status():
    """Frontend polls this to check backend liveness."""
    return JSONResponse({
        "status": "online",
        "connected_clients": len(connected_clients),
        "version": "2.0.0"
    })




@app.post("/command")
async def post_command(cmd: TextCommand):
    """Accept a text command from the browser."""
    text = cmd.text.strip()
    if not text:
        return JSONResponse({"error": "Empty command"}, status_code=400)
    # Stop David from speaking before queuing the new command
    try:
        from voice.tts import stop_speaking
        stop_speaking()
    except Exception:
        pass
    
    # Record habit
    try:
        from core.habits import get_habit_tracker
        get_habit_tracker().record_action(text, "command")
    except Exception:
        pass
    
    _inject_text_command(text)
    return JSONResponse({"queued": text})


@app.post("/stop")
async def stop_david():
    """Immediately stop David from speaking."""
    try:
        from voice.tts import stop_speaking
        stop_speaking()
    except Exception:
        pass
    # Clear any pending commands too
    _pending_text.clear()
    return JSONResponse({"stopped": True})


# ────────────────────────────────────────────
# WebSocket endpoint
# ────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    await ws.send_json({"event": "status", "payload": "Connected"})
    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "text_command":
                text = data.get("text", "").strip()
                if text:
                    _inject_text_command(text)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if ws in connected_clients:
            connected_clients.remove(ws)


# ────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────
def run_web(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True):
    import time

    if open_browser:
        def _open():
            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")
        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host=host, port=port, log_level="warning")

