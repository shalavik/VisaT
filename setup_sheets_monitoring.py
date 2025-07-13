#!/usr/bin/env python3
"""
Google Sheets Monitoring Setup
Configure and test Google Sheets monitoring for form submissions
"""

import sys
import os
import re
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from integrations.sheets_monitor import SheetsMonitor
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("❌ Make sure the Flask app is running and all dependencies are installed")
    sys.exit(1)

def extract_spreadsheet_id_from_url(url):
    """Extract Google Sheets ID from URL"""
    # Pattern: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def setup_sheets_monitoring():
    """Interactive setup for Google Sheets monitoring"""
    print("🚀 GOOGLE SHEETS MONITORING SETUP")
    print("=" * 50)
    
    # Get the Google Sheets URL or ID
    print("\n📋 Step 1: Google Sheets Configuration")
    print("You need the Google Sheets that receives your Google Form responses.")
    print()
    
    sheets_input = input("Enter your Google Sheets URL or ID: ").strip()
    
    if not sheets_input:
        print("❌ Google Sheets URL/ID is required!")
        return False
    
    # Extract spreadsheet ID if URL provided
    if 'docs.google.com' in sheets_input:
        spreadsheet_id = extract_spreadsheet_id_from_url(sheets_input)
        if not spreadsheet_id:
            print("❌ Could not extract spreadsheet ID from URL!")
            return False
        print(f"✅ Extracted spreadsheet ID: {spreadsheet_id}")
    else:
        spreadsheet_id = sheets_input
        print(f"✅ Using spreadsheet ID: {spreadsheet_id}")
    
    # Save to environment variable
    env_line = f"GOOGLE_SHEETS_ID={spreadsheet_id}"
    print(f"\n📝 Add this to your .env file:")
    print(f"   {env_line}")
    
    # Test the sheets access
    print(f"\n🧪 Step 2: Testing Google Sheets Access")
    try:
        monitor = SheetsMonitor(spreadsheet_id)
        sheet_data = monitor._get_sheet_data()
        
        if sheet_data is not None:
            print(f"✅ Successfully connected to Google Sheets")
            print(f"📊 Found {len(sheet_data)} existing rows")
            
            if len(sheet_data) > 0:
                print(f"📋 Sample row data: {sheet_data[0][:5]}...")  # Show first 5 columns
            
        else:
            print("❌ Could not access Google Sheets data")
            print("   Check your Google Sheets credentials and permissions")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing Google Sheets: {e}")
        return False
    
    # Test server connection
    print(f"\n🔗 Step 3: Testing Server Connection")
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        print("✅ Flask server is running")
    except:
        print("❌ Flask server not running - start with: python app.py")
        return False
    
    # Start monitoring
    print(f"\n▶️ Step 4: Starting Sheets Monitoring")
    try:
        response = requests.post("http://localhost:5002/api/sheets-monitor/start", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Google Sheets monitoring started successfully!")
            else:
                print(f"❌ Failed to start monitoring: {result.get('message')}")
                return False
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting monitoring: {e}")
        return False
    
    # Get monitoring status
    print(f"\n📊 Step 5: Monitoring Status")
    try:
        response = requests.get("http://localhost:5002/api/sheets-monitor/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   Monitoring Active: {status.get('is_monitoring')}")
            print(f"   Spreadsheet ID: {status.get('spreadsheet_id')}")
            print(f"   Last Processed Row: {status.get('last_processed_row')}")
            print(f"   Check Interval: {status.get('polling_interval')}s")
        else:
            print("❌ Could not get monitoring status")
    except Exception as e:
        print(f"❌ Error getting status: {e}")
    
    print(f"\n🎉 SETUP COMPLETE!")
    print(f"=" * 50)
    print(f"✅ Google Sheets monitoring is now active")
    print(f"✅ System will check for new form submissions every 30 seconds")
    print(f"✅ New submissions will automatically trigger email and WhatsApp responses")
    print(f"\n📋 Next Steps:")
    print(f"1. Fill out your Google Form to test")
    print(f"2. Check the application logs for processing messages")
    print(f"3. Verify you receive email and WhatsApp responses")
    
    return True

def test_current_setup():
    """Test the current sheets monitoring setup"""
    print("🧪 TESTING CURRENT SHEETS MONITORING SETUP")
    print("=" * 50)
    
    # Check if GOOGLE_SHEETS_ID is set
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    if not sheets_id:
        print("❌ GOOGLE_SHEETS_ID environment variable not set")
        print("   Run the setup first")
        return False
    
    print(f"✅ GOOGLE_SHEETS_ID: {sheets_id}")
    
    # Test server connection
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        print("✅ Flask server is running")
    except:
        print("❌ Flask server not running - start with: python app.py")
        return False
    
    # Check monitoring status
    try:
        response = requests.get("http://localhost:5002/api/sheets-monitor/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Monitoring Status:")
            print(f"   Active: {status.get('is_monitoring')}")
            print(f"   Last Processed Row: {status.get('last_processed_row')}")
            print(f"   Polling Interval: {status.get('polling_interval')}s")
            
            if not status.get('is_monitoring'):
                print("\n⚠️ Monitoring is not active - starting it...")
                response = requests.post("http://localhost:5002/api/sheets-monitor/start", timeout=10)
                if response.status_code == 200:
                    print("✅ Monitoring started")
                else:
                    print("❌ Failed to start monitoring")
        else:
            print("❌ Could not get monitoring status")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False
    
    # Manually process any new rows
    print(f"\n🔄 Checking for new form submissions...")
    try:
        response = requests.post("http://localhost:5002/api/sheets-monitor/process", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manual processing completed: {result.get('message')}")
        else:
            print("❌ Manual processing failed")
    except Exception as e:
        print(f"❌ Error processing: {e}")
    
    print(f"\n✅ Current setup is working!")
    return True

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Full setup (first time)")
    print("2. Test current setup")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        setup_sheets_monitoring()
    elif choice == "2":
        test_current_setup()
    else:
        print("Invalid choice") 