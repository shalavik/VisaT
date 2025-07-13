#!/usr/bin/env python3
"""
Test Google Sheets Connection - Fixed Version
Tests the fixed sheets client that handles JWT issues
"""

import sys
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

def test_with_fixed_client():
    """Test Google Sheets connection with fixed client"""
    print("🔧 TESTING GOOGLE SHEETS - FIXED VERSION")
    print("=" * 60)
    
    try:
        from integrations.sheets_client_fixed import SheetsClientFixed
        
        print("📋 Step 1: Initializing Fixed Sheets Client...")
        client = SheetsClientFixed()
        
        if not client.service:
            print("❌ Failed to initialize service")
            return False
        
        print("✅ Service initialized successfully")
        
        print(f"\n📊 Step 2: Testing Connection...")
        connection_result = client.test_connection()
        
        if connection_result["status"] == "success":
            print("✅ Connection test PASSED!")
            print(f"   📄 Sheet Title: {connection_result['title']}")
            print(f"   📊 Sheet Count: {connection_result['sheet_count']}")
            print(f"   🆔 Spreadsheet ID: {connection_result['spreadsheet_id']}")
        else:
            print(f"❌ Connection test failed: {connection_result['error']}")
            return False
        
        print(f"\n📖 Step 3: Testing Header Reading...")
        headers = client.get_headers()
        
        if headers:
            print(f"✅ Headers retrieved successfully!")
            print(f"   📋 Column count: {len(headers)}")
            print(f"   📄 Headers: {headers[:6]}...")  # Show first 6 headers
        else:
            print("⚠️  No headers found (sheet might be empty)")
        
        print(f"\n📊 Step 4: Testing Data Reading...")
        data_rows = client.get_data_rows()
        
        if data_rows:
            print(f"✅ Data retrieved successfully!")
            print(f"   📊 Row count: {len(data_rows)}")
            print(f"   📄 Sample row: {data_rows[0][:4]}..." if data_rows else "No data")
        else:
            print("⚠️  No data rows found (only headers or empty sheet)")
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Google Sheets connection is working with fixed client")
        print("✅ Ready for form submission monitoring")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_original_vs_fixed():
    """Compare original client vs fixed client"""
    print("\n🔄 COMPARING ORIGINAL VS FIXED CLIENT")
    print("=" * 60)
    
    # Test original client
    print("📋 Testing Original Client...")
    try:
        from integrations.sheets_client import SheetsClient
        original_client = SheetsClient()
        
        if original_client.service:
            # Try to get data
            result = original_client.service.spreadsheets().get(
                spreadsheetId=original_client.spreadsheet_id
            ).execute()
            print("✅ Original client working")
        else:
            print("❌ Original client failed to initialize")
    except Exception as e:
        print(f"❌ Original client error: {e}")
    
    # Test fixed client
    print("\n📋 Testing Fixed Client...")
    try:
        from integrations.sheets_client_fixed import SheetsClientFixed
        fixed_client = SheetsClientFixed()
        
        connection_result = fixed_client.test_connection()
        if connection_result["status"] == "success":
            print("✅ Fixed client working")
        else:
            print(f"❌ Fixed client error: {connection_result['error']}")
    except Exception as e:
        print(f"❌ Fixed client error: {e}")

def simulate_monitoring():
    """Simulate the monitoring process"""
    print("\n🔍 SIMULATING MONITORING PROCESS")
    print("=" * 60)
    
    try:
        from integrations.sheets_client_fixed import SheetsClientFixed
        
        client = SheetsClientFixed()
        
        print("📊 Getting current data...")
        data_rows = client.get_data_rows()
        
        if data_rows:
            print(f"✅ Found {len(data_rows)} existing form submissions")
            
            # Show latest submissions
            print("\n📋 Latest Submissions:")
            for i, row in enumerate(data_rows[-3:]):  # Show last 3
                row_num = len(data_rows) - 2 + i
                timestamp = row[0] if len(row) > 0 else "No timestamp"
                name = row[1] if len(row) > 1 else "No name"
                email = row[2] if len(row) > 2 else "No email"
                print(f"   Row {row_num}: {timestamp} - {name} ({email})")
            
            print(f"\n🎯 Monitoring would process new rows starting from: {len(data_rows) + 1}")
            
        else:
            print("📄 No existing data found - monitoring will start from row 1")
        
        print("\n✅ Simulation complete - ready for real monitoring!")
        
    except Exception as e:
        print(f"❌ Simulation error: {e}")

if __name__ == "__main__":
    print("🚀 GOOGLE SHEETS CONNECTION TESTING")
    print("=" * 60)
    
    # Main test
    success = test_with_fixed_client()
    
    # Additional tests
    if success:
        test_original_vs_fixed()
        simulate_monitoring()
        
        print(f"\n🎉 FINAL RESULT: SUCCESS!")
        print("✅ Google Sheets monitoring is ready to use")
        print("✅ You can now test form submissions")
    else:
        print(f"\n❌ FINAL RESULT: FAILED")
        print("❌ Additional troubleshooting needed")
    
    sys.exit(0 if success else 1) 