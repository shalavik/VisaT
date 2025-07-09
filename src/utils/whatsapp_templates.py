#!/usr/bin/env python3
"""
WhatsApp Auto-Reply Templates
Specialized templates for WhatsApp Web automation
"""

import os
from typing import Dict, Any

class WhatsAppTemplateManager:
    """Manages WhatsApp auto-reply templates with dynamic content injection"""
    
    def __init__(self):
        self.templates = {
            'default': self._get_exact_user_template,
            'plain': self._get_plain_text_template,  # Add plain text version
            'enhanced': self._get_enhanced_engagement_template,
            'conversational': self._get_conversational_template,
            'conversion': self._get_conversion_focused_template
        }
    
    def get_auto_reply_template(self, template_type: str = None, **kwargs) -> str:
        """
        Get auto-reply template based on type and inject variables
        
        Args:
            template_type (str): Template type ('default', 'enhanced', 'conversational', 'conversion')
            **kwargs: Variables to inject into template
            
        Returns:
            str: Formatted template message
        """
        # Get template type from environment or use default
        if template_type is None:
            template_type = os.getenv('WHATSAPP_AUTO_REPLY_TEMPLATE', 'default')
        
        # Get template function
        template_func = self.templates.get(template_type, self.templates['default'])
        
        # Generate template with variable injection
        return template_func(**kwargs)
    
    def _get_exact_user_template(self, **kwargs) -> str:
        """
        Exact template as specified by user (Primary Template)
        Thailand visa consultation with Google Form link
        """
        form_url = kwargs.get('form_url', os.getenv('GOOGLE_FORM_URL', 'https://forms.gle/your-form-id'))
        consultant_name = kwargs.get('consultant_name', os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava'))
        
        template = f"""Hello! 👋

Thank you for contacting us about Thailand visa consultation services.

To provide you with the most accurate consultation, please fill out our quick assessment form:

👉 {form_url}

This will help us:
✅ Understand your specific situation
✅ Provide personalized visa guidance
✅ Connect you with the right services

The form takes just 2-3 minutes to complete.

Best regards,
{consultant_name} - Thailand Visa Specialist"""
        
        return template.strip()
    
    def _get_plain_text_template(self, **kwargs) -> str:
        """
        Plain text template without emojis (for Chrome/Selenium compatibility)
        """
        form_url = kwargs.get('form_url', os.getenv('GOOGLE_FORM_URL', 'https://forms.gle/your-form-id'))
        consultant_name = kwargs.get('consultant_name', os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava'))
        
        template = f"""Hello!

Thank you for contacting us about Thailand visa consultation services.

To provide you with the most accurate consultation, please fill out our quick assessment form:

{form_url}

This will help us:
- Understand your specific situation
- Provide personalized visa guidance
- Connect you with the right services

The form takes just 2-3 minutes to complete.

Best regards,
{consultant_name} - Thailand Visa Specialist"""
        
        return template.strip()
    
    def _get_enhanced_engagement_template(self, **kwargs) -> str:
        """
        Enhanced engagement template with better value proposition
        """
        form_url = kwargs.get('form_url', os.getenv('GOOGLE_FORM_URL', 'https://forms.gle/your-form-id'))
        consultant_name = kwargs.get('consultant_name', os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava'))
        
        template = f"""🇹🇭 Thailand Visa Consultation - {consultant_name} here!

Thank you for reaching out! I help people successfully obtain Thailand visas and navigate the immigration process.

📋 Quick Assessment Form (2-3 mins):
{form_url}

✅ What you'll get:
• Personalized visa strategy
• Document checklist tailored to you
• Timeline and cost breakdown
• Direct expert guidance

I'll review your information and provide specific recommendations within 24 hours.

Questions? Just reply to this message!

Best regards,
{consultant_name} - Thailand Visa Specialist 🇹🇭"""
        
        return template.strip()
    
    def _get_conversational_template(self, **kwargs) -> str:
        """
        Conversational template with friendly approach
        """
        form_url = kwargs.get('form_url', os.getenv('GOOGLE_FORM_URL', 'https://forms.gle/your-form-id'))
        consultant_name = kwargs.get('consultant_name', os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava'))
        
        template = f"""Hi there! 👋

Thanks for your message about Thailand visas! I'm {consultant_name}, and I specialize in helping people like you navigate Thailand's visa process successfully.

Before I can give you the best advice, I'd love to learn more about your specific situation:

📝 Quick form: {form_url}

Why this helps:
✅ Get advice tailored to YOUR situation
✅ Avoid common costly mistakes
✅ Fast-track your application process

Takes 2-3 minutes, and I'll personally review every response.

Looking forward to helping you with your Thailand journey!

{consultant_name} 🇹🇭"""
        
        return template.strip()
    
    def _get_conversion_focused_template(self, **kwargs) -> str:
        """
        Conversion-focused template with urgency and credibility
        """
        form_url = kwargs.get('form_url', os.getenv('GOOGLE_FORM_URL', 'https://forms.gle/your-form-id'))
        consultant_name = kwargs.get('consultant_name', os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava'))
        
        template = f"""🚨 THAILAND VISA CONSULTATION - Quick Response Needed!

Hi! {consultant_name} here - Thailand visa specialist with 500+ successful applications.

⏰ I have availability this week for new consultations, but spots fill quickly.

Secure your consultation slot:
👉 {form_url} (2-3 minutes)

✅ What's included:
• Free 30-min expert consultation
• Personalized visa strategy
• Document preparation guide
• Success rate: 98.5%

⚡ Priority review within 4 hours for completed forms.

Ready to make Thailand your new home?

{consultant_name} - Thailand Visa Expert 🇹🇭"""
        
        return template.strip()
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """
        Validate template for WhatsApp compatibility
        
        Args:
            template (str): Template to validate
            
        Returns:
            dict: Validation results
        """
        max_length = 4096  # WhatsApp message limit
        
        return {
            'valid': len(template) <= max_length,
            'length': len(template),
            'max_length': max_length,
            'length_percentage': (len(template) / max_length) * 100,
            'has_form_url': '{form_url}' in template or 'forms.gle' in template or 'docs.google.com/forms' in template
        }
    
    def get_available_templates(self) -> list:
        """Get list of available template types"""
        return list(self.templates.keys())

# Global template manager instance
template_manager = WhatsAppTemplateManager()

def get_auto_reply_template(template_type: str = None, **kwargs) -> str:
    """
    Convenience function to get auto-reply template
    
    Args:
        template_type (str): Template type
        **kwargs: Variables to inject
        
    Returns:
        str: Formatted template
    """
    return template_manager.get_auto_reply_template(template_type, **kwargs) 