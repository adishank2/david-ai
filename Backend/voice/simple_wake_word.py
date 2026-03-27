import sounddevice as sd
import numpy as np
# import scipy.io.wavfile as wav
# import tempfile
# import os
from core.config import SAMPLE_RATE
from core.logger import get_logger
import threading
import time
import warnings

# Suppress Whisper warnings
warnings.filterwarnings("ignore", category=UserWarning, module="whisper")
warnings.filterwarnings("ignore", category=ResourceWarning)

logger = get_logger(__name__)

class SimpleWakeWordDetector:
    """Simple wake word detector using Whisper for transcription."""
    
    def __init__(self, callback=None):
        """
        Initialize wake word detector.
        
        Args:
            callback: Function to call when wake word is detected
        """
        self.callback = callback
        self.is_listening = False
        self._thread = None
        # Accept multiple wake word variations
        self.wake_words = ["david", "hey david", "ok david", "hey davit", "hey davi"]
        self.model = None
        
    def start(self):
        """Start wake word detection in background thread."""
        if self.is_listening:
            logger.warning("Wake word detector already running")
            return
            
        try:
            # Load 'base.en' Whisper model (English optimized, better accuracy than tiny)
            import whisper
            logger.info("Loading 'base.en' Whisper model for accurate wake word detection...")
            print("⚡ Loading high-accuracy wake word detector...")
            
            try:
                self.model = whisper.load_model("base.en")
            except Exception as e:
                logger.warning(f"Failed to load 'base.en' ({e}), falling back to 'base'...")
                self.model = whisper.load_model("base")

            self.is_listening = True
            self._thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()
            
            logger.info("Wake word detection started")
            print(f"🎤 Listening for: 'david' or 'hey david'")
            print("Press Ctrl+C to exit\n")
            
        except Exception as e:
            logger.error(f"Failed to start wake word detection: {e}")
            print(f"❌ Wake word error: {e}")
            # Don't raise, just log, so the main loop doesn't crash entirely if possible
            # But main loop relies on this.
            raise
    
    def _listen_loop(self):
        """Background listening loop for wake word."""
        logger.debug("Wake word listening loop started")
        
        while self.is_listening:
            try:
                # Record 1.5s clips (Balance between speed and accuracy)
                duration = 1.5
                audio = sd.rec(
                    int(duration * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype=np.int16
                )
                sd.wait()
                
                # Convert to float32 for Whisper (No ffmpeg needed!)
                audio_float = audio.flatten().astype(np.float32) / 32768.0
                
                # Transcribe directly from memory
                result = self.model.transcribe(audio_float, language="en", fp16=False)
                text = result.get("text", "").strip().lower()
                
                # Check detection
                if text:
                    for wake_word in self.wake_words:
                        if wake_word in text:
                            print(f"\n✅ Wake word detected!")
                            logger.info(f"Wake word '{wake_word}' detected in: '{text}'")
                            if self.callback:
                                self.callback()
                            time.sleep(1.0)
                            break
                        
            except Exception as e:
                logger.error(f"Error in wake word detection loop: {e}")
                time.sleep(0.5)
    
    def stop(self):
        """Stop wake word detection."""
        logger.info("Stopping wake word detection")
        self.is_listening = False
        
        if self._thread:
            self._thread.join(timeout=2)

