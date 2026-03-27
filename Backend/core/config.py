import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ── Ollama ───────────────────────────────────────────────
OLLAMA_URL   = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME   = os.getenv("OLLAMA_MODEL", "llama3.2")
VISION_MODEL = os.getenv("VISION_MODEL", "llava")

# ── Security ─────────────────────────────────────────────
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"

# ── Audio ─────────────────────────────────────────────────
SAMPLE_RATE        = int(os.getenv("SAMPLE_RATE", "16000"))
RECORDING_DURATION = int(os.getenv("RECORDING_DURATION", "5"))
MICROPHONE_INDEX   = int(os.getenv("MICROPHONE_INDEX", "-1"))

# ── Text-to-Speech ───────────────────────────────────────
TTS_ENGINE  = os.getenv("TTS_ENGINE", "cloud")   # 'cloud' (EdgeTTS) or 'local' (pyttsx3)
TTS_VOICE   = os.getenv("TTS_VOICE", "en-IN-PrabhatNeural")  # Natural conversational male Indian accent
TTS_RATE    = os.getenv("TTS_RATE", "+0%")        # Default human speed

# ── Wake Word ─────────────────────────────────────────────
WAKE_WORD_ENABLED      = os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
WAKE_WORD              = os.getenv("WAKE_WORD", "hey david").lower()
WAKE_WORD_SENSITIVITY  = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
PORCUPINE_ACCESS_KEY   = os.getenv("PORCUPINE_ACCESS_KEY", "")

# ── Continuous listening ──────────────────────────────────
CONTINUOUS_MODE    = os.getenv("CONTINUOUS_MODE", "true").lower() == "true"
VAD_AGGRESSIVENESS = int(os.getenv("VAD_AGGRESSIVENESS", "3"))
SILENCE_DURATION   = float(os.getenv("SILENCE_DURATION", "1.5"))

# ── Context & memory ─────────────────────────────────────
CONTEXT_ENABLED      = os.getenv("CONTEXT_ENABLED", "true").lower() == "true"
CONTEXT_HISTORY_SIZE = int(os.getenv("CONTEXT_HISTORY_SIZE", "10"))

# ── Web search ────────────────────────────────────────────
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"

# ── Plugins ───────────────────────────────────────────────
PLUGINS_ENABLED = os.getenv("PLUGINS_ENABLED", "true").lower() == "true"
PLUGINS_DIR     = os.getenv("PLUGINS_DIR", "plugins")

# ── Email — set via .env ONLY, never hardcode ─────────────
EMAIL_ENABLED     = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT   = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_ADDRESS     = os.getenv("EMAIL_ADDRESS", "")       # set in .env
EMAIL_PASSWORD    = os.getenv("EMAIL_PASSWORD", "")      # use Gmail App Password
EMAIL_USE_TLS     = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"

# ── Spotify — set via .env ONLY, never hardcode ───────────
SPOTIFY_ENABLED      = os.getenv("SPOTIFY_ENABLED", "false").lower() == "true"
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")      # set in .env
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")  # set in .env
SPOTIFY_REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
SPOTIFY_DEVICE_ID     = os.getenv("SPOTIFY_DEVICE_ID", "")

# ── Calendar ──────────────────────────────────────────────
CALENDAR_ENABLED                  = os.getenv("CALENDAR_ENABLED", "true").lower() == "true"
CALENDAR_REMINDER_CHECK_INTERVAL  = int(os.getenv("CALENDAR_REMINDER_CHECK_INTERVAL", "60"))

# ── Browser automation ────────────────────────────────────
BROWSER_ENABLED  = os.getenv("BROWSER_ENABLED", "true").lower() == "true"
BROWSER_DEFAULT  = os.getenv("BROWSER_DEFAULT", "chrome")
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

# ── System monitor ────────────────────────────────────────
SYSTEM_MONITOR_ENABLED       = os.getenv("SYSTEM_MONITOR_ENABLED", "true").lower() == "true"
SYSTEM_MONITOR_CPU_THRESHOLD = int(os.getenv("SYSTEM_MONITOR_CPU_THRESHOLD", "80"))
SYSTEM_MONITOR_RAM_THRESHOLD = int(os.getenv("SYSTEM_MONITOR_RAM_THRESHOLD", "80"))

# ── Screenshot ────────────────────────────────────────────
SCREENSHOT_ENABLED   = os.getenv("SCREENSHOT_ENABLED", "true").lower() == "true"
SCREENSHOT_SAVE_DIR  = os.getenv(
    "SCREENSHOT_SAVE_DIR",
    os.path.join(os.environ.get("USERPROFILE", ""), "Pictures", "David_Screenshots")
)
SCREENSHOT_OCR_ENABLED = os.getenv("SCREENSHOT_OCR_ENABLED", "false").lower() == "true"

# ── Clipboard ─────────────────────────────────────────────
CLIPBOARD_ENABLED      = os.getenv("CLIPBOARD_ENABLED", "true").lower() == "true"
CLIPBOARD_HISTORY_SIZE = int(os.getenv("CLIPBOARD_HISTORY_SIZE", "10"))

# ── Window control ────────────────────────────────────────
WINDOW_CONTROL_ENABLED = os.getenv("WINDOW_CONTROL_ENABLED", "true").lower() == "true"

# ── File operations ───────────────────────────────────────
FILE_OPS_ENABLED      = os.getenv("FILE_OPS_ENABLED", "true").lower() == "true"
FILE_OPS_ALLOWED_DIRS = os.getenv("FILE_OPS_ALLOWED_DIRS", "Desktop,Downloads,Documents,Pictures").split(",")
FILE_OPS_MAX_SIZE_MB  = int(os.getenv("FILE_OPS_MAX_SIZE_MB", "100"))
FILE_OPS_CONFIRM_DELETE = os.getenv("FILE_OPS_CONFIRM_DELETE", "true").lower() == "true"

# ── Paths ─────────────────────────────────────────────────
def get_app_paths():
    if getattr(sys, 'frozen', False):
        BUNDLED_DIR = sys._MEIPASS
        ROOT_DIR    = os.path.dirname(sys.executable)
    else:
        ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        BUNDLED_DIR = ROOT_DIR
    return ROOT_DIR, BUNDLED_DIR

ROOT_DIR, BUNDLED_DIR = get_app_paths()
BASE_DIR          = ROOT_DIR
TOOLS_DIR         = os.path.join(BUNDLED_DIR, "tools")
NIRCMD_PATH       = os.path.join(TOOLS_DIR, "nircmd.exe")
CONTEXT_SAVE_PATH = os.path.join(ROOT_DIR, "context.json")
CALENDAR_SAVE_PATH = os.path.join(ROOT_DIR, "calendar.json")


def validate_config():
    """Validate configuration — returns list of blocking errors."""
    errors = []

    if not os.path.exists(NIRCMD_PATH):
        # Warning only — volume control will be unavailable, not a crash
        import warnings
        warnings.warn(f"nircmd.exe not found at {NIRCMD_PATH} — volume control unavailable")

    if SAMPLE_RATE not in [8000, 16000, 22050, 44100, 48000]:
        errors.append(f"Invalid SAMPLE_RATE: {SAMPLE_RATE}")

    if VAD_AGGRESSIVENESS not in [0, 1, 2, 3]:
        errors.append(f"Invalid VAD_AGGRESSIVENESS: {VAD_AGGRESSIVENESS} (must be 0-3)")

    if WAKE_WORD_ENABLED and not PORCUPINE_ACCESS_KEY:
        import warnings
        warnings.warn("Wake word enabled but no PORCUPINE_ACCESS_KEY set. Get one free at picovoice.ai")

    return errors
