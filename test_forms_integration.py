#!/usr/bin/env python3
"""
Test Google Forms Integration
Test the complete flow from form submission to email + WhatsApp follow-up
"""

import sys
import os
sys.path.append('src')

from handlers.form_processor import FormProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_qualified_prospect():
    """Test processing a qualified prospect"""
    print("🧪 Testing qualified prospect flow...")
    
    # Sample qualified prospect data (Spanish citizen in Thailand with funds)
    test_data = {
        'Full Name': 'Maria Garcia',
        'Email Address': 'maria@example.com',
        'Nationality': 'Spain',
        'Current Country': 'Thailand',
        'Do you have more than 500k BTH in your bank account?': 'Yes',
        'WhatsApp Number (with country code)': '+34666123456'
    }
    
    processor = FormProcessor()
    result = processor.process_submission(test_data)
    
    print(f"📋 Processing Result:")
    print(f"   Status: {result.get('status')}")
    print(f"   Qualified: {result.get('qualified')}")
    print(f"   Qualification Reason: {result.get('qualification_reason')}")
    print(f"   Email Result: {result.get('email_result')}")
    print(f"   WhatsApp Result: {result.get('whatsapp_result')}")
    print(f"   Calendly Link: {result.get('calendly_link')}")
    
    return result

def test_unqualified_prospect():
    """Test processing an unqualified prospect"""
    print("\n🧪 Testing unqualified prospect flow...")
    
    # Sample unqualified prospect data (Afghanistan citizen - restricted)
    test_data = {
        'Full Name': 'Ahmad Khan',
        'Email Address': 'ahmad@example.com',
        'Nationality': 'Afghanistan',
        'Current Country': 'Afghanistan',
        'Do you have more than 500k BTH in your bank account?': 'Yes',
        'WhatsApp Number (with country code)': '+93701234567'
    }
    
    processor = FormProcessor()
    result = processor.process_submission(test_data)
    
    print(f"📋 Processing Result:")
    print(f"   Status: {result.get('status')}")
    print(f"   Qualified: {result.get('qualified')}")
    print(f"   Qualification Reason: {result.get('qualification_reason')}")
    print(f"   Email Result: {result.get('email_result')}")
    print(f"   WhatsApp Result: {result.get('whatsapp_result')}")
    print(f"   Calendly Link: {result.get('calendly_link')}")
    
    return result

def test_whatsapp_follow_up():
    """Test WhatsApp follow-up template generation"""
    print("\n🧪 Testing WhatsApp follow-up template...")
    
    from utils.whatsapp_templates import get_follow_up_template
    
    template = get_follow_up_template(
        name="Maria Garcia",
        calendly_link="https://calendly.com/slavaidler/30min",
        consultant_name="Slava"
    )
    
    print("📱 Follow-up Template:")
    print(template)
    
    return template

if __name__ == "__main__":
    print("🚀 STARTING GOOGLE FORMS INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Test 1: WhatsApp follow-up template
        test_whatsapp_follow_up()
        
        # Test 2: Qualified prospect
        qualified_result = test_qualified_prospect()
        
        # Test 3: Unqualified prospect
        unqualified_result = test_unqualified_prospect()
        
        print("\n✅ INTEGRATION TEST COMPLETE")
        print("=" * 50)
        
        # Summary
        print("\n📊 SUMMARY:")
        print(f"Qualified prospect processed: {qualified_result.get('status') == 'processed'}")
        print(f"Unqualified prospect processed: {unqualified_result.get('status') == 'processed'}")
        
        if qualified_result.get('qualified') and qualified_result.get('calendly_link'):
            print("✅ Qualified prospects get Calendly link")
        else:
            print("❌ Issue with qualified prospect handling")
            
        if not unqualified_result.get('qualified') and not unqualified_result.get('calendly_link'):
            print("✅ Unqualified prospects don't get Calendly link")
        else:
            print("❌ Issue with unqualified prospect handling")
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc() 