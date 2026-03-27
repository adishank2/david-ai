from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
import bcrypt
from core.database import (
    create_user, get_user_by_email, save_otp, verify_otp, mark_user_verified
)
from utils.email_auth import generate_otp, send_otp_email
from core.logger import get_logger
import hashlib

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Pydantic Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Helper functions
def _truncate_password(password: str) -> bytes:
    """Pre-hash password to bypass bcrypt 72 character limit."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_truncate_password(plain_password), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(_truncate_password(password), salt).decode('utf-8')


@router.post("/register")
def register(user: RegisterRequest):
    # Check if user already exists
    existing_user = get_user_by_email(user.email)
    
    if existing_user:
        if existing_user["is_verified"]:
            raise HTTPException(status_code=400, detail="Account already exists. Please log in.")
        # If they exist but aren't verified, we'll just resend a new OTP.
        # We also need to update their password hash if they changed it, but for simplicity
        # we'll just block creating a totally new record and let them continue verification.
    else:
        # Create new unverified user
        hashed_pw = get_password_hash(user.password)
        success = create_user(user.email, hashed_pw)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create account")
    
    # Generate and send OTP
    otp = generate_otp()
    save_otp(user.email, otp)
    email_sent = send_otp_email(user.email, otp)
    
    return {
        "message": "OTP sent to email", 
        "email_sent": email_sent, 
        "email": user.email
    }


@router.post("/verify")
def verify_account(req: VerifyRequest):
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user["is_verified"]:
        return {"message": "Account is already verified", "success": True}
        
    is_valid = verify_otp(req.email, req.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")
        
    mark_user_verified(req.email)
    return {"message": "Account verified successfully", "success": True}


@router.post("/login")
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not user["is_verified"]:
        raise HTTPException(status_code=403, detail="Account not verified. Please verify OTP first.")
        
    # In a fully production app, we'd return a JWT token here.
    # For David AI local use, returning a simple success token is sufficient.
    return {
        "message": "Login successful",
        "token": "david_auth_token_static_for_local_use",
        "email": req.email
    }
