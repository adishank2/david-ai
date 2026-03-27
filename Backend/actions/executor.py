import subprocess
import os
from actions.volume import volume_up, volume_down, mute, unmute
from core.logger import get_logger
from core.security import is_path_allowed, sanitize
from core.personality import get_personality

logger = get_logger(__name__)
personality = get_personality()

FOLDERS = {
    "desktop": os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
    "downloads": os.path.join(os.environ.get("USERPROFILE", ""), "Downloads"),
    "documents": os.path.join(os.environ.get("USERPROFILE", ""), "Documents"),
}

def execute(intent):
    """Execute an intent action with security validation and friendly responses."""
    try:
        intent_type = intent.get("intent")
        logger.info(f"Executing intent: {intent_type}")

        # Volume controls (safe, no validation needed)
        if intent_type == "volume_up":
            volume_up()
            return personality.success()

        if intent_type == "volume_down":
            volume_down()
            return personality.success()

        if intent_type == "mute":
            mute()
            return personality.success()

        if intent_type == "unmute":
            unmute()
            return personality.success()

        # Shutdown (dangerous command - already confirmed in assistant.py)
        if intent_type == "shutdown_request":
            logger.warning("Executing system shutdown")
            subprocess.Popen(["shutdown", "/s", "/t", "0"])
            return "Shutting down now. See you later!"

        # Open applications (sanitize app name)
        if intent_type == "open_app":
            app = intent.get("app")
            app = sanitize(app)
            logger.info(f"Opening application: {app}")
            
            if app == "chrome":
                subprocess.Popen(["cmd", "/c", "start", "chrome"], shell=False)
                return f"{personality.acknowledge()} Opening Chrome."
            
            if app == "notepad":
                subprocess.Popen(["notepad"])
                return f"{personality.acknowledge()} Opening Notepad."
            
            if app == "calculator":
                subprocess.Popen(["calc"])
                return f"{personality.acknowledge()} Opening Calculator."
            
            logger.warning(f"Unknown app requested: {app}")
            return f"I don't know how to open {app}. Try Chrome, Notepad, or Calculator."

        # Open folders (validate path)
        if intent_type == "open_folder":
            folder = intent.get("folder")
            path = FOLDERS.get(folder)
            
            if not path:
                logger.warning(f"Unknown folder requested: {folder}")
                return f"I don't know where {folder} is. Try Desktop, Downloads, or Documents."
            
            # Validate path security
            is_allowed, reason = is_path_allowed(path)
            if not is_allowed:
                logger.warning(f"Path blocked: {reason}")
                return "Sorry, I can't access that folder for security reasons."
            
            if not os.path.exists(path):
                logger.error(f"Folder does not exist: {path}")
                return f"The {folder} folder doesn't exist."
            
            logger.info(f"Opening folder: {path}")
            subprocess.Popen(["explorer", path])
            return f"{personality.acknowledge()} Opening {folder}."

        # WhatsApp messaging
        if intent_type == "send_whatsapp":
            try:
                from integrations.whatsapp import send_whatsapp
                contact = intent.get("contact", "")
                message = intent.get("message", "")
                
                if not contact or not message:
                    return "I need a contact name and message. Try: 'Send WhatsApp to Mom saying hello'"
                
                success, result = send_whatsapp(contact, message)
                if success:
                    return f"{personality.success()} {result}"
                else:
                    return result
            except ImportError:
                return "WhatsApp feature not available. Install pywhatkit: pip install pywhatkit"

        # Music playback
        if intent_type == "play_music":
            try:
                from integrations.music_player import play_music
                query = intent.get("query", "")
                
                if not query:
                    return "What song do you want to play?"
                
                # 1. Try Local Music
                success, result = play_music(query)
                if success:
                    return f"{personality.acknowledge()} {result}"
                
                # 2. Fallback to Spotify
                from core.config import SPOTIFY_ENABLED
                if SPOTIFY_ENABLED:
                    logger.info(f"Local music not found, trying Spotify for: {query}")
                    from integrations.spotify_client import get_spotify_client
                    spotify = get_spotify_client()
                    sp_success, sp_msg = spotify.play_track(query)
                    if sp_success:
                        return f"{personality.acknowledge()} {sp_msg}"
                        
                return result  # Return local error if both fail
            except ImportError:
                return "Music player not available."

        if intent_type == "stop_music":
            try:
                # Stop local music
                from integrations.music_player import stop_music
                stop_music()
                
                # Stop Spotify
                try:
                    from integrations.spotify_client import get_spotify_client
                    spotify = get_spotify_client()
                    spotify.pause()
                except:
                    pass
                    
                return "Music stopped."
            except ImportError:
                return "Music player not available."

        # Spotify controls
        if intent_type == "play_spotify":
            from integrations.spotify_client import get_spotify_client
            spotify = get_spotify_client()
            query = intent.get("query", "")
            if not query:
                return "What do you want to play on Spotify?"
            success, msg = spotify.play_track(query)
            return f"{personality.acknowledge()} {msg}" if success else msg

        if intent_type == "next_song":
            from integrations.spotify_client import get_spotify_client
            success, msg = get_spotify_client().next_track()
            return msg

        if intent_type == "previous_song":
            from integrations.spotify_client import get_spotify_client
            success, msg = get_spotify_client().previous_track()
            return msg

        if intent_type == "pause_music":
            from integrations.spotify_client import get_spotify_client
            success, msg = get_spotify_client().pause()
            return msg

        if intent_type == "resume_music":
            from integrations.spotify_client import get_spotify_client
            success, msg = get_spotify_client().resume()
            return msg

        logger.warning(f"Unknown intent type: {intent_type}")
        return personality.error("unclear")

    except Exception as e:
        logger.error(f"Error executing intent {intent}: {e}")
        return personality.error("failed")
