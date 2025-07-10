#!/usr/bin/env python3
"""
Debug Environment Variables
Check if WhatsApp token is loading correctly
"""

import os
from dotenv import load_dotenv

print("=== Environment Debug ===")

# Check if .env file exists
env_file_exists = os.path.exists('.env')
print(f"1. .env file exists: {env_file_exists}")

# Load environment variables
print("2. Loading environment variables...")
load_dotenv()

# Check WhatsApp token
token = os.getenv('WHATSAPP_ACCESS_TOKEN')
print(f"3. Token loaded: {bool(token)}")
print(f"4. Token length: {len(token) if token else 0}")

if token:
    print(f"5. Token first 20 chars: {token[:20]}...")
    print(f"6. Token last 20 chars: ...{token[-20:]}")
    
    # Check if it's the old expired token
    if "EAAKyRmvSL70BO" in token and len(token) > 100:
        print("7. ⚠️  This appears to be a valid format token")
    else:
        print("7. ❌ Token format seems incorrect")
else:
    print("5. ❌ No token found!")

# Check other WhatsApp env vars
phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')

print(f"8. Phone Number ID: {phone_id}")
print(f"9. Verify Token: {verify_token}")

# Test the WhatsApp client
try:
    from src.integrations.whatsapp_client import WhatsAppClient
    client = WhatsAppClient()
    fresh_token = client._get_access_token()
    print(f"10. Fresh token from client: {bool(fresh_token)}")
    print(f"11. Fresh token matches: {fresh_token == token}")
except Exception as e:
    print(f"10. Error testing client: {e}")

print("=== End Debug ===") 