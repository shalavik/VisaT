#!/usr/bin/env python3
"""
Webhook Setup Verification Script
Run this to verify your Google Forms webhook integration is working
"""

import requests
import json
import time
import sys

WEBHOOK_URL = "http://localhost:5002/webhook/forms"

def test_webhook_endpoint():
    """Test if the webhook endpoint is responding"""
    print("🧪 Testing webhook endpoint accessibility...")
    
    try:
        response = requests.post(WEBHOOK_URL, 
                               json={"test": "connectivity"}, 
                               timeout=5)
        print(f"✅ Webhook endpoint is accessible (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Webhook endpoint not accessible - is the application running?")
        print("   Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def test_qualified_submission():
    """Test a qualified prospect submission"""
    print("\n🧪 Testing qualified prospect webhook...")
    
    qualified_data = {
        "Full Name": "Maria Garcia",
        "Email Address": "maria.test@example.com",
        "Nationality": "Spain",
        "Current Country": "Thailand", 
        "Do you have more than 500k BTH in your bank account?": "Yes",
        "WhatsApp Number (with country code)": "+34666123456",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "form_title": "Thailand Visa Consultation - Qualification Form",
        "test_mode": True
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=qualified_data, timeout=10)
        result = response.json()
        
        print(f"✅ Webhook processed successfully (Status: {response.status_code})")
        print(f"   Prospect: {result.get('result', {}).get('prospect_email')}")
        print(f"   Qualified: {result.get('result', {}).get('qualified')}")
        print(f"   Email Status: {result.get('result', {}).get('email_result', {}).get('status')}")
        print(f"   WhatsApp Status: {result.get('result', {}).get('whatsapp_result', {}).get('status')}")
        print(f"   Calendly Link: {result.get('result', {}).get('calendly_link')}")
        
        return result.get('result', {}).get('qualified') == True
        
    except Exception as e:
        print(f"❌ Qualified prospect test failed: {e}")
        return False

def test_unqualified_submission():
    """Test an unqualified prospect submission"""
    print("\n🧪 Testing unqualified prospect webhook...")
    
    unqualified_data = {
        "Full Name": "Ahmad Khan",
        "Email Address": "ahmad.test@example.com", 
        "Nationality": "Afghanistan",
        "Current Country": "Afghanistan",
        "Do you have more than 500k BTH in your bank account?": "Yes",
        "WhatsApp Number (with country code)": "+93701234567",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "form_title": "Thailand Visa Consultation - Qualification Form",
        "test_mode": True
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=unqualified_data, timeout=10)
        result = response.json()
        
        print(f"✅ Webhook processed successfully (Status: {response.status_code})")
        print(f"   Prospect: {result.get('result', {}).get('prospect_email')}")
        print(f"   Qualified: {result.get('result', {}).get('qualified')}")
        print(f"   Email Status: {result.get('result', {}).get('email_result', {}).get('status')}")
        print(f"   WhatsApp Status: {result.get('result', {}).get('whatsapp_result', {}).get('status')}")
        print(f"   Calendly Link: {result.get('result', {}).get('calendly_link')}")
        
        return result.get('result', {}).get('qualified') == False
        
    except Exception as e:
        print(f"❌ Unqualified prospect test failed: {e}")
        return False

def monitor_webhook_activity():
    """Monitor for incoming webhook requests"""
    print("\n👀 Monitoring webhook activity...")
    print("   Fill out your Google Form now to see if data comes through...")
    print("   Press Ctrl+C to stop monitoring\n")
    
    try:
        import subprocess
        import signal
        
        # Monitor application logs for webhook activity
        process = subprocess.Popen(
            ['tail', '-f', '/dev/null'],  # Placeholder - in real scenario would tail log files
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for form submissions...")
        print("   (This is a placeholder - check your application terminal for actual webhook logs)")
        
        time.sleep(30)  # Wait 30 seconds for form submissions
        process.terminate()
        
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped")

def main():
    """Run all verification tests"""
    print("🚀 GOOGLE FORMS WEBHOOK VERIFICATION")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    if not test_webhook_endpoint():
        print("\n❌ FAILED: Webhook endpoint not accessible")
        print("   Solution: Make sure 'python app.py' is running")
        sys.exit(1)
    
    # Test 2: Qualified prospect processing
    qualified_success = test_qualified_submission()
    
    # Test 3: Unqualified prospect processing  
    unqualified_success = test_unqualified_submission()
    
    # Results
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS:")
    print(f"✅ Webhook endpoint accessible: ✓")
    print(f"✅ Qualified prospect processing: {'✓' if qualified_success else '❌'}")
    print(f"✅ Unqualified prospect processing: {'✓' if unqualified_success else '❌'}")
    
    if qualified_success and unqualified_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 NEXT STEPS:")
        print("1. Add the Google Apps Script to your Google Form")
        print("2. Run setupTrigger() in Apps Script") 
        print("3. Fill out your form with qualified data")
        print("4. Check for email and WhatsApp messages")
    else:
        print("\n❌ SOME TESTS FAILED - Check the errors above")
        
    # Optional monitoring
    user_input = input("\n❓ Monitor for live form submissions? (y/n): ")
    if user_input.lower() == 'y':
        monitor_webhook_activity()

if __name__ == "__main__":
    main() 