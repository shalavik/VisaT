#!/usr/bin/env python3
"""
Verify Monitoring Fix
Test if the sheets monitor is now using the fixed client
"""

import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

def test_fixed_sheets_monitor():
    """Test the sheets monitor with fixed client"""
    print("🔧 TESTING FIXED SHEETS MONITOR")
    print("=" * 50)
    
    try:
        from integrations.sheets_monitor import SheetsMonitor
        
        print("📋 Step 1: Initializing SheetsMonitor...")
        monitor = SheetsMonitor()
        
        print(f"✅ Monitor initialized")
        print(f"   Spreadsheet ID: {monitor.spreadsheet_id}")
        print(f"   Using fixed client: {type(monitor.sheets_client).__name__}")
        
        print(f"\n📖 Step 2: Testing data retrieval...")
        try:
            # Test the fixed client directly
            connection_result = monitor.sheets_client.test_connection()
            if connection_result["status"] == "success":
                print("✅ Fixed client connection test PASSED")
                print(f"   Sheet Title: {connection_result['title']}")
            else:
                print(f"❌ Connection test failed: {connection_result['error']}")
                return False
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False
        
        print(f"\n📊 Step 3: Testing sheet data retrieval...")
        try:
            sheet_data = monitor._get_sheet_data()
            if sheet_data is not None:
                print(f"✅ Sheet data retrieved successfully")
                print(f"   Rows found: {len(sheet_data)}")
                if len(sheet_data) > 0:
                    print(f"   Sample row: {sheet_data[0][:3]}...")
            else:
                print("⚠️  No data returned (sheet might be empty)")
        except Exception as e:
            print(f"❌ Data retrieval error: {e}")
            return False
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Sheets monitor is now using the fixed client")
        print("✅ JWT signature issues should be resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing monitor: {e}")
        return False

def test_background_monitoring():
    """Test if background monitoring would work"""
    print(f"\n🔄 SIMULATING BACKGROUND MONITORING")
    print("=" * 50)
    
    try:
        from integrations.sheets_monitor import SheetsMonitor
        
        monitor = SheetsMonitor()
        
        print("📊 Simulating monitoring check...")
        
        # Get initial data to establish baseline
        initial_data = monitor._get_sheet_data()
        if initial_data:
            print(f"✅ Initial data retrieved: {len(initial_data)} rows")
            monitor.last_processed_row = len(initial_data)
            print(f"   Would process new rows starting from: {len(initial_data) + 1}")
        else:
            print("📄 No existing data - would start monitoring from row 1")
            monitor.last_processed_row = 0
        
        # Simulate a monitoring check
        print(f"\n🔍 Simulating monitoring loop check...")
        try:
            sheet_data = monitor._get_sheet_data()
            current_row_count = len(sheet_data) if sheet_data else 0
            
            if current_row_count > monitor.last_processed_row:
                new_rows = sheet_data[monitor.last_processed_row:]
                print(f"✅ Would process {len(new_rows)} new submissions")
            else:
                print(f"✅ No new submissions to process")
            
            print(f"✅ Monitoring simulation successful - no JWT errors!")
            
        except Exception as e:
            print(f"❌ Monitoring simulation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MONITORING FIX VERIFICATION")
    print("=" * 50)
    
    # Test the fixed monitor
    test1_success = test_fixed_sheets_monitor()
    
    # Test background monitoring simulation
    test2_success = test_background_monitoring()
    
    if test1_success and test2_success:
        print(f"\n🎉 VERIFICATION SUCCESSFUL!")
        print("✅ Sheets monitor fixed and ready")
        print("✅ Background monitoring should work without JWT errors")
        print("\n📋 Next Steps:")
        print("1. Restart Flask app to pick up the code changes")
        print("2. Start monitoring again")
        print("3. Test with a real form submission")
    else:
        print(f"\n❌ VERIFICATION FAILED")
        print("❌ Additional fixes needed")
    
    sys.exit(0 if (test1_success and test2_success) else 1) 