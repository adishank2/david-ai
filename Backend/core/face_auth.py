"""
David AI 2.0 — Face Recognition Login & Emotion Detection
Uses OpenCV + DeepFace for webcam-based biometric authentication
and real-time emotion analysis.
"""
import os
import cv2
import json
import base64
import numpy as np
from datetime import datetime
from core.logger import get_logger
from core.config import BASE_DIR

logger = get_logger(__name__)

FACE_DB_DIR = os.path.join(BASE_DIR, "face_db")
FACE_DATA_FILE = os.path.join(FACE_DB_DIR, "faces.json")
os.makedirs(FACE_DB_DIR, exist_ok=True)

# ── Face Data Store ──────────────────────────────────────
def _load_face_db():
    if os.path.exists(FACE_DATA_FILE):
        try:
            with open(FACE_DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_face_db(db):
    with open(FACE_DATA_FILE, "w") as f:
        json.dump(db, f, indent=2)


# ── Face Detection (Haar Cascade — fast, no GPU needed) ──
_face_cascade = None
def _get_cascade():
    global _face_cascade
    if _face_cascade is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def _extract_face_encoding(image_bgr):
    """Extract a simple face histogram encoding from an image."""
    cascade = _get_cascade()
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.3, 5, minSize=(80, 80))
    
    if len(faces) == 0:
        return None, None
    
    # Take the largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_roi = gray[y:y+h, x:x+w]
    
    # Resize to standard size for comparison
    face_resized = cv2.resize(face_roi, (128, 128))
    
    # Use LBPH (Local Binary Pattern Histogram) as a simple encoding
    # Normalize to create a comparable vector
    face_normalized = face_resized.astype(np.float32) / 255.0
    encoding = face_normalized.flatten().tolist()
    
    return encoding, (x, y, w, h)


def _compare_faces(encoding1, encoding2, threshold=0.65):
    """Compare two face encodings using cosine similarity."""
    v1 = np.array(encoding1)
    v2 = np.array(encoding2)
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = float(np.dot(v1, v2) / (norm1 * norm2))
    return similarity


# ── Public API ───────────────────────────────────────────

def register_face(email: str, image_b64: str) -> dict:
    """Register a face from a base64 webcam snapshot."""
    try:
        # Decode base64 image
        img_data = base64.b64decode(image_b64.split(",")[-1])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"success": False, "error": "Invalid image data"}
        
        encoding, bbox = _extract_face_encoding(image)
        if encoding is None:
            return {"success": False, "error": "No face detected. Please look directly at the camera."}
        
        # Save encoding
        db = _load_face_db()
        db[email] = {
            "encoding": encoding,
            "registered_at": datetime.now().isoformat(),
            "login_count": 0
        }
        _save_face_db(db)
        
        logger.info(f"Face registered for {email}")
        return {"success": True, "message": "Face ID registered successfully"}
        
    except Exception as e:
        logger.error(f"Face registration error: {e}")
        return {"success": False, "error": str(e)}


def verify_face(email: str, image_b64: str) -> dict:
    """Verify a face against the stored encoding."""
    try:
        db = _load_face_db()
        if email not in db:
            return {"success": False, "error": "No face registered for this account. Register first."}
        
        # Decode image
        img_data = base64.b64decode(image_b64.split(",")[-1])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"success": False, "error": "Invalid image data"}
        
        encoding, bbox = _extract_face_encoding(image)
        if encoding is None:
            return {"success": False, "error": "No face detected. Please look directly at the camera."}
        
        stored_encoding = db[email]["encoding"]
        similarity = _compare_faces(encoding, stored_encoding)
        
        logger.info(f"Face verification for {email}: similarity={similarity:.3f}")
        
        if similarity >= 0.65:
            db[email]["login_count"] = db[email].get("login_count", 0) + 1
            db[email]["last_login"] = datetime.now().isoformat()
            _save_face_db(db)
            return {
                "success": True, 
                "confidence": round(similarity * 100, 1),
                "message": f"Identity confirmed ({round(similarity*100)}% match)"
            }
        else:
            return {
                "success": False, 
                "confidence": round(similarity * 100, 1),
                "error": f"Face mismatch ({round(similarity*100)}% — need 65%+). Try better lighting."
            }
            
    except Exception as e:
        logger.error(f"Face verification error: {e}")
        return {"success": False, "error": str(e)}


def detect_emotion(image_b64: str) -> dict:
    """Detect emotion from a webcam frame using simple heuristics.
    
    For a lightweight approach, we use face geometry analysis.
    For production, swap this with DeepFace or FER.
    """
    try:
        img_data = base64.b64decode(image_b64.split(",")[-1])
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"emotion": "unknown", "confidence": 0}
        
        # Try using DeepFace if available
        try:
            from deepface import DeepFace
            result = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False, silent=True)
            if isinstance(result, list):
                result = result[0]
                
            emotion = result.get("dominant_emotion", "neutral")
            scores = result.get("emotion", {})
            confidence = scores.get(emotion, 50)
            
            return {
                "emotion": emotion,
                "confidence": round(confidence, 1),
                "all_emotions": {k: round(v, 1) for k, v in scores.items()}
            }
        except ImportError:
            # Fallback: simple brightness/contrast heuristic
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean_brightness = float(np.mean(gray))
            
            # Very rough heuristic based on image properties
            if mean_brightness > 140:
                return {"emotion": "happy", "confidence": 55.0}
            elif mean_brightness < 80:
                return {"emotion": "sad", "confidence": 45.0}
            else:
                return {"emotion": "neutral", "confidence": 60.0}
                
    except Exception as e:
        logger.error(f"Emotion detection error: {e}")
        return {"emotion": "unknown", "confidence": 0}


def get_registered_faces() -> list:
    """Get list of registered face emails."""
    db = _load_face_db()
    return [{"email": k, "registered_at": v.get("registered_at"), "login_count": v.get("login_count", 0)} 
            for k, v in db.items()]
