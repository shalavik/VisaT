# 🔑 CREATE NEW SERVICE ACCOUNT KEY

## Problem
The current service account key is producing persistent JWT signature errors despite all authentication methods. This indicates the key itself is corrupted or invalid.

## ✅ SOLUTION: Generate Fresh Service Account Key

### Step 1: Access Google Cloud Console
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=visat-464403
2. Make sure you're in project: `visat-464403`

### Step 2: Find Existing Service Account
Look for: `sheet-access-visat@visat-464403.iam.gserviceaccount.com`

### Step 3: Generate New Key
1. Click on the service account email
2. Go to **"Keys"** tab
3. Click **"Add Key" → "Create New Key"**
4. Select **"JSON"** format
5. Click **"Create"**
6. Download the new key file (it will be named something like `visat-464403-xyz.json`)

### Step 4: Replace Current Key
```bash
# Backup current key
cp config/google_service_account.json config/google_service_account.json.backup

# Replace with new key
# Option 1: Rename downloaded file
mv ~/Downloads/visat-464403-*.json config/google_service_account.json

# Option 2: Copy new key content to existing file
# Open the downloaded key file and copy its contents
# Paste into config/google_service_account.json
```

### Step 5: Verify New Key Structure
```bash
# Check the new key has proper structure
python -c "
import json
with open('config/google_service_account.json', 'r') as f:
    data = json.load(f)
    print('✅ Key structure verification:')
    print(f'Project ID: {data.get(\"project_id\")}')
    print(f'Client Email: {data.get(\"client_email\")}')
    print(f'Key ID: {data.get(\"private_key_id\")}')
    print(f'Has private key: {\"private_key\" in data}')
"
```

### Step 6: Restart Flask App
```bash
# Stop Flask app (Ctrl+C in Flask terminal)
python app.py
```

### Step 7: Test New Key
```bash
# Start monitoring with new key
curl -X POST http://localhost:5002/api/sheets-monitor/start

# Test manual processing (should work without JWT errors)
curl -X POST http://localhost:5002/api/sheets-monitor/process

# Check status
curl http://localhost:5002/api/sheets-monitor/status
```

## Expected Result
- ✅ No JWT signature errors
- ✅ Google Sheets access working
- ✅ Background monitoring functional
- ✅ Form submissions processed automatically

## ⚠️ Important Notes
- The service account already has access to your Google Sheet (you shared it earlier)
- New key will use same service account email: `sheet-access-visat@visat-464403.iam.gserviceaccount.com`
- No need to reshare the Google Sheet

---

**Creating a fresh service account key should resolve the JWT signature issue! 🔑** 