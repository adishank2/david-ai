"""File operations plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import os
import shutil
import glob
from datetime import datetime, timedelta
from core.logger import get_logger
from core.config import FILE_OPS_ALLOWED_DIRS, FILE_OPS_MAX_SIZE_MB, FILE_OPS_CONFIRM_DELETE

logger = get_logger(__name__)

class FileOpsPlugin(BasePlugin):
    """Perform file and folder operations."""
    
    def __init__(self):
        super().__init__()
        self.userprofile = os.environ.get("USERPROFILE", "")
        # Build allowed paths
        self.allowed_paths = [
            os.path.join(self.userprofile, dir_name.strip())
            for dir_name in FILE_OPS_ALLOWED_DIRS
        ]
    
    def get_intents(self) -> List[str]:
        return ["create_folder", "delete_file", "move_file", "copy_file", 
                "list_files", "search_files", "file_info",
                "edit_file", "append_file"]
    
    def get_description(self) -> str:
        return "File operations: create, delete, move, copy, search, edit files and folders"
    
    def get_prompt_examples(self) -> str:
        return """create_folder:
{
  "intent": "create_folder",
  "path": "Desktop/NewFolder"
}

delete_file:
{
  "intent": "delete_file",
  "path": "Downloads/old_file.txt"
}

move_file:
{
  "intent": "move_file",
  "source": "Downloads/file.pdf",
  "destination": "Documents"
}

copy_file:
{
  "intent": "copy_file",
  "source": "Documents/report.docx",
  "destination": "Desktop"
}

list_files:
{
  "intent": "list_files",
  "path": "Downloads",
  "limit": 10 (optional)
}

search_files:
{
  "intent": "search_files",
  "path": "Documents",
  "pattern": "*.pdf"
}

edit_file:
{
  "intent": "edit_file",
  "path": "Desktop/notes.txt",
  "content": "new file content here"
}

append_file:
{
  "intent": "append_file",
  "path": "Desktop/notes.txt",
  "content": "text to append"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute file operation."""
        intent_type = intent.get("intent")
        
        try:
            if intent_type == "create_folder":
                path = self._resolve_path(intent.get("path", ""))
                if not self._is_allowed(path):
                    return "Access denied to this location."
                
                os.makedirs(path, exist_ok=True)
                logger.info(f"Created folder: {path}")
                return f"Created folder: {os.path.basename(path)}"
            
            elif intent_type == "delete_file":
                path = self._resolve_path(intent.get("path", ""))
                if not self._is_allowed(path):
                    return "Access denied to this location."
                
                if not os.path.exists(path):
                    return "File or folder not found."
                
                # GUARDIAN MODE SECURITY CHECK
                from core.config import SAFE_MODE
                if SAFE_MODE:
                    # In safe mode, we don't just delete. We return a "confirmation request" string 
                    # that the assistant must handle, OR we just block it for now saying "Manual confirmation required".
                    # For a V1 Industry Ready model, blocking reckless AI behavior is safer.
                    return f"🛑 SECURITY ALERT: Guardian Mode is ACTIVE.\nI cannot delete '{os.path.basename(path)}' automatically.\nPlease delete it manually or disable SAFE_MODE in config."
                
                # Send to recycle bin (safer than permanent delete)
                try:
                    from send2trash import send2trash
                    send2trash(path)
                    logger.warning(f"Deleted to recycle bin: {path}")
                    return f"Moved to recycle bin: {os.path.basename(path)}"
                except ImportError:
                    # Fallback to permanent delete (not recommended)
                    if os.path.isfile(path):
                        os.remove(path)
                    else:
                        shutil.rmtree(path)
                    logger.warning(f"Permanently deleted: {path}")
                    return f"Deleted: {os.path.basename(path)}"
            
            elif intent_type == "move_file":
                source = self._resolve_path(intent.get("source", ""))
                dest = self._resolve_path(intent.get("destination", ""))
                
                if not self._is_allowed(source) or not self._is_allowed(dest):
                    return "Access denied to source or destination."
                
                if not os.path.exists(source):
                    return "Source file not found."
                
                # If dest is a directory, keep the filename
                if os.path.isdir(dest):
                    dest = os.path.join(dest, os.path.basename(source))
                
                shutil.move(source, dest)
                logger.info(f"Moved {source} to {dest}")
                return f"Moved {os.path.basename(source)} to {os.path.dirname(dest)}"
            
            elif intent_type == "copy_file":
                source = self._resolve_path(intent.get("source", ""))
                dest = self._resolve_path(intent.get("destination", ""))
                
                if not self._is_allowed(source) or not self._is_allowed(dest):
                    return "Access denied to source or destination."
                
                if not os.path.exists(source):
                    return "Source file not found."
                
                # If dest is a directory, keep the filename
                if os.path.isdir(dest):
                    dest = os.path.join(dest, os.path.basename(source))
                
                if os.path.isfile(source):
                    shutil.copy2(source, dest)
                else:
                    shutil.copytree(source, dest)
                
                logger.info(f"Copied {source} to {dest}")
                return f"Copied {os.path.basename(source)} to {os.path.dirname(dest)}"
            
            elif intent_type == "list_files":
                path = self._resolve_path(intent.get("path", "Desktop"))
                limit = intent.get("limit", 10)
                
                if not self._is_allowed(path):
                    return "Access denied to this location."
                
                if not os.path.exists(path):
                    return "Folder not found."
                
                files = os.listdir(path)[:limit]
                if not files:
                    return "Folder is empty."
                
                result = f"Files in {os.path.basename(path)}: "
                for f in files:
                    result += f"{f}, "
                
                return result.rstrip(", ")
            
            elif intent_type == "search_files":
                path = self._resolve_path(intent.get("path", "Documents"))
                pattern = intent.get("pattern", "*")
                
                if not self._is_allowed(path):
                    return "Access denied to this location."
                
                search_pattern = os.path.join(path, "**", pattern)
                matches = glob.glob(search_pattern, recursive=True)[:10]
                
                if not matches:
                    return f"No files found matching {pattern}"
                
                result = f"Found {len(matches)} files: "
                for match in matches:
                    result += f"{os.path.basename(match)}, "
                
                return result.rstrip(", ")
            
            elif intent_type == "file_info":
                path = self._resolve_path(intent.get("path", ""))
                
                if not self._is_allowed(path):
                    return "Access denied to this location."
                
                if not os.path.exists(path):
                    return "File not found."
                
                stat = os.stat(path)
                size_mb = stat.st_size / (1024**2)
                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                
                return f"{os.path.basename(path)}: {size_mb:.2f} MB, modified {modified}"
            
            elif intent_type == "edit_file":
                path = self._resolve_path(intent.get("path", ""))
                content = intent.get("content", "")
                
                if not self._is_allowed(path):
                    return "Access denied to this location."
                if not content:
                    return "No content provided to write."
                
                # Safety: only allow text files
                ext = os.path.splitext(path)[1].lower()
                allowed_ext = ['.txt', '.md', '.csv', '.json', '.log', '.py', '.js', '.html', '.css', '.bat', '.sh', '.yaml', '.yml', '.xml', '.ini', '.cfg', '.conf']
                if ext and ext not in allowed_ext:
                    return f"Cannot edit {ext} files. Only text-based files are allowed."
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Wrote to file: {path}")
                return f"Saved content to {os.path.basename(path)}"
            
            elif intent_type == "append_file":
                path = self._resolve_path(intent.get("path", ""))
                content = intent.get("content", "")
                
                if not self._is_allowed(path):
                    return "Access denied to this location."
                if not content:
                    return "No content provided to append."
                
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(content + "\n")
                logger.info(f"Appended to file: {path}")
                return f"Appended content to {os.path.basename(path)}"
            
            else:
                return "Unknown file operation."
                
        except Exception as e:
            logger.error(f"File ops plugin error: {e}")
            return f"Sorry, I couldn't perform the file operation: {str(e)}"
    
    def _resolve_path(self, path: str) -> str:
        """Resolve relative path to absolute path."""
        if not path:
            return ""
        
        # If already absolute, return as is
        if os.path.isabs(path):
            return path
        
        # Try to resolve relative to allowed directories
        for allowed_path in self.allowed_paths:
            if os.path.basename(allowed_path).lower() in path.lower():
                # Remove the directory name from path
                relative = path.split("/", 1)[-1] if "/" in path else path.split("\\", 1)[-1] if "\\" in path else ""
                return os.path.join(allowed_path, relative) if relative else allowed_path
        
        # Default to Desktop
        return os.path.join(self.userprofile, "Desktop", path)
    
    def _is_allowed(self, path: str) -> bool:
        """Check if path is in allowed directories."""
        if not path:
            return False
        
        abs_path = os.path.abspath(path)
        for allowed in self.allowed_paths:
            if abs_path.startswith(os.path.abspath(allowed)):
                return True
        
        return False
