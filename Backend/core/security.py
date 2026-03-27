"""
Security module for David AI.
Provides command validation, path whitelisting, and audit logging.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.logger import get_logger

logger = get_logger(__name__)

# Dangerous commands that require confirmation
DANGEROUS_COMMANDS = [
    "shutdown", "restart", "reboot", "format", "delete", "remove", "rm",
    "kill", "taskkill", "stop-process", "registry", "reg", "diskpart"
]

# Allowed directories for file operations
ALLOWED_DIRECTORIES = [
    str(Path.home() / "Documents"),
    str(Path.home() / "Downloads"),
    str(Path.home() / "Desktop"),
    str(Path.home() / "Music"),
    str(Path.home() / "Pictures"),
    str(Path.home() / "Videos"),
]

# Blocked commands (never allow)
BLOCKED_COMMANDS = [
    "format c:", "del /f /s /q c:\\*", "rd /s /q c:\\",
    "rm -rf /", ":(){ :|:& };:",  # Fork bomb
]

class SecurityValidator:
    """Validates commands and file paths for security."""
    
    def __init__(self):
        self.audit_log_path = "security_audit.log"
        
    def validate_command(self, command: str) -> tuple[bool, str]:
        """
        Validate if a command is safe to execute.
        
        Args:
            command: Command to validate
            
        Returns:
            Tuple of (is_safe, reason)
        """
        command_lower = command.lower().strip()
        
        # Check blocked commands
        for blocked in BLOCKED_COMMANDS:
            if blocked in command_lower:
                reason = f"Blocked command detected: {blocked}"
                self._audit_log("BLOCKED", command, reason)
                return False, reason
        
        # Check dangerous commands
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                reason = f"Dangerous command requires confirmation: {dangerous}"
                self._audit_log("REQUIRES_CONFIRMATION", command, reason)
                return False, reason
        
        # Command is safe
        self._audit_log("ALLOWED", command, "Command validated")
        return True, "Command is safe"
    
    def validate_path(self, path: str) -> tuple[bool, str]:
        """
        Validate if a file path is in allowed directories.
        
        Args:
            path: File path to validate
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        try:
            abs_path = str(Path(path).resolve())
            
            # Check if path is in allowed directories
            for allowed_dir in ALLOWED_DIRECTORIES:
                if abs_path.startswith(allowed_dir):
                    self._audit_log("PATH_ALLOWED", abs_path, f"Path in allowed directory: {allowed_dir}")
                    return True, "Path is in allowed directory"
            
            # Path not in allowed directories
            reason = f"Path not in allowed directories: {abs_path}"
            self._audit_log("PATH_BLOCKED", abs_path, reason)
            return False, reason
            
        except Exception as e:
            reason = f"Invalid path: {e}"
            self._audit_log("PATH_ERROR", path, reason)
            return False, reason
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Sanitized input
        """
        # Remove null bytes
        sanitized = user_input.replace('\x00', '')
        
        # Remove excessive whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Limit length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")
        
        return sanitized
    
    def _audit_log(self, action: str, target: str, reason: str):
        """
        Log security events to audit log.
        
        Args:
            action: Action type (ALLOWED, BLOCKED, etc.)
            target: Command or path being validated
            reason: Reason for decision
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "action": action,
            "target": target,
            "reason": reason
        }
        
        try:
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            logger.info(f"Security audit: {action} - {target[:50]}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent audit log entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        try:
            if not os.path.exists(self.audit_log_path):
                return []
            
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get last N lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            # Parse JSON
            logs = []
            for line in recent_lines:
                try:
                    logs.append(json.loads(line))
                except:
                    pass
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to read audit logs: {e}")
            return []

# Global security validator instance
_validator = SecurityValidator()

def get_validator() -> SecurityValidator:
    """Get the global security validator instance."""
    return _validator

def is_command_safe(command: str) -> tuple[bool, str]:
    """Check if a command is safe to execute."""
    return _validator.validate_command(command)

def is_path_allowed(path: str) -> tuple[bool, str]:
    """Check if a file path is allowed."""
    return _validator.validate_path(path)

def sanitize(user_input: str) -> str:
    """Sanitize user input."""
    return _validator.sanitize_input(user_input)
