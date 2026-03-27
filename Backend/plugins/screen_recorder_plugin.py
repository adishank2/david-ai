"""Screen recording plugin for David AI Assistant."""

import os
import threading
import time
from datetime import datetime
from typing import Dict, List
from plugins.base import BasePlugin
from core.logger import get_logger
from core.config import SCREENSHOT_SAVE_DIR

logger = get_logger(__name__)

# Recording state
_recording = False
_record_thread = None


class ScreenRecorderPlugin(BasePlugin):
    """Record the screen to a video file."""

    def get_intents(self) -> List[str]:
        return ["start_recording", "stop_recording"]

    def get_description(self) -> str:
        return "Screen recording: start and stop video capture of the screen"

    def get_prompt_examples(self) -> str:
        return """start_recording:
{
  "intent": "start_recording",
  "duration": 30 (optional, max seconds, default 60)
}

stop_recording:
{
  "intent": "stop_recording"
}"""

    def execute(self, intent: Dict) -> str:
        global _recording, _record_thread
        intent_type = intent.get("intent")

        try:
            if intent_type == "start_recording":
                if _recording:
                    return "Already recording! Say 'stop recording' to finish."

                duration = intent.get("duration", 60)
                duration = min(int(duration), 300)  # Max 5 minutes

                # Create output path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_dir = os.path.join(SCREENSHOT_SAVE_DIR, "Recordings")
                os.makedirs(save_dir, exist_ok=True)
                output_path = os.path.join(save_dir, f"recording_{timestamp}.avi")

                _recording = True
                _record_thread = threading.Thread(
                    target=self._record_worker,
                    args=(output_path, duration),
                    daemon=True,
                )
                _record_thread.start()

                logger.info(f"Screen recording started: {output_path} (max {duration}s)")
                return f"Recording started! Max duration: {duration} seconds. Say 'stop recording' to finish."

            elif intent_type == "stop_recording":
                if not _recording:
                    return "No recording is currently active."

                _recording = False
                logger.info("Screen recording stop requested")
                return "Recording stopped! Saving video file..."

            else:
                return "Unknown recording command."

        except Exception as e:
            logger.error(f"Screen recorder error: {e}")
            _recording = False
            return f"Recording error: {e}"

    @staticmethod
    def _record_worker(output_path: str, max_duration: int):
        """Background worker that captures screen frames to a video file."""
        global _recording

        try:
            import cv2
            import numpy as np
            from PIL import ImageGrab

            # Get screen size from first capture
            screen = ImageGrab.grab()
            width, height = screen.size

            # Video writer setup
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            fps = 10  # 10 FPS is good enough for screen recording
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            logger.info(f"Recording at {width}x{height} @ {fps} FPS")

            start_time = time.time()

            while _recording and (time.time() - start_time) < max_duration:
                frame_start = time.time()

                # Capture screen
                screen = ImageGrab.grab()
                frame = np.array(screen)

                # Convert RGB (PIL) to BGR (OpenCV)
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)

                # Maintain target FPS
                elapsed = time.time() - frame_start
                sleep_time = max(0, (1.0 / fps) - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            out.release()
            _recording = False

            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            duration = time.time() - start_time
            logger.info(f"Recording saved: {output_path} ({file_size_mb:.1f} MB, {duration:.0f}s)")

            # Notify user via TTS
            try:
                from voice.tts import speak
                speak(f"Recording saved. {duration:.0f} seconds, {file_size_mb:.1f} megabytes.")
            except Exception:
                pass

            # Open the file
            try:
                os.startfile(output_path)
            except Exception:
                pass

        except ImportError:
            _recording = False
            logger.error("Screen recording requires opencv-python. Install with: pip install opencv-python")
        except Exception as e:
            _recording = False
            logger.error(f"Recording worker error: {e}")
