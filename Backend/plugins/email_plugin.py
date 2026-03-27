"""Email integration plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logger import get_logger
from core.config import (EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_ADDRESS, 
                         EMAIL_PASSWORD, EMAIL_USE_TLS)

logger = get_logger(__name__)

class EmailPlugin(BasePlugin):
    """Send and read emails."""
    
    def get_intents(self) -> List[str]:
        return ["send_email", "read_emails", "email_count"]
    
    def get_description(self) -> str:
        return "Email integration: send emails, read inbox, check email count"
    
    def get_prompt_examples(self) -> str:
        return """send_email:
{
  "intent": "send_email",
  "to": "recipient@example.com",
  "subject": "Meeting Notes",
  "body": "Here are the notes from today's meeting..."
}

read_emails:
{
  "intent": "read_emails",
  "limit": 5 (optional, default 5)
}

email_count:
{
  "intent": "email_count"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute email operation."""
        intent_type = intent.get("intent")
        
        # Check if email is configured
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return "Email is not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file."
        
        try:
            if intent_type == "send_email":
                to_address = intent.get("to", "")
                subject = intent.get("subject", "")
                body = intent.get("body", "")
                
                if not to_address:
                    return "Please provide a recipient email address."
                
                if not subject:
                    subject = "(No Subject)"
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = to_address
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                
                # Send email
                with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
                    if EMAIL_USE_TLS:
                        server.starttls()
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.send_message(msg)
                
                logger.info(f"Sent email to {to_address}")
                return f"Email sent to {to_address}"
            
            elif intent_type == "read_emails":
                limit = intent.get("limit", 5)
                
                # Connect to IMAP server
                imap_server = EMAIL_SMTP_SERVER.replace("smtp", "imap")
                mail = imaplib.IMAP4_SSL(imap_server)
                mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                mail.select('inbox')
                
                # Search for unread emails
                status, messages = mail.search(None, 'UNSEEN')
                email_ids = messages[0].split()
                
                if not email_ids:
                    mail.logout()
                    return "No unread emails."
                
                # Get latest emails
                result = f"You have {len(email_ids)} unread emails. Latest {min(limit, len(email_ids))}: "
                
                for email_id in email_ids[-limit:]:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    subject = msg['subject']
                    from_addr = msg['from']
                    
                    result += f"From {from_addr}, Subject: {subject}. "
                
                mail.logout()
                return result
            
            elif intent_type == "email_count":
                # Connect to IMAP server
                imap_server = EMAIL_SMTP_SERVER.replace("smtp", "imap")
                mail = imaplib.IMAP4_SSL(imap_server)
                mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                mail.select('inbox')
                
                # Count unread emails
                status, messages = mail.search(None, 'UNSEEN')
                email_ids = messages[0].split()
                count = len(email_ids)
                
                mail.logout()
                
                if count == 0:
                    return "You have no unread emails."
                elif count == 1:
                    return "You have 1 unread email."
                else:
                    return f"You have {count} unread emails."
            
            else:
                return "Unknown email command."
                
        except Exception as e:
            logger.error(f"Email plugin error: {e}")
            return f"Sorry, I couldn't perform the email operation. Error: {str(e)}"
