#!/usr/bin/env python3
"""
Message Templates
Educational messaging templates for VisaT system
"""

def get_whatsapp_welcome_template(form_url):
    """
    Get WhatsApp welcome message template
    
    Args:
        form_url (str): Google Form URL
        
    Returns:
        str: Formatted welcome message
    """
    return f"""
🌟 Thank you for your interest in Thailand visa services!

To better assist you, please fill out our quick consultation form:

📋 {form_url}

This will help us:
✅ Understand your specific needs
✅ Pre-qualify your application
✅ Provide personalized guidance

Our visa experts will review your information and get back to you within 24 hours.

Best regards,
VisaT Team 🇹🇭
    """.strip()

def get_qualification_email_template(name, qualified=True, calendly_link=None):
    """
    Get email template for qualification results
    
    Args:
        name (str): Prospect name
        qualified (bool): Whether prospect is qualified
        calendly_link (str, optional): Calendly booking link
        
    Returns:
        dict: Email template with subject and body
    """
    if qualified:
        subject = "🎉 Great News! You're Pre-Qualified for Thailand Visa Consultation"
        
        body = f"""
Dear {name},

We're excited to inform you that based on your initial information, you appear to be an excellent candidate for Thailand visa services.

✅ Your Pre-Qualification Status: APPROVED

Your profile meets our initial criteria for Thailand visa consultation.

🗓️ Next Steps:
Schedule your FREE 30-minute consultation to discuss:
• Your specific visa options
• Required documentation
• Timeline and process
• Investment opportunities (if applicable)

{f'📅 Book Your Free Consultation: {calendly_link}' if calendly_link else 'We will contact you shortly to schedule your consultation.'}

Our Thailand visa experts are ready to help you navigate the process smoothly.

Best regards,
Slava
VisaT - Thailand Visa Specialists
📧 slavaidler@gmail.com
        """.strip()
        
    else:
        subject = "Thank You for Your Interest in Thailand Visa Services"
        
        body = f"""
Dear {name},

Thank you for your interest in Thailand visa services. We appreciate you taking the time to submit your information.

After reviewing your current situation, we believe you may benefit from exploring additional preparation options before proceeding with visa applications.

📚 Helpful Resources:
We recommend reviewing Thailand's official visa requirements and considering:
• Financial planning and documentation
• Understanding different visa categories
• Exploring alternative pathways

We encourage you to reach out again in the future when your circumstances may better align with Thailand's visa requirements.

Best regards,
Slava
VisaT - Thailand Visa Specialists
📧 slavaidler@gmail.com
        """.strip()
    
    return {
        "subject": subject,
        "body": body
    }

def get_whatsapp_follow_up_template(name, qualified=True):
    """
    Get WhatsApp follow-up message template
    
    Args:
        name (str): Prospect name
        qualified (bool): Whether prospect is qualified
        
    Returns:
        str: Follow-up message
    """
    if qualified:
        return f"""
🎉 Great news, {name}!

You've been pre-qualified for Thailand visa consultation! 

📧 Check your email for detailed next steps and booking information.

Our team is excited to help you with your Thailand journey! 🇹🇭

Best regards,
VisaT Team
        """.strip()
    else:
        return f"""
Hi {name},

Thank you for your interest in Thailand visa services.

📧 Please check your email for helpful resources and information about visa requirements.

Feel free to reach out when you're ready to explore Thailand visa options in the future.

Best regards,
VisaT Team 🇹🇭
        """.strip()

def get_educational_content_templates():
    """
    Get educational content templates for different scenarios
    
    Returns:
        dict: Educational content templates
    """
    return {
        "visa_types": {
            "title": "Thailand Visa Types Guide",
            "content": """
🇹🇭 THAILAND VISA TYPES OVERVIEW

1. Tourist Visa (TR)
   • Short-term visits (30-60 days)
   • Tourism and leisure purposes

2. Non-Immigrant Visa (Non-O)
   • Retirement, marriage, business
   • Long-term stays (90 days - 1 year)

3. Investment Visa (Non-B)
   • Business and investment purposes
   • Work permit eligible

4. Elite Visa
   • Premium long-term residence
   • 5-20 year options

Contact us for personalized guidance! 📞
            """
        },
        "financial_requirements": {
            "title": "Financial Requirements Guide",
            "content": """
💰 THAILAND VISA FINANCIAL REQUIREMENTS

General Requirements:
• Tourist Visa: 20,000 BTH proof of funds
• Non-O Retirement: 800,000 BTH bank deposit
• Investment Visa: Varies by investment type

Important Notes:
✅ Bank statements required (3-6 months)
✅ Funds must be seasoned (held for required period)
✅ Some visas require monthly income proof

Need help planning? We're here to assist! 🤝
            """
        },
        "documentation": {
            "title": "Required Documentation Guide",
            "content": """
📋 THAILAND VISA DOCUMENTATION

Standard Documents:
• Valid passport (6+ months validity)
• Completed visa application form
• Recent passport photos
• Bank statements
• Criminal background check

Additional Requirements:
• Medical certificate (some visas)
• Insurance documentation
• Proof of accommodation
• Flight itinerary

Let us help you prepare everything correctly! ✅
            """
        }
    }

def get_rejection_reasons_templates():
    """
    Get templates for different rejection reasons
    
    Returns:
        dict: Rejection reason templates
    """
    return {
        "blocked_nationality": {
            "email_message": "Unfortunately, we cannot process applications for your nationality at this time due to current regulations. We recommend consulting with the Thai embassy directly for the most up-to-date requirements.",
            "whatsapp_message": "Thank you for your interest. Due to current regulations, we recommend consulting directly with the Thai embassy for your nationality's specific requirements."
        },
        "insufficient_funds": {
            "email_message": "Thailand visa applications require specific financial documentation. We recommend reviewing the financial requirements and ensuring you meet the minimum thresholds before reapplying.",
            "whatsapp_message": "Thank you for your interest. Please review Thailand's financial requirements and feel free to reach out when you meet the minimum thresholds."
        },
        "invalid_visa_type": {
            "email_message": "For Thailand residents, specific visa documentation is required. We recommend consulting with immigration specialists familiar with in-country visa processes.",
            "whatsapp_message": "As a Thailand resident, you may need specialized assistance. We recommend consulting with local immigration specialists."
        }
    } 