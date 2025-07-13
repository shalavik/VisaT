#!/usr/bin/env python3
"""
Test Google Sheets Access
Simple script to verify the service account can access your Google Sheet
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

def test_sheets_access():
    """Test Google Sheets access"""
    print("🧪 TESTING GOOGLE SHEETS ACCESS")
    print("=" * 50)
    
    try:
        from integrations.sheets_client import SheetsClient
        
        # Initialize client
        print("📋 Initializing Google Sheets client...")
        client = SheetsClient()
        
        if not client.service:
            print("❌ Failed to initialize Google Sheets service")
            return False
            
        print("✅ Google Sheets service initialized")
        print(f"📊 Spreadsheet ID: {client.spreadsheet_id}")
        
        # Test spreadsheet access
        print("\n🔍 Testing spreadsheet access...")
        try:
            spreadsheet = client.service.spreadsheets().get(
                spreadsheetId=client.spreadsheet_id
            ).execute()
            
            title = spreadsheet.get('properties', {}).get('title', 'Unknown')
            sheet_count = len(spreadsheet.get('sheets', []))
            
            print(f"✅ Spreadsheet accessible!")
            print(f"   Title: {title}")
            print(f"   Sheets: {sheet_count}")
            
        except Exception as e:
            print(f"❌ Spreadsheet access failed: {e}")
            print("\n💡 SOLUTION:")
            print("   1. Open your Google Sheet")
            print("   2. Click 'Share' button")
            print("   3. Add this email: sheet-access-visat@visat-464403.iam.gserviceaccount.com")
            print("   4. Set permission to 'Editor'")
            print("   5. Uncheck 'Notify people'")
            print("   6. Click 'Share'")
            return False
        
        # Test reading data
        print("\n📖 Testing data reading...")
        try:
            result = client.service.spreadsheets().values().get(
                spreadsheetId=client.spreadsheet_id,
                range='A1:Z1'  # Get header row
            ).execute()
            
            values = result.get('values', [])
            if values:
                print(f"✅ Data readable!")
                print(f"   Headers: {values[0][:5]}...")  # Show first 5 headers
            else:
                print("⚠️  Sheet appears empty (no headers found)")
                
        except Exception as e:
            print(f"❌ Data reading failed: {e}")
            return False
        
        # Test getting all data
        print("\n📊 Testing full data access...")
        try:
            result = client.service.spreadsheets().values().get(
                spreadsheetId=client.spreadsheet_id,
                range='A:Z'  # Get all data
            ).execute()
            
            values = result.get('values', [])
            row_count = len(values) - 1 if values else 0  # Subtract header
            
            print(f"✅ Full data access successful!")
            print(f"   Total rows (excluding header): {row_count}")
            
            if row_count > 0:
                print(f"   Sample row: {values[1][:3]}..." if len(values) > 1 else "")
            
        except Exception as e:
            print(f"❌ Full data access failed: {e}")
            return False
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Google Sheets access is working correctly")
        print("✅ Ready to monitor form submissions")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_sheets_access()
    sys.exit(0 if success else 1) 