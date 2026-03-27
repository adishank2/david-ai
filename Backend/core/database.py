import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from core.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "david_users.db")

def init_db():
    """Initialize the SQLite database with users and otps tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_verified BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # OTPs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otps (
                email TEXT PRIMARY KEY,
                otp_code TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

# Call init_db immediately upon import
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(email: str, password_hash: str) -> bool:
    """Create a new user. Returns False if email already exists."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash, is_verified) VALUES (?, ?, ?)", (email, password_hash, False))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    """Retrieve a user by their email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def mark_user_verified(email: str):
    """Mark a user as verified."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def save_otp(email: str, otp_code: str, valid_mins: int = 15):
    """Save an OTP code for an email, replacing any existing code."""
    conn = get_db_connection()
    expires_at = datetime.now() + timedelta(minutes=valid_mins)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)", (email, otp_code, expires_at))
    conn.commit()
    conn.close()

def verify_otp(email: str, otp_code: str) -> bool:
    """Verify an OTP code. Returns True if valid and not expired."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT otp_code, expires_at FROM otps WHERE email = ?", (email,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return False
        
    db_otp, expires_at_str = row
    
    # Check match
    if db_otp != otp_code:
        conn.close()
        return False
        
    # Check expiration
    # Handle both with and without microseconds
    try:
        expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        try:
            expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
            except Exception as e:
                logger.error(f"Failed to parse expiry date '{expires_at_str}': {e}")
                conn.close()
                return False
    
    if datetime.now() > expires_at:
        # Delete expired OTP
        cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return False
        
    # Valid - delete OTP so it can't be reused
    cursor.execute("DELETE FROM otps WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    return True

def get_user_count() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count
