#!/usr/bin/env python3
"""
Direct Webhook Test
Test the webhook endpoint with your actual contact information
"""

import requests
import json
import sys

def test_webhook_with_your_info():
    """Test webhook with qualified prospect data"""
    
    # Get your contact information
    print("🧪 TESTING WEBHOOK WITH YOUR INFORMATION")
    print("=" * 50)
    
    your_email = input("Enter your email address: ").strip()
    your_whatsapp = input("Enter your WhatsApp number (with country code, e.g., +1234567890): ").strip()
    your_name = input("Enter your name: ").strip()
    
    if not your_email or not your_whatsapp or not your_name:
        print("❌ All fields are required!")
        return False
    
    # Test data (qualified prospect)
    test_data = {
        "Full Name": your_name,
        "Email Address": your_email,
        "Nationality": "Spain",  # Qualified nationality
        "Current Country": "Thailand", 
        "Do you have more than 500k BTH in your bank account?": "Yes",  # Qualified financially
        "WhatsApp Number (with country code)": your_whatsapp,
        "timestamp": "2025-01-10 20:30:00",
        "form_title": "Thailand Visa Consultation - Qualification Form",
        "direct_test": True
    }
    
    print(f"\n🚀 Sending test submission to webhook...")
    print(f"📧 Email: {your_email}")
    print(f"📱 WhatsApp: {your_whatsapp}")
    print(f"👤 Name: {your_name}")
    
    try:
        response = requests.post(
            "http://localhost:5002/webhook/forms",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ WEBHOOK PROCESSED SUCCESSFULLY!")
            print(f"Status: {result.get('status')}")
            
            form_result = result.get('result', {})
            print(f"\n📊 PROCESSING RESULTS:")
            print(f"   Prospect: {form_result.get('prospect_email')}")
            print(f"   Qualified: {form_result.get('qualified')}")
            print(f"   Qualification Reason: {form_result.get('qualification_reason')}")
            
            email_result = form_result.get('email_result', {})
            print(f"\n📧 EMAIL RESULT:")
            print(f"   Status: {email_result.get('status')}")
            print(f"   Subject: {email_result.get('subject', 'N/A')}")
            
            whatsapp_result = form_result.get('whatsapp_result', {})
            print(f"\n📱 WHATSAPP RESULT:")
            print(f"   Status: {whatsapp_result.get('status')}")
            print(f"   Details: {whatsapp_result}")
            
            calendly_link = form_result.get('calendly_link')
            if calendly_link:
                print(f"\n🗓️ CALENDLY LINK: {calendly_link}")
            
            # Check what should happen
            if form_result.get('qualified'):
                print(f"\n🎉 YOU ARE QUALIFIED!")
                print(f"   ✅ Check your email for welcome message")
                print(f"   ✅ Check your WhatsApp for follow-up message with Calendly link")
            else:
                print(f"\n📋 You were not qualified for this test")
                print(f"   ✅ Check your email for alternative resources")
            
            return True
            
        else:
            print(f"❌ WEBHOOK FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION FAILED: Is the Flask app running?")
        print(f"   Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        return False

def test_server_status():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        print("✅ Server is running")
        return True
    except:
        print("❌ Server is not running - start with: python app.py")
        return False

if __name__ == "__main__":
    print("🔍 Checking server status...")
    if not test_server_status():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("This will test the webhook directly with your contact info")
    print("You should receive email and WhatsApp messages if qualified")
    print("="*50)
    
    proceed = input("\nProceed with test? (y/n): ").lower()
    if proceed == 'y':
        success = test_webhook_with_your_info()
        if success:
            print(f"\n🎯 TEST COMPLETED!")
            print(f"   If you didn't receive messages, check the logs above for errors")
        else:
            print(f"\n❌ TEST FAILED!")
    else:
        print("Test cancelled") 