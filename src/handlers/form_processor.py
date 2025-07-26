#!/usr/bin/env python3
"""
Form Processor
Handles Google Forms submissions and triggers qualification workflow
"""

import logging
from datetime import datetime
import json

from ..engines.qualification_engine import QualificationEngine
from ..integrations.gmail_client import GmailClient
from ..integrations.personal_whatsapp_client import PersonalWhatsAppClient
from ..utils.whatsapp_templates import get_follow_up_template

logger = logging.getLogger(__name__)

class FormProcessor:
    def __init__(self):
        self.qualification_engine = QualificationEngine()
        self.gmail_client = GmailClient()
        self.whatsapp_client = PersonalWhatsAppClient()
        
        logger.info("✅ Form processor initialized (without Calendly client - using polling)")
    
    def process_form_submission(self, prospect_data):
        """Process a form submission from Google Forms"""
        try:
            email = prospect_data.get('email')
            logger.info(f"📋 Processing form submission from: {email}")
            
            # Qualify the prospect
            is_qualified = self.qualification_engine.qualify_prospect(prospect_data)
            logger.info(f"📊 Qualification result for {email}: {is_qualified}")
            
            # Send appropriate email response
            self._send_email_response(prospect_data, is_qualified)
            
            # Send WhatsApp follow-up if qualified and phone number provided
            whatsapp_sent = False
            if is_qualified and prospect_data.get('whatsapp_number'):
                whatsapp_sent = self._send_whatsapp_follow_up(prospect_data)
            
            return {
                'email': email,
                'qualified': is_qualified,
                'email_sent': True,
                'whatsapp_sent': whatsapp_sent
            }
            
        except Exception as e:
            logger.error(f"Error processing form submission: {e}")
            return {
                'email': prospect_data.get('email', 'unknown'),
                'qualified': False,
                'email_sent': False,
                'whatsapp_sent': False,
                'error': str(e)
            }
    
    def _send_email_response(self, prospect_data, is_qualified):
        """Send email response based on qualification"""
        try:
            email = prospect_data.get('email')
            name = prospect_data.get('name', 'there')
            nationality = prospect_data.get('nationality', '')
            
            if is_qualified:
                subject = "🎯 Perfect Match! Let's Schedule Your Thailand Visa Consultation"
                
                # Qualified prospect email content
                message = f"""Dear {name},

Thank you for your interest in Thailand visa services! 

Based on your profile, you're an excellent candidate for our specialized visa consultation services. We'd love to help you navigate the Thailand visa process.

📅 Next Step: Schedule Your Free Consultation
Please book a convenient time for your personalized consultation:
👉 https://calendly.com/slavaidler/30min

During this consultation, we'll:
✅ Review your specific situation and nationality requirements
✅ Explain the best visa options for your needs  
✅ Provide a clear roadmap for your application
✅ Answer all your questions about living in Thailand

Best regards,
The Thailand Visa Team

P.S. Limited slots available - book today to secure your spot!
"""
                
                html_message = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2c5aa0;">🎯 Perfect Match! Let's Schedule Your Thailand Visa Consultation</h2>
    
    <p>Dear <strong>{name}</strong>,</p>
    
    <p>Thank you for your interest in Thailand visa services!</p>
    
    <p>Based on your profile, you're an excellent candidate for our specialized visa consultation services. We'd love to help you navigate the Thailand visa process.</p>
    
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="color: #28a745; margin-top: 0;">📅 Next Step: Schedule Your Free Consultation</h3>
        <p>Please book a convenient time for your personalized consultation:</p>
        <p style="text-align: center;">
            <a href="https://calendly.com/slavaidler/30min" 
               style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                📅 Book Your Consultation Now
            </a>
        </p>
    </div>
    
    <h4>During this consultation, we'll:</h4>
    <ul>
        <li>✅ Review your specific situation and nationality requirements</li>
        <li>✅ Explain the best visa options for your needs</li>
        <li>✅ Provide a clear roadmap for your application</li>
        <li>✅ Answer all your questions about living in Thailand</li>
    </ul>
    
    <p>Best regards,<br>
    <strong>The Thailand Visa Team</strong></p>
    
    <p style="font-size: 12px; color: #6c757d;">
        <em>P.S. Limited slots available - book today to secure your spot!</em>
    </p>
</div>
"""
            else:
                subject = "Thank You for Your Interest in Thailand Visa Services"
                
                # General inquiry email content
                message = f"""Dear {name},

Thank you for your interest in Thailand visa services!

We've received your inquiry and appreciate you reaching out to us. While your current profile may not match our specialized consultation services at this time, we'd still like to help.

📧 We'll be in touch soon with general information about Thailand visa options that might be suitable for your situation.

If you have any urgent questions, please don't hesitate to contact us.

Best regards,
The Thailand Visa Team
"""
                
                html_message = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #2c5aa0;">Thank You for Your Interest</h2>
    
    <p>Dear <strong>{name}</strong>,</p>
    
    <p>Thank you for your interest in Thailand visa services!</p>
    
    <p>We've received your inquiry and appreciate you reaching out to us. While your current profile may not match our specialized consultation services at this time, we'd still like to help.</p>
    
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <p>📧 We'll be in touch soon with general information about Thailand visa options that might be suitable for your situation.</p>
    </div>
    
    <p>If you have any urgent questions, please don't hesitate to contact us.</p>
    
    <p>Best regards,<br>
    <strong>The Thailand Visa Team</strong></p>
</div>
"""
            
            # Send the email
            self.gmail_client.send_email(
                to_email=email,
                subject=subject,
                message=message,
                html_message=html_message
            )
            
            logger.info(f"📧 Sent email to {email} (qualified: {is_qualified})")
            
        except Exception as e:
            logger.error(f"Failed to send email to {prospect_data.get('email')}: {e}")
            raise
    
    def _send_whatsapp_follow_up(self, prospect_data):
        """Send WhatsApp follow-up message"""
        try:
            whatsapp_number = prospect_data.get('whatsapp_number')
            name = prospect_data.get('name', 'there')
            
            if not whatsapp_number:
                logger.warning("No WhatsApp number provided for follow-up")
                return False
            
            # Get follow-up template with Calendly link
            calendly_link = "https://calendly.com/slavaidler/30min"
            message = get_follow_up_template(name, calendly_link)
            
            # Send via WhatsApp
            success = self.whatsapp_client.send_follow_up(whatsapp_number, name, message)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp follow-up: {e}")
            return False 