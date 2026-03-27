import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import os
from core.config import EMAIL_ADDRESS, EMAIL_PASSWORD
from core.logger import get_logger

logger = get_logger(__name__)

def generate_otp() -> str:
    """Generate a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Send an OTP code to the user's email via SMTP.
    Returns True if successful, False otherwise.
    """
    # If no email configured, just print to console (good for local testing)
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.warning(f"No SMTP credentials configured. Printing OTP to console instead.")
        logger.info(f"========== OTP FOR {to_email} is: {otp_code} ==========")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = f"David AI <{EMAIL_ADDRESS}>"
        msg['To'] = to_email
        msg['Subject'] = "David AI - Your Verification Code"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #fff; background-color: #0b0f19; padding: 20px;">
                <h2 style="color: #00f3ff;">David AI</h2>
                <p>Hello,</p>
                <p>Your verification code is:</p>
                <h1 style="color: #00f3ff; font-size: 32px; letter-spacing: 5px;">{otp_code}</h1>
                <p>This code will expire in 15 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        
        logger.info(f"OTP email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {to_email}: {e}")
        # Even if it fails, print the OTP so the user isn't stuck during testing
        logger.info(f"========== FALLBACK OTP FOR {to_email} is: {otp_code} ==========")
        return False
