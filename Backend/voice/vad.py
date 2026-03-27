"""
Simplified Voice Activity Detection using energy-based detection.
Fallback implementation when webrtcvad is not available.
"""

import sounddevice as sd
import numpy as np
# import scipy.io.wavfile as wav
import tempfile
import os
from core.config import SAMPLE_RATE, SILENCE_DURATION
from core.logger import get_logger

logger = get_logger(__name__)

class VoiceActivityDetector:
    """Simple energy-based voice activity detector (fallback when webrtcvad unavailable)."""
    
    def __init__(self, sample_rate=SAMPLE_RATE, aggressiveness=3):
        """
        Initialize simple VAD.
        
        Args:
            sample_rate: Audio sample rate
            aggressiveness: Not used in simple implementation
        """
        self.sample_rate = sample_rate
        self.frame_duration = 30  # ms
        self.frame_size = int(sample_rate * self.frame_duration / 1000)
        self.energy_threshold = 500  # Adjust based on testing
        
    def record_until_silence(self, silence_duration=SILENCE_DURATION, max_duration=30):
        """
        Record audio until silence is detected using energy-based detection.
        
        Args:
            silence_duration: Seconds of silence before stopping
            max_duration: Maximum recording duration in seconds
            
        Returns:
            numpy array: Recorded audio data
        """
        try:
            logger.debug("Recording with simple VAD...")
            print("🎤 Listening... (speak naturally)")
            
            frames = []
            silence_frames = 0
            silence_threshold = int(silence_duration * 1000 / self.frame_duration)
            max_frames = int(max_duration * 1000 / self.frame_duration)
            
            voiced_frames = 0
            
            stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16,
                blocksize=self.frame_size
            )
            
            with stream:
                for i in range(max_frames):
                    frame, overflowed = stream.read(self.frame_size)
                    
                    if overflowed:
                        logger.warning("Audio buffer overflow")
                    
                    frames.append(frame)
                    
                    # Calculate energy (simple voice detection)
                    energy = np.abs(frame).mean()
                    is_speech = energy > self.energy_threshold
                    
                    if is_speech:
                        silence_frames = 0
                        voiced_frames += 1
                    else:
                        silence_frames += 1
                    
                    # Stop if we've detected enough silence after speech
                    if voiced_frames > 5 and silence_frames >= silence_threshold:
                        logger.debug(f"Silence detected after {voiced_frames} voiced frames")
                        break
            
            # Concatenate all frames
            audio_data = np.concatenate(frames, axis=0)
            logger.debug(f"Recorded {len(frames)} frames ({len(frames) * self.frame_duration / 1000:.1f}s)")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"VAD recording error: {e}")
            return np.array([], dtype=np.int16)
    
    def is_speech_present(self, audio_data):
        """
        Check if audio data contains speech using energy detection.
        
        Args:
            audio_data: Raw audio numpy array
            
        Returns:
            bool: True if speech detected
        """
        try:
            # Calculate average energy
            energy = np.abs(audio_data).mean()
            return energy > self.energy_threshold
            
        except Exception as e:
            logger.error(f"Speech detection error: {e}")
            return False
