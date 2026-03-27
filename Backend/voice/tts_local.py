import subprocess
import threading
import time
from core.logger import get_logger

logger = get_logger(__name__)

# Global reference to the current TTS process
current_process = None

def stop_speaking():
    """Stop any ongoing TTS playback immediately."""
    global current_process
    if current_process:
        logger.info("Stopping TTS playback...")
        try:
            current_process.kill()
        except Exception as e:
            logger.error(f"Failed to kill TTS process: {e}")
        finally:
            current_process = None

def speak_local(text: str):
    """Speak using PowerShell (Robust fallback)."""
    # Stop previous speech before starting new one
    stop_speaking()
    
    logger.info(f"Speaking (PowerShell): {text[:50]}...")
    
    def _run():
        global current_process
        try:
            # Escape quotes to prevent syntax errors
            safe_text = text.replace('"', '').replace("'", "")
            
            # PowerShell command to use System.Speech
            ps_command = (
                f"Add-Type -AssemblyName System.Speech; "
                f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.SelectVoiceByHints('Male'); "  # Prefer male voice
                f"$s.Speak('{safe_text}')"
            )
            
            # Use Popen to allow interruption
            current_process = subprocess.Popen(
                ["powershell", "-Command", ps_command], 
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide window
            )
            current_process.wait()
            
        except Exception as e:
            logger.error(f"PowerShell TTS failed: {e}")
        finally:
            # Cleanup reference if this thread's process finished naturally
            # and wasn't replaced by a new one
            if current_process and current_process.poll() is not None:
                pass # It's done

    threading.Thread(target=_run, daemon=True).start()
