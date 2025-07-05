#!/usr/bin/env python3
"""
Contact Handler
Processes incoming messages from WhatsApp and Facebook
"""

import os
import logging
from src.integrations.whatsapp_client import WhatsAppClient

logger = logging.getLogger(__name__)

class ContactHandler:
    """Handles incoming contact messages"""
    
    def __init__(self):
        self.whatsapp_client = WhatsAppClient()
        self.google_form_url = os.getenv('GOOGLE_FORM_URL')
    
    def handle_whatsapp_message(self, webhook_data):
        """
        Handle incoming WhatsApp message
        
        Args:
            webhook_data (dict): WhatsApp webhook payload
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract message data from webhook
            entry = webhook_data.get('entry', [])
            if not entry:
                return {"status": "no_entry", "message": "No entry in webhook data"}
            
            changes = entry[0].get('changes', [])
            if not changes:
                return {"status": "no_changes", "message": "No changes in webhook data"}
            
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return {"status": "no_messages", "message": "No messages in webhook data"}
            
            # Process each message
            results = []
            for message in messages:
                result = self._process_whatsapp_message(message)
                results.append(result)
            
            logger.info(f"Processed {len(results)} WhatsApp messages")
            return {"status": "processed", "results": results}
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp message: {e}")
            return {"status": "error", "error": str(e)}
    
    def _process_whatsapp_message(self, message):
        """
        Process individual WhatsApp message
        
        Args:
            message (dict): Message data
            
        Returns:
            dict: Processing result
        """
        try:
            from_number = message.get('from')
            message_id = message.get('id')
            message_type = message.get('type')
            
            if message_type == 'text':
                text_body = message.get('text', {}).get('body', '')
                
                # Send form link in response
                if self.google_form_url:
                    response = self.whatsapp_client.send_form_link(from_number, self.google_form_url)
                    
                    logger.info(f"Sent form link to {from_number}")
                    return {
                        "status": "form_sent",
                        "from": from_number,
                        "message_id": message_id,
                        "response": response
                    }
                else:
                    logger.warning("Google Form URL not configured")
                    return {
                        "status": "no_form_url",
                        "from": from_number,
                        "message_id": message_id
                    }
            else:
                logger.info(f"Unsupported message type: {message_type}")
                return {
                    "status": "unsupported_type",
                    "from": from_number,
                    "message_id": message_id,
                    "type": message_type
                }
                
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return {"status": "error", "error": str(e)}
    
    def handle_facebook_message(self, webhook_data):
        """
        Handle incoming Facebook Messenger message
        
        Args:
            webhook_data (dict): Facebook webhook payload
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract message data from webhook
            entry = webhook_data.get('entry', [])
            if not entry:
                return {"status": "no_entry", "message": "No entry in webhook data"}
            
            messaging = entry[0].get('messaging', [])
            if not messaging:
                return {"status": "no_messaging", "message": "No messaging in webhook data"}
            
            # Process each message
            results = []
            for message_event in messaging:
                result = self._process_facebook_message(message_event)
                results.append(result)
            
            logger.info(f"Processed {len(results)} Facebook messages")
            return {"status": "processed", "results": results}
            
        except Exception as e:
            logger.error(f"Error handling Facebook message: {e}")
            return {"status": "error", "error": str(e)}
    
    def _process_facebook_message(self, message_event):
        """
        Process individual Facebook message
        
        Args:
            message_event (dict): Message event data
            
        Returns:
            dict: Processing result
        """
        try:
            sender_id = message_event.get('sender', {}).get('id')
            message = message_event.get('message', {})
            message_text = message.get('text', '')
            
            # For Facebook, we would need to implement Facebook Send API
            # For now, just log the interaction
            logger.info(f"Facebook message from {sender_id}: {message_text}")
            
            # In a full implementation, you would:
            # 1. Send form link via Facebook Send API
            # 2. Store interaction in database/sheets
            
            return {
                "status": "logged",
                "sender_id": sender_id,
                "message": message_text,
                "note": "Facebook Send API not implemented - would send form link here"
            }
            
        except Exception as e:
            logger.error(f"Error processing Facebook message: {e}")
            return {"status": "error", "error": str(e)} 