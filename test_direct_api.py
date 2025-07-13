#!/usr/bin/env python3
"""
Test Google Sheets via Flask App
Test if the Flask app can access Google Sheets successfully
"""

import requests
import json
import time

def test_flask_app_access():
    """Test Google Sheets access through Flask app"""
    print("🧪 TESTING GOOGLE SHEETS VIA FLASK APP")
    print("=" * 50)
    
    base_url = "http://localhost:5002"
    
    # Check if app is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print("✅ Flask app is running")
    except:
        print("❌ Flask app not running - start with: python app.py")
        return False
    
    # Test sheets monitor status
    print("\n📊 Testing Sheets Monitor Status...")
    try:
        response = requests.get(f"{base_url}/api/sheets-monitor/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print("✅ Sheets monitor API accessible")
            print(f"   Monitoring: {status.get('is_monitoring')}")
            print(f"   Spreadsheet ID: {status.get('spreadsheet_id')}")
            print(f"   Last processed row: {status.get('last_processed_row')}")
        else:
            print(f"❌ Status request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status request error: {e}")
        return False
    
    # Test manual processing to see actual error
    print("\n🔍 Testing Manual Processing...")
    try:
        response = requests.post(f"{base_url}/api/sheets-monitor/process", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Processing request completed")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('status') == 'success':
                print("🎉 Google Sheets access is working!")
                return True
            else:
                print(f"⚠️  Processing status: {result.get('status')}")
                return False
        else:
            print(f"❌ Processing request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Processing request error: {e}")
        return False

def test_alternative_auth():
    """Test if we can use alternative authentication"""
    print("\n🔄 TESTING ALTERNATIVE AUTHENTICATION")
    print("=" * 50)
    
    # Check if we have Gmail working (uses same service account)
    print("📧 Testing Gmail integration...")
    try:
        test_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "nationality": "Thailand"
        }
        
        response = requests.post(
            "http://localhost:5002/api/test-email",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Gmail integration accessible")
        else:
            print(f"⚠️  Gmail test: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Gmail test error: {e}")

def get_detailed_logs():
    """Check the app logs for detailed error information"""
    print("\n📋 CHECKING APPLICATION LOGS")
    print("=" * 50)
    
    print("💡 To see detailed error logs, check the Flask app console output")
    print("💡 Look for any Google Sheets related errors")
    print("💡 Common JWT signature issues are caused by:")
    print("   - System time incorrect (most common)")
    print("   - Service account key expired")
    print("   - Missing scopes in service account")
    
    # Try to trigger an error to see it in logs
    print("\n🔍 Triggering sheets access to see error logs...")
    try:
        requests.post("http://localhost:5002/api/sheets-monitor/process", timeout=5)
        print("✅ Request sent - check Flask app logs for detailed error")
    except:
        print("⚠️  Request failed")

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE GOOGLE SHEETS TESTING")
    print("=" * 50)
    
    # Test through Flask app
    flask_success = test_flask_app_access()
    
    # Test alternative authentication
    test_alternative_auth()
    
    # Get detailed logs
    get_detailed_logs()
    
    if flask_success:
        print(f"\n🎉 SUCCESS: Google Sheets working via Flask app!")
    else:
        print(f"\n⚠️  ISSUE: Need to resolve authentication problem")
        print("\n💡 SOLUTIONS TO TRY:")
        print("1. 🕐 Fix system time (most likely cause)")
        print("2. 🔑 Regenerate Google service account key")
        print("3. 📋 Verify service account permissions")
        print("4. 🔄 Try alternative authentication method") 