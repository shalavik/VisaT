#!/usr/bin/env python3
"""
Gmail Client - SMTP Authentication
Simple email sending using Gmail SMTP with app password
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)

class GmailClient:
    """Gmail client using SMTP authentication"""
    
    def __init__(self):
        self.sender_email = os.getenv('GMAIL_SENDER_EMAIL')
        self.sender_name = os.getenv('GMAIL_SENDER_NAME')
        self.password = os.getenv('GMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        if not all([self.sender_email, self.sender_name, self.password]):
            logger.warning("Gmail SMTP credentials not fully configured")
    
    def send_email(self, to_email, subject, message, html_message=None):
        """
        Send email using Gmail SMTP
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message (str): Plain text message
            html_message (str, optional): HTML formatted message
            
        Returns:
            dict: Result of email sending
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            text_part = MIMEText(message, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_message:
                html_part = MIMEText(html_message, 'html')
                msg.attach(html_part)
            
            # Connect to Gmail SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.sender_email, self.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {
                "status": "failed",
                "to": to_email,
                "subject": subject,
                "error": str(e)
            }
    
    def send_qualification_email(self, prospect_data, qualified=True, calendly_link=None):
        """
        Send qualification result email
        
        Args:
            prospect_data (dict): Prospect information
            qualified (bool): Whether prospect is qualified
            calendly_link (str, optional): Calendly booking link
            
        Returns:
            dict: Result of email sending
        """
        try:
            email = prospect_data.get('email')
            name = prospect_data.get('full_name', 'Valued Client')
            
            if qualified:
                subject = "🎉 Great News! You're Pre-Qualified for Thailand Visa Consultation"
                
                # HTML message for qualified prospects
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2E8B57;">Congratulations, {name}!</h2>
                        
                        <p>We're excited to inform you that based on your initial information, you appear to be an excellent candidate for Thailand visa services.</p>
                        
                        <div style="background-color: #f0f8f0; padding: 15px; border-left: 4px solid #2E8B57; margin: 20px 0;">
                            <h3 style="margin-top: 0;">✅ Your Pre-Qualification Status: APPROVED</h3>
                            <p>Your profile meets our initial criteria for Thailand visa consultation.</p>
                        </div>
                        
                        <h3>🗓️ Next Steps:</h3>
                        <p>Schedule your <strong>FREE 30-minute consultation</strong> to discuss:</p>
                        <ul>
                            <li>Your specific visa options</li>
                            <li>Required documentation</li>
                            <li>Timeline and process</li>
                            <li>Investment opportunities (if applicable)</li>
                        </ul>
                        
                        {f'<p><a href="{calendly_link}" style="background-color: #2E8B57; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0;">📅 Book Your Free Consultation</a></p>' if calendly_link else ''}
                        
                        <p>Our Thailand visa experts are ready to help you navigate the process smoothly.</p>
                        
                        <hr style="margin: 30px 0;">
                        <p style="font-size: 14px; color: #666;">
                            Best regards,<br>
                            <strong>{self.sender_name}</strong><br>
                            VisaT - Thailand Visa Specialists<br>
                            📧 {self.sender_email}
                        </p>
                    </div>
                </body>
                </html>
                """
                
                # Plain text version
                plain_message = f"""
                Congratulations, {name}!
                
                We're excited to inform you that based on your initial information, you appear to be an excellent candidate for Thailand visa services.
                
                ✅ Your Pre-Qualification Status: APPROVED
                Your profile meets our initial criteria for Thailand visa consultation.
                
                🗓️ Next Steps:
                Schedule your FREE 30-minute consultation to discuss:
                • Your specific visa options
                • Required documentation  
                • Timeline and process
                • Investment opportunities (if applicable)
                
                {f'Book your consultation: {calendly_link}' if calendly_link else 'We will contact you shortly to schedule your consultation.'}
                
                Our Thailand visa experts are ready to help you navigate the process smoothly.
                
                Best regards,
                {self.sender_name}
                VisaT - Thailand Visa Specialists
                📧 {self.sender_email}
                """
                
            else:
                subject = "Thank You for Your Interest in Thailand Visa Services"
                
                # HTML message for non-qualified prospects
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4682B4;">Thank You, {name}</h2>
                        
                        <p>Thank you for your interest in Thailand visa services. We appreciate you taking the time to submit your information.</p>
                        
                        <div style="background-color: #f0f4f8; padding: 15px; border-left: 4px solid #4682B4; margin: 20px 0;">
                            <p>After reviewing your current situation, we believe you may benefit from exploring additional preparation options before proceeding with visa applications.</p>
                        </div>
                        
                        <h3>📚 Helpful Resources:</h3>
                        <p>We recommend reviewing Thailand's official visa requirements and considering:</p>
                        <ul>
                            <li>Financial planning and documentation</li>
                            <li>Understanding different visa categories</li>
                            <li>Exploring alternative pathways</li>
                        </ul>
                        
                        <p>We encourage you to reach out again in the future when your circumstances may better align with Thailand's visa requirements.</p>
                        
                        <hr style="margin: 30px 0;">
                        <p style="font-size: 14px; color: #666;">
                            Best regards,<br>
                            <strong>{self.sender_name}</strong><br>
                            VisaT - Thailand Visa Specialists<br>
                            📧 {self.sender_email}
                        </p>
                    </div>
                </body>
                </html>
                """
                
                # Plain text version
                plain_message = f"""
                Thank You, {name}
                
                Thank you for your interest in Thailand visa services. We appreciate you taking the time to submit your information.
                
                After reviewing your current situation, we believe you may benefit from exploring additional preparation options before proceeding with visa applications.
                
                📚 Helpful Resources:
                We recommend reviewing Thailand's official visa requirements and considering:
                • Financial planning and documentation
                • Understanding different visa categories  
                • Exploring alternative pathways
                
                We encourage you to reach out again in the future when your circumstances may better align with Thailand's visa requirements.
                
                Best regards,
                {self.sender_name}
                VisaT - Thailand Visa Specialists
                📧 {self.sender_email}
                """
            
            return self.send_email(email, subject, plain_message, html_message)
            
        except Exception as e:
            logger.error(f"Failed to send qualification email: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def test_connection(self):
        """Test Gmail SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.quit()
            
            logger.info("Gmail SMTP connection test successful")
            return {"status": "success", "message": "Connection successful"}
            
        except Exception as e:
            logger.error(f"Gmail SMTP connection test failed: {e}")
            return {"status": "failed", "error": str(e)} 