"""
David AI Assistant - Core Assistant Loop
"""
import traceback
import atexit
import os

from ai.llm import ask_llm
from ai.prompts import SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
from actions.validator import validate_intent
from actions.executor import execute
from voice.stt import listen
from voice.tts import speak as original_speak, stop_speaking
from voice.vad import VoiceActivityDetector
from voice.simple_wake_word import SimpleWakeWordDetector
from core.logger import get_logger
from core.context import ConversationContext
from core.memory import MemoryManager
from core.config import (
    WAKE_WORD_ENABLED, CONTINUOUS_MODE, CONTEXT_ENABLED,
    WEB_SEARCH_ENABLED, PLUGINS_ENABLED, CONTEXT_SAVE_PATH
)
from tools.web_search import WebSearchTool
from plugins.manager import PluginManager

# GUI Support — catch all exceptions (DLL load failures are not plain ImportError)
try:
    from gui.signals import signals
except Exception:
    signals = None

logger = get_logger(__name__)
pending_action = None

# Initialize advanced features
context = ConversationContext() if CONTEXT_ENABLED else None
web_search = WebSearchTool() if WEB_SEARCH_ENABLED else None
plugin_manager = PluginManager() if PLUGINS_ENABLED else None
wake_word_detector = None
vad = VoiceActivityDetector() if CONTINUOUS_MODE else None
memory_manager = MemoryManager()


def speak(text: str):
    """Speak text and emit GUI events if connected."""
    if signals:
        signals.assistant_response.emit(text)
        signals.status_changed.emit("Speaking")
    original_speak(text)
    if signals:
        signals.status_changed.emit("Idle")


def on_wake_word_detected():
    """Callback when wake word is detected."""
    logger.info("Wake word detected - activating assistant")
    stop_speaking()
    try:
        import winsound
        winsound.Beep(800, 200)
    except Exception:
        print('\a')
    process_single_command()


def process_single_command():
    """Process a single voice command."""
    global pending_action

    if signals:
        signals.status_changed.emit("Listening")
        signals.assistant_response.emit("")

    try:
        # ── Get user input ─────────────────────────────
        # In web mode always poll the browser command queue — never touch the mic.
        from voice.stt import _web_mode
        if _web_mode():
            user_input = listen()   # blocks until a text command arrives from the browser
        elif CONTINUOUS_MODE and vad:
            import tempfile
            import numpy as np
            import whisper

            audio_data = vad.record_until_silence()
            if audio_data is None or len(audio_data) < 1000:
                return

            audio_float = audio_data.flatten().astype(np.float32) / 32768.0
            from voice.stt import get_model
            model = get_model()
            result = model.transcribe(audio_float, language="en", fp16=False)
            user_input = result.get("text", "").strip()
        else:
            user_input = listen()

        if not user_input:
            return

        # Sanitize input
        from core.security import sanitize
        user_input = sanitize(user_input)
        text = user_input.lower()
        logger.info(f"User input: {text}")

        if signals:
            signals.user_input_received.emit(user_input)
            signals.status_changed.emit("Processing")

        # ── Vision override ───────────────────────────
        vision_triggers = ["on my screen", "analyze screen", "read the screen",
                           "read this error", "look at my screen"]
        if any(p in text for p in vision_triggers):
            logger.info("Vision override triggered")
            intent = {"intent": "analyze_screen", "query": user_input}
            if PLUGINS_ENABLED and plugin_manager:
                speak("Analyzing screen...")
                plugin_result = plugin_manager.execute_plugin(intent)
                if plugin_result:
                    speak(plugin_result)
                    if CONTEXT_ENABLED and context:
                        context.add_exchange(user_input, plugin_result, intent)
                    return

        # ── Shutdown detection ────────────────────────
        if any(word in text for word in ["shutdown", "shut down", "power off"]):
            pending_action = {"intent": "shutdown_request"}
            speak("Do you want me to shut down now?")
            logger.warning("Shutdown request detected, awaiting confirmation")
            return

        # ── Pending action confirmation ───────────────
        if pending_action:
            if any(word in text for word in ["yes", "confirm", "do it", "yeah", "yep"]):
                logger.info(f"Executing pending action: {pending_action}")
                result = execute(pending_action)
                speak(result)
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, result, pending_action)
            else:
                speak("Cancelled.")
                logger.info("Pending action cancelled")
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, "Cancelled.", None)
            pending_action = None
            return

        # ── Volume control (priority) ─────────────────
        if "volume" in text or "sound" in text:
            if any(p in text for p in ["down", "lower", "reduce", "quieter", "decrease"]):
                result = execute({"intent": "volume_down"})
                speak(result)
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, result, {"intent": "volume_down"})
                return
            if any(p in text for p in ["up", "increase", "raise", "louder", "higher"]):
                result = execute({"intent": "volume_up"})
                speak(result)
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, result, {"intent": "volume_up"})
                return
            if "mute" in text and "unmute" not in text:
                result = execute({"intent": "mute"})
                speak(result)
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, result, {"intent": "mute"})
                return
            if "unmute" in text:
                result = execute({"intent": "unmute"})
                speak(result)
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, result, {"intent": "unmute"})
                return
            speak("Please say volume up, volume down, mute, or unmute.")
            return

        # ── Plugin + intent execution (priority) ─────
        if PLUGINS_ENABLED and plugin_manager:
            from datetime import datetime

            ctx_prompt = context.get_context_prompt() + "\n" if CONTEXT_ENABLED and context else ""
            prompt = ctx_prompt + user_input

            plugin_prompts = plugin_manager.get_plugin_prompts()
            full_system = SYSTEM_PROMPT

            # Memory injection
            if memory_manager:
                relevant = memory_manager.search_memory(user_input)
                if relevant:
                    full_system += "\n\nRELEVANT MEMORIES:\n" + "\n".join(f"- {m}" for m in relevant)
                memory_manager.extract_and_store_fact(user_input)

            full_system += f"\n\nCurrent date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            if plugin_prompts:
                full_system += "\n" + plugin_prompts + "\n\nUser request:\n"

            logger.debug(f"Prompt length: {len(full_system + prompt)} chars")

            intent_text = ask_llm(prompt, system=full_system, temperature=0.0, num_predict=150)
            logger.debug(f"LLM raw response: {intent_text[:200]}")

            intent = validate_intent(intent_text)

            if intent:
                plugin_result = plugin_manager.execute_plugin(intent)
                if plugin_result:
                    logger.info(f"Plugin executed: {intent}")
                    speak(plugin_result)
                    if CONTEXT_ENABLED and context:
                        context.add_exchange(user_input, plugin_result, intent)
                    return

                result = execute(intent)
                speak(result)
                if CONTEXT_ENABLED and context:
                    context.add_exchange(user_input, result, intent)
                return

        # ── Web search ────────────────────────────────
        if WEB_SEARCH_ENABLED and web_search and web_search.is_search_query(text):
            logger.info("Web search query detected")
            query = web_search.extract_search_query(text)
            response = web_search.search_and_summarize(query)
            speak(response)
            if CONTEXT_ENABLED and context:
                context.add_exchange(user_input, response, {"intent": "web_search", "query": query})
            return

        # ── Conversational fallback ───────────────────
        try:
            # Check if user is correcting David
            if memory_manager and CONTEXT_ENABLED and context:
                last_response = context.get_last_response()
                if last_response:
                    was_correction = memory_manager.detect_and_store_correction(
                        user_input, last_response
                    )
                    if was_correction:
                        logger.info("Correction detected and stored in memory")

            ctx_prompt = context.get_context_prompt() + "\n" if CONTEXT_ENABLED and context else ""
            prompt = ctx_prompt + user_input
            response = ask_llm(prompt, system=CHAT_SYSTEM_PROMPT, temperature=0.7, num_predict=350)
            speak(response)
            if CONTEXT_ENABLED and context:
                context.add_exchange(user_input, response, None)
        except Exception as e:
            logger.error(f"Chat response failed: {e}")
            speak("I'm having trouble processing that request.")

    except Exception as e:
        logger.error(f"Error processing command: {e}\n{traceback.format_exc()}")
        speak("Sorry, I encountered an error.")


def cleanup():
    """Cleanup resources on exit."""
    logger.info("Cleaning up resources...")
    try:
        from core.proactive import stop_proactive_agent
        stop_proactive_agent()
    except Exception as e:
        logger.error(f"Proactive agent stop error: {e}")

    if wake_word_detector:
        wake_word_detector.stop()
    if CONTEXT_ENABLED and context:
        context.save_to_file(CONTEXT_SAVE_PATH)
    if PLUGINS_ENABLED and plugin_manager:
        plugin_manager.unload_all_plugins()


def run():
    """Main assistant loop."""
    global wake_word_detector

    atexit.register(cleanup)

    try:
        if signals:
            signals.status_changed.emit("Initializing...")

        if PLUGINS_ENABLED and plugin_manager:
            logger.info("Loading plugins...")
            if signals:
                signals.status_changed.emit("Loading plugins...")
            plugin_manager.load_all_plugins()

        if CONTEXT_ENABLED and context:
            if os.path.exists(CONTEXT_SAVE_PATH):
                context.load_from_file(CONTEXT_SAVE_PATH)

        if signals:
            signals.status_changed.emit("Loading AI model...")
        logger.info("Pre-loading Whisper model...")
        from voice.stt import get_model
        get_model()
        logger.info("Whisper model ready")

        # Start background proactive agent
        try:
            from core.proactive import start_proactive_agent
            start_proactive_agent()
        except Exception as e:
            logger.error(f"Failed to start proactive agent: {e}")

        # Start Local Knowledge Indexer (RAG) agent
        try:
            from core.indexer import start_indexing_agent
            start_indexing_agent()
            logger.info("Local knowledge indexer (RAG) agent started.")
        except Exception as e:
            logger.error(f"Failed to start RAG indexing agent: {e}")

        # Start Smart Suggestion Agent (habits + auto-learning)
        try:
            from core.habits import start_suggestion_agent
            start_suggestion_agent()
            logger.info("Smart Suggestion Agent started.")
        except Exception as e:
            logger.error(f"Failed to start suggestion agent: {e}")

        # Start Workflow Scheduler (task automation)
        try:
            from core.workflows import start_workflow_scheduler
            start_workflow_scheduler()
            logger.info("Workflow Scheduler started.")
        except Exception as e:
            logger.error(f"Failed to start workflow scheduler: {e}")

        if signals:
            signals.assistant_response.emit("David is ready.")
            signals.status_changed.emit("Ready")
        else:
            speak("David is ready.")

        logger.info("David AI started successfully")

        # ── Determine run mode ────────────────────────────────
        # In web (browser) mode we NEVER use the microphone or wake word.
        # Instead we loop process_single_command() which calls listen()
        # which polls the browser text queue (see voice/stt.py _web_mode).
        from voice.stt import _web_mode
        is_web = _web_mode()

        if WAKE_WORD_ENABLED and not is_web:
            from core.config import WAKE_WORD
            logger.info("Starting in wake word mode")
            if signals:
                signals.status_changed.emit(f"Waiting for '{WAKE_WORD}'...")
            try:
                wake_word_detector = SimpleWakeWordDetector(callback=on_wake_word_detected)
                wake_word_detector.start()
                import time
                while True:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Wake word failed to start: {e}")
                speak("Wake word system failed. Switching to continuous mode.")
                while True:
                    process_single_command()
        else:
            mode_name = "web command-queue mode" if is_web else "continuous mic mode"
            logger.info(f"Starting in {mode_name}")
            if signals:
                signals.status_changed.emit("Listening")
            while True:
                process_single_command()

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (Ctrl+C)")
        speak("Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")
        if signals:
            signals.status_changed.emit("Fatal error — see logs")
        else:
            speak("A critical error occurred.")
    finally:
        cleanup()