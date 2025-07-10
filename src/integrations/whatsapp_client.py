#!/usr/bin/env python3
"""
WhatsApp Client Factory
Chooses between Business API and Personal WhatsApp modes
"""

import os
import logging
from .business_whatsapp_client import BusinessWhatsAppClient
from .personal_whatsapp_client import PersonalWhatsAppClient

logger = logging.getLogger(__name__)

class WhatsAppClient:
    """WhatsApp client factory that chooses between business and personal modes"""
    
    def __init__(self):
        self.mode = os.getenv('WHATSAPP_MODE', 'business').lower()
        self.client = None
        
        if self.mode == 'personal':
            logger.info("Initializing Personal WhatsApp client (Selenium-based)")
            self.client = PersonalWhatsAppClient()
            # Personal client will auto-start session during initialization
        elif self.mode == 'business':
            logger.info("Initializing Business WhatsApp client (Meta API)")
            self.client = BusinessWhatsAppClient()
        else:
            logger.error(f"Invalid WhatsApp mode: {self.mode}. Using business mode as fallback.")
            self.mode = 'business'
            self.client = BusinessWhatsAppClient()
        
        logger.info(f"WhatsApp client initialized in {self.mode} mode")
    
    def send_message(self, to_phone, message):
        """
        Send WhatsApp message
        
        Args:
            to_phone (str): Recipient phone number (with country code)
            message (str): Message text
            
        Returns:
            dict: Result of message sending
        """
        if not self.client:
            return {
                "status": "failed",
                "to": to_phone,
                "error": "WhatsApp client not initialized"
            }
        
        return self.client.send_message(to_phone, message)
    
    def send_form_link(self, to_phone, form_url):
        """
        Send Google Form link via WhatsApp
        
        Args:
            to_phone (str): Recipient phone number
            form_url (str): Google Form URL
            
        Returns:
            dict: Result of message sending
        """
        if not self.client:
            return {
                "status": "failed",
                "to": to_phone,
                "error": "WhatsApp client not initialized"
            }
        
        return self.client.send_form_link(to_phone, form_url)
    
    def send_follow_up(self, to_phone, name, qualified=True):
        """
        Send follow-up message after form submission
        
        Args:
            to_phone (str): Recipient phone number
            name (str): Prospect name
            qualified (bool): Whether prospect is qualified
            
        Returns:
            dict: Result of message sending
        """
        if not self.client:
            return {
                "status": "failed",
                "to": to_phone,
                "error": "WhatsApp client not initialized"
            }
        
        return self.client.send_follow_up(to_phone, name, qualified)
    
    def verify_webhook(self, verify_token, challenge):
        """
        Verify WhatsApp webhook
        
        Args:
            verify_token (str): Token from webhook request
            challenge (str): Challenge from webhook request
            
        Returns:
            str or None: Challenge if verification successful, None otherwise
        """
        if not self.client:
            logger.error("WhatsApp client not initialized")
            return None
        
        return self.client.verify_webhook(verify_token, challenge)
    
    def get_mode(self):
        """Get current WhatsApp mode"""
        return self.mode
    
    def get_status(self):
        """Get client status"""
        status = {
            "mode": self.mode,
            "client_initialized": self.client is not None
        }
        
        # Add mode-specific status
        if self.mode == 'personal' and hasattr(self.client, 'get_session_status'):
            status.update(self.client.get_session_status())
        elif self.mode == 'business':
            status.update({
                "phone_number_id": getattr(self.client, 'phone_number_id', None),
                "api_configured": bool(getattr(self.client, 'phone_number_id', None))
            })
        
        return status
    
    def restart_personal_session(self):
        """Restart personal WhatsApp session (only for personal mode)"""
        if self.mode == 'personal' and self.client:
            logger.info("Restarting personal WhatsApp session")
            self.client.stop_session()
            return self.client.start_session()
        else:
            logger.warning("Restart session called on non-personal mode")
            return False
    
    def start_personal_session(self):
        """Start personal WhatsApp session (only for personal mode)"""
        if self.mode == 'personal' and self.client:
            logger.info("Starting personal WhatsApp session")
            return self.client.start_session()
        else:
            logger.warning("Start session called on non-personal mode")
            return False
    
    def stop_personal_session(self):
        """Stop personal WhatsApp session (only for personal mode)"""
        if self.mode == 'personal' and self.client:
            logger.info("Stopping personal WhatsApp session")
            self.client.stop_session()
            return True
        else:
            logger.warning("Stop session called on non-personal mode")
            return False
    
    def start_monitoring(self, force=False):
        """Start message monitoring (only for personal mode)"""
        if self.mode == 'personal' and self.client:
            logger.info("Starting WhatsApp message monitoring")
            return self.client.start_monitoring(force=force)
        else:
            logger.warning("Start monitoring called on non-personal mode")
            return False
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.mode == 'personal' and self.client:
            try:
                self.client.stop_session()
            except:
                pass 