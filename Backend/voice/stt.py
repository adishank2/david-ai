import whisper
import os
import time
from core.logger import get_logger

logger = get_logger(__name__)

_model = None

def get_model():
    """Lazy-load (or return cached) Whisper model."""
    global _model
    if _model is None:
        logger.info("Loading Whisper model...")
        _model = whisper.load_model("base")  # Multilingual model (Hindi + English)
        logger.info("Whisper model ready")
    return _model

# ─────────────────────────────────────────────────────────
# Web-mode detection helpers
# ─────────────────────────────────────────────────────────
def _web_pending() -> str | None:
    """Return the next queued text command from the web UI, or None."""
    try:
        from web.server import get_pending_text
        return get_pending_text()
    except Exception:
        return None

def _web_mode() -> bool:
    """True when the web server module is loaded (running under main.py web mode)."""
    import sys
    return "web.server" in sys.modules

# ─────────────────────────────────────────────────────────
# Main listen function
# ─────────────────────────────────────────────────────────
def listen(poll_interval: float = 0.15) -> str:
    """
    Get the next user input.

    • In WEB mode  → polls the browser command queue; never touches the mic.
    • In CLI mode  → records from the microphone and transcribes with Whisper.
    """

    # ── WEB mode: poll queue until a command arrives ──
    if _web_mode():
        while True:
            text = _web_pending()
            if text:
                logger.debug(f"Web text command received: {text}")
                return text
            time.sleep(poll_interval)

    # ── CLI / mic mode ────────────────────────────────
    from voice.listener import record_voice
    wav_file = None
    text = ""
    try:
        wav_file = record_voice()
        if wav_file and os.path.exists(wav_file):
            import scipy.io.wavfile as wav_io
            import numpy as np
            rate, data = wav_io.read(wav_file)
            audio_float = data.astype(np.float32) / 32768.0
            model = get_model()
            result = model.transcribe(audio_float, fp16=False)  # Auto-detect Hindi/English
            text = result.get("text", "").strip()
        logger.debug(f"Whisper transcription: {text}")
        return text
    except Exception as e:
        logger.error(f"Speech recognition failed: {e}")
        return ""
    finally:
        if wav_file and os.path.exists(wav_file):
            try:
                os.remove(wav_file)
            except Exception:
                pass
