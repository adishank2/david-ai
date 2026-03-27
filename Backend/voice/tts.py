import asyncio
import edge_tts
import subprocess
import uuid
import os
from core.config import TTS_VOICE, TTS_RATE, TTS_ENGINE, TOOLS_DIR
from core.logger import get_logger
from voice.tts_local import speak_local, stop_speaking as stop_local
import re

logger = get_logger(__name__)

# Hindi voice for when David responds in Hindi
HINDI_VOICE = "hi-IN-MadhurNeural"

# Use bundled ffplay from tools directory, fall back to system ffplay
_FFPLAY_PATH = os.path.join(TOOLS_DIR, "ffplay.exe")
if os.path.isfile(_FFPLAY_PATH):
    _FFPLAY = _FFPLAY_PATH
else:
    _FFPLAY = "ffplay"
    logger.debug(f"Bundled ffplay not found at {_FFPLAY_PATH}, using system 'ffplay'")

# Track cloud process
cloud_process = None


def stop_speaking():
    """Stop all TTS engines."""
    global cloud_process
    stop_local()
    if cloud_process:
        try:
            cloud_process.kill()
        except Exception:
            pass
        cloud_process = None


async def _speak_cloud(text: str):
    """Async Cloud TTS implementation (EdgeTTS → ffplay)."""
    global cloud_process
    filename = os.path.join(os.environ.get("TEMP", "."), f"david_tts_{uuid.uuid4()}.mp3")

    try:
        # Auto-detect Hindi vs English and pick the right voice
        voice = _detect_voice(text)
        communicate = edge_tts.Communicate(text, voice, rate=TTS_RATE)
        await communicate.save(filename)

        stop_speaking()

        cloud_process = subprocess.Popen(
            [_FFPLAY, "-nodisp", "-autoexit", "-loglevel", "quiet", filename],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        cloud_process.wait()
    except Exception as e:
        logger.error(f"Cloud TTS playback failed: {e}")
        raise
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass


def speak(text: str):
    """Speak text using the configured engine (cloud EdgeTTS or local pyttsx3)."""
    if not text or not text.strip():
        return
    try:
        if TTS_ENGINE == "local":
            speak_local(text)
        else:
            try:
                logger.debug(f"Speaking (Cloud): {text[:60]}")
                asyncio.run(_speak_cloud(text))
            except Exception as e:
                logger.warning(f"Cloud TTS failed, falling back to local: {e}")
                speak_local(text)
    except Exception as e:
        logger.error(f"TTS failed entirely: {e}")
        print(f"[TTS] {text}")

def _detect_voice(text: str) -> str:
    """Detect if text contains Hindi (Devanagari) and return the appropriate voice."""
    # Check for Devanagari Unicode characters (Hindi script)
    if re.search(r'[\u0900-\u097F]', text):
        logger.debug(f"Hindi detected, using voice: {HINDI_VOICE}")
        return HINDI_VOICE
    logger.debug(f"English detected, using voice: {TTS_VOICE}")
    return TTS_VOICE
