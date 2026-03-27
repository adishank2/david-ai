"""
Music playback integration for David AI.
Supports local music files and basic playback controls.
"""

import os
import subprocess
import glob
from pathlib import Path
from typing import Optional, List
from core.logger import get_logger

logger = get_logger(__name__)

class MusicPlayer:
    """Manages music playback."""
    
    def __init__(self):
        self.music_dirs = [
            str(Path.home() / "Music"),
            str(Path.home() / "Downloads"),
        ]
        self.current_process = None
    
    def find_song(self, query: str) -> Optional[str]:
        """
        Find a song file matching the query.
        
        Args:
            query: Song name or artist to search for
            
        Returns:
            Path to song file or None
        """
        query_lower = query.lower()
        
        # Search in music directories
        for music_dir in self.music_dirs:
            if not os.path.exists(music_dir):
                continue
            
            # Search for MP3, WAV, M4A files
            for ext in ['*.mp3', '*.wav', '*.m4a', '*.flac']:
                pattern = os.path.join(music_dir, '**', ext)
                for file in glob.glob(pattern, recursive=True):
                    filename = os.path.basename(file).lower()
                    if query_lower in filename:
                        return file
        
        return None
    
    def play(self, song_path: str) -> tuple[bool, str]:
        """
        Play a song file.
        
        Args:
            song_path: Path to song file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not os.path.exists(song_path):
                return False, "Song file not found"
            
            logger.info(f"Playing: {song_path}")
            
            # Use Windows default media player
            self.current_process = subprocess.Popen(
                ['start', '', song_path],
                shell=True
            )
            
            song_name = os.path.basename(song_path)
            return True, f"Playing {song_name}"
            
        except Exception as e:
            logger.error(f"Failed to play song: {e}")
            return False, f"Couldn't play song: {str(e)}"
    
    def play_by_name(self, query: str) -> tuple[bool, str]:
        """
        Search and play a song by name.
        
        Args:
            query: Song name or artist
            
        Returns:
            Tuple of (success, message)
        """
        song_path = self.find_song(query)
        
        if not song_path:
            return False, f"Couldn't find a song matching '{query}'"
        
        return self.play(song_path)
    
    def stop(self) -> tuple[bool, str]:
        """Stop current playback."""
        try:
            if self.current_process:
                self.current_process.terminate()
                self.current_process = None
                return True, "Music stopped"
            return False, "No music is playing"
        except Exception as e:
            logger.error(f"Failed to stop music: {e}")
            return False, "Couldn't stop music"
    
    def get_music_library(self, limit: int = 10) -> List[str]:
        """
        Get list of available songs.
        
        Args:
            limit: Maximum number of songs to return
            
        Returns:
            List of song filenames
        """
        songs = []
        
        for music_dir in self.music_dirs:
            if not os.path.exists(music_dir):
                continue
            
            for ext in ['*.mp3', '*.wav', '*.m4a']:
                pattern = os.path.join(music_dir, '**', ext)
                for file in glob.glob(pattern, recursive=True):
                    songs.append(os.path.basename(file))
                    if len(songs) >= limit:
                        return songs
        
        return songs

# Global music player
_player = MusicPlayer()

def get_music_player() -> MusicPlayer:
    """Get the global music player."""
    return _player

def play_music(query: str) -> tuple[bool, str]:
    """Play music by name."""
    return _player.play_by_name(query)

def stop_music() -> tuple[bool, str]:
    """Stop music playback."""
    return _player.stop()
