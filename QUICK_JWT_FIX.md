# 🔧 QUICK JWT SIGNATURE FIX

## Problem
```
❌ ERROR: invalid_grant: Invalid JWT Signature
```

The issue is likely **system time** showing 2025 instead of 2024, causing JWT validation to fail.

## 🚀 QUICK SOLUTION: Generate New Service Account Key

### Step 1: Create New Service Account Key
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=visat-464403
2. Find service account: `sheet-access-visat@visat-464403.iam.gserviceaccount.com`
3. Click **"Actions" → "Manage Keys"**
4. Click **"Add Key" → "Create New Key"**
5. Choose **"JSON"** format
6. Download the new key file

### Step 2: Replace Service Account File
1. **Backup current file:**
   ```bash
   cp config/google_service_account.json config/google_service_account.json.backup
   ```

2. **Replace with new key:**
   - Replace `config/google_service_account.json` with the newly downloaded file
   - Make sure the JSON structure looks similar to the current one

### Step 3: Test the Fix
```bash
# Test the new key
python test_direct_api.py

# If successful, test monitoring
curl -X POST http://localhost:5002/api/sheets-monitor/process
```

## 🕐 ALTERNATIVE: Fix System Time (macOS)

If you can fix the system time issue:
```bash
# Check current time
date

# If showing 2025, synchronize with network time
sudo sntp -sS time.apple.com
```

## ✅ Expected Result

After fixing either the service account key or system time:
- ✅ JWT signature validation passes
- ✅ Google Sheets access works
- ✅ Form monitoring becomes operational

## 🧪 Quick Test Commands

```bash
# Test 1: Check if Flask app can connect
python test_direct_api.py

# Test 2: Manual processing test
curl -X POST http://localhost:5002/api/sheets-monitor/process

# Test 3: Check monitoring status
curl http://localhost:5002/api/sheets-monitor/status
```

---

**Note:** The service account email `sheet-access-visat@visat-464403.iam.gserviceaccount.com` already has access to your Google Sheet, so you just need a working key file. 