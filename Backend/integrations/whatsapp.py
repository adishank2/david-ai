"""
WhatsApp integration for David AI.
Send messages via WhatsApp Web using pywhatkit.
"""

import pywhatkit as kit
import json
import os
from datetime import datetime
from typing import Optional, Dict
from core.logger import get_logger

logger = get_logger(__name__)

class WhatsAppManager:
    """Manages WhatsApp messaging."""
    
    def __init__(self, contacts_file="contacts.json"):
        self.contacts_file = contacts_file
        self.contacts: Dict[str, str] = {}
        self.load_contacts()
    
    def load_contacts(self):
        """Load contacts from file."""
        try:
            if os.path.exists(self.contacts_file):
                with open(self.contacts_file, 'r', encoding='utf-8') as f:
                    self.contacts = json.load(f)
                logger.info(f"Loaded {len(self.contacts)} contacts")
            else:
                # Create default contacts file
                self.contacts = {
                    "example": "+1234567890"
                }
                self.save_contacts()
        except Exception as e:
            logger.error(f"Failed to load contacts: {e}")
            self.contacts = {}
    
    def save_contacts(self):
        """Save contacts to file."""
        try:
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(self.contacts, f, indent=2)
            logger.info(f"Saved {len(self.contacts)} contacts")
        except Exception as e:
            logger.error(f"Failed to save contacts: {e}")
    
    def get_phone_number(self, contact_name: str) -> Optional[str]:
        """
        Get phone number for a contact.
        
        Args:
            contact_name: Name of contact
            
        Returns:
            Phone number or None
        """
        name_lower = contact_name.lower()
        for name, number in self.contacts.items():
            if name.lower() == name_lower:
                return number
        return None
    
    def send_message(self, contact_name: str, message: str) -> tuple[bool, str]:
        """
        Send WhatsApp message.
        
        Args:
            contact_name: Name of contact
            message: Message to send
            
        Returns:
            Tuple of (success, status_message)
        """
        try:
            # Get phone number
            phone = self.get_phone_number(contact_name)
            if not phone:
                return False, f"I don't have a contact named '{contact_name}'. Add them to contacts.json first."
            
            # Send message instantly
            # wait_time: time to wait for WhatsApp Web to load (seconds)
            # tab_close: close tab after sending
            # close_time: time to wait after sending before closing (seconds)
            logger.info(f"Sending WhatsApp to {contact_name} ({phone}): {message}")
            
            kit.sendwhatmsg_instantly(
                phone, 
                message, 
                wait_time=20,     # Give it 20s to load
                tab_close=True, 
                close_time=5      # Wait 5s after sending before closing
            )
            
            return True, f"Message sent to {contact_name}!"
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp: {e}")
            return False, f"Couldn't send message: {str(e)}"
    
    def add_contact(self, name: str, phone: str):
        """Add a new contact."""
        self.contacts[name] = phone
        self.save_contacts()
        logger.info(f"Added contact: {name} - {phone}")

# Global WhatsApp manager
_whatsapp = WhatsAppManager()

def get_whatsapp_manager() -> WhatsAppManager:
    """Get the global WhatsApp manager."""
    return _whatsapp

def send_whatsapp(contact: str, message: str) -> tuple[bool, str]:
    """Send a WhatsApp message."""
    return _whatsapp.send_message(contact, message)
