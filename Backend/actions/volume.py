import subprocess
from core.config import NIRCMD_PATH
from core.logger import get_logger

logger = get_logger(__name__)

def volume_up():
    """Increase system volume."""
    try:
        subprocess.Popen([NIRCMD_PATH, "changesysvolume", "5000"])
    except Exception as e:
        logger.error(f"Volume up failed: {e}")

def volume_down():
    """Decrease system volume."""
    try:
        subprocess.Popen([NIRCMD_PATH, "changesysvolume", "-5000"])
    except Exception as e:
        logger.error(f"Volume down failed: {e}")

def mute():
    """Mute system volume."""
    try:
        subprocess.Popen([NIRCMD_PATH, "mutesysvolume", "1"])
    except Exception as e:
        logger.error(f"Mute failed: {e}")

def unmute():
    """Unmute system volume."""
    try:
        subprocess.Popen([NIRCMD_PATH, "mutesysvolume", "0"])
    except Exception as e:
        logger.error(f"Unmute failed: {e}")

