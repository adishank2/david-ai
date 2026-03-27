import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pyautogui
from core.config import (
    SPOTIFY_CLIENT_ID, 
    SPOTIFY_CLIENT_SECRET, 
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_DEVICE_ID
)
from core.logger import get_logger

logger = get_logger(__name__)

class SpotifyClient:
    """Spotify API client wrapper with media key fallback."""
    
    def __init__(self):
        self.sp = None
        self.authenticated = False
        
        if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=SPOTIFY_REDIRECT_URI,
                    scope="user-modify-playback-state user-read-playback-state"
                ))
                self.authenticated = True
                logger.info("Spotify client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify: {e}")
        else:
            logger.warning("Spotify credentials not found in config")

    def _fallback_media_key(self, key: str, action_name: str) -> tuple[bool, str]:
        """Press a global media key as fallback."""
        try:
            logger.info(f"Using fallback media key: {key}")
            pyautogui.press(key)
            return True, f"{action_name} (Basic Mode)"
        except Exception as e:
            msg = f"Failed to simulate media key: {e}"
            logger.error(msg)
            return False, msg

    def play_track(self, query: str) -> tuple[bool, str]:
        """Search and play a track."""
        if not self.authenticated:
            return False, "Spotify is not configured."
            
        try:
            # Search for track
            results = self.sp.search(q=query, limit=1, type='track')
            tracks = results['tracks']['items']
            
            if not tracks:
                return False, f"Couldn't find track '{query}'"
            
            track = tracks[0]
            track_uri = track['uri']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            
            # Play
            self.sp.start_playback(device_id=SPOTIFY_DEVICE_ID or None, uris=[track_uri])
            return True, f"Playing {track_name} by {artist_name} on Spotify"
            
        except spotipy.exceptions.SpotifyException as e:
            # Fallback for Premium restriction
            if "Premium" in str(e) or "403" in str(e) or "Restricted" in str(e):
                logger.warning("Spotify API restricted (Premium required). Trying to open URL instead.")
                # We can try to open the track URL in browser, allowing user to play it manually
                import webbrowser
                try:
                    webbrowser.open(track['external_urls']['spotify'])
                    return True, f"Opened {track_name} in Spotify (Premium required for auto-play)"
                except:
                    pass
            
            logger.error(f"Spotify API error: {e}")
            return False, f"Spotify error: {e}"
        except Exception as e:
            logger.error(f"Spotify error: {e}")
            return False, f"Couldn't play on Spotify: {e}"

    def pause(self) -> tuple[bool, str]:
        """Pause playback."""
        if not self.authenticated:
            return self._fallback_media_key("playpause", "Paused")
        try:
            self.sp.pause_playback(device_id=SPOTIFY_DEVICE_ID or None)
            return True, "Spotify paused"
        except Exception as e:
            logger.warning(f"Spotify Pause failed: {e}. Using fallback.")
            return self._fallback_media_key("playpause", "Paused")

    def resume(self) -> tuple[bool, str]:
        """Resume playback."""
        if not self.authenticated:
            return self._fallback_media_key("playpause", "Resumed")
        try:
            self.sp.start_playback(device_id=SPOTIFY_DEVICE_ID or None)
            return True, "Spotify resumed"
        except Exception as e:
            logger.warning(f"Spotify Resume failed: {e}. Using fallback.")
            return self._fallback_media_key("playpause", "Resumed")

    def next_track(self) -> tuple[bool, str]:
        """Skip to next track."""
        if not self.authenticated:
             return self._fallback_media_key("nexttrack", "Skipped")
        try:
            self.sp.next_track(device_id=SPOTIFY_DEVICE_ID or None)
            return True, "Skipped to next song"
        except Exception as e:
            logger.warning(f"Spotify Next failed: {e}. Using fallback.")
            return self._fallback_media_key("nexttrack", "Skipped")

    def previous_track(self) -> tuple[bool, str]:
        """Skip to previous track."""
        if not self.authenticated:
            return self._fallback_media_key("prevtrack", "Previous")
        try:
            self.sp.previous_track(device_id=SPOTIFY_DEVICE_ID or None)
            return True, "Skipped to previous song"
        except Exception as e:
            logger.warning(f"Spotify Previous failed: {e}. Using fallback.")
            return self._fallback_media_key("prevtrack", "Previous")

# Global instance
_spotify = SpotifyClient()

def get_spotify_client() -> SpotifyClient:
    return _spotify
