import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
from core.config import SAMPLE_RATE, RECORDING_DURATION, MICROPHONE_INDEX
from core.logger import get_logger

logger = get_logger(__name__)

def record_voice():
    """
    Record audio from the microphone.
    
    Returns:
        str: Path to the recorded WAV file
        
    Raises:
        Exception: If recording fails
    """
    try:
        logger.debug(f"Recording for {RECORDING_DURATION} seconds...")
        print(f"🎤 Listening... (speak now for {RECORDING_DURATION} seconds)")
        
        # Select device if configured
        device_index = MICROPHONE_INDEX if MICROPHONE_INDEX >= 0 else None
        if device_index is not None:
             logger.debug(f"Using microphone index: {device_index}")

        audio = sd.rec(
            int(RECORDING_DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype=np.int16,
            device=device_index
        )
        sd.wait()
        
        # Check if audio was captured
        max_amplitude = np.max(np.abs(audio))
        logger.debug(f"Max audio amplitude: {max_amplitude}")
        
        if max_amplitude < 100:  # Very quiet or silent
            logger.warning("Audio level very low - microphone might not be working")
            print("⚠️  Warning: Very quiet audio detected. Speak louder!")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav.write(temp_file.name, SAMPLE_RATE, audio)
        logger.debug(f"Audio recorded to {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Failed to record audio: {e}")
        raise Exception(f"Microphone error: {e}")

