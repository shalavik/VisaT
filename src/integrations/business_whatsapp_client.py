#!/usr/bin/env python3
"""
Business WhatsApp Client
Handles WhatsApp Business API integration
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

class BusinessWhatsAppClient:
    """WhatsApp Business API client"""
    
    def __init__(self):
        # Don't cache the token - get it fresh each time
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
        self.api_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
        if not self.phone_number_id:
            logger.warning("WhatsApp phone number ID not configured")
    
    def _get_access_token(self):
        """Get fresh access token from environment"""
        token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        if not token:
            logger.error("WhatsApp access token not found in environment")
        return token
    
    def send_message(self, to_phone, message):
        """
        Send WhatsApp message
        
        Args:
            to_phone (str): Recipient phone number (with country code)
            message (str): Message text
            
        Returns:
            dict: Result of message sending
        """
        try:
            # Get fresh token each time
            access_token = self._get_access_token()
            if not access_token:
                return {
                    "status": "failed",
                    "to": to_phone,
                    "error": "Access token not configured"
                }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_phone,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {to_phone}")
                return {
                    "status": "sent",
                    "to": to_phone,
                    "message_id": response.json().get('messages', [{}])[0].get('id'),
                    "message": "Message sent successfully"
                }
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return {
                    "status": "failed",
                    "to": to_phone,
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {to_phone}: {e}")
            return {
                "status": "failed",
                "to": to_phone,
                "error": str(e)
            }
    
    def send_form_link(self, to_phone, form_url):
        """
        Send Google Form link via WhatsApp
        
        Args:
            to_phone (str): Recipient phone number
            form_url (str): Google Form URL
            
        Returns:
            dict: Result of message sending
        """
        message = """🇹🇭 Thailand Visa Consultation - VisaT

Hello! Thank you for reaching out about Thailand visa services.

To provide you with the most accurate consultation, please fill out our quick assessment form:

👉 https://docs.google.com/forms/d/e/1FAIpQLScol3ZjPUuAueFf32s3-dHQiTE3oL1qmkDZGdt-YSqWffecdw/viewform?usp=sharing&ouid=114692513524380498491

This will help us:
✅ Understand your specific situation
✅ Provide personalized visa guidance
✅ Connect you with the right services

The form takes just 2-3 minutes to complete.

Best regards,
Slava - Thailand Visa Specialist"""
        
        return self.send_message(to_phone, message)
    
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
        if qualified:
            message = f"""
🎉 Great news, {name}!

You've been pre-qualified for Thailand visa consultation! 

📧 Check your email for detailed next steps and booking information.

Our team is excited to help you with your Thailand journey! 🇹🇭

Best regards,
VisaT Team
            """.strip()
        else:
            message = f"""
Hi {name},

Thank you for your interest in Thailand visa services.

📧 Please check your email for helpful resources and information about visa requirements.

Feel free to reach out when you're ready to explore Thailand visa options in the future.

Best regards,
VisaT Team 🇹🇭
            """.strip()
        
        return self.send_message(to_phone, message)
    
    def verify_webhook(self, verify_token, challenge):
        """
        Verify WhatsApp webhook
        
        Args:
            verify_token (str): Token from webhook request
            challenge (str): Challenge from webhook request
            
        Returns:
            str or None: Challenge if verification successful, None otherwise
        """
        if verify_token == self.verify_token:
            logger.info("WhatsApp webhook verification successful")
            return challenge
        else:
            logger.warning("WhatsApp webhook verification failed")
            return None 