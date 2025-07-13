# 🔄 ALTERNATIVE: Google Sheets API Key Solution

## If Service Account Key Still Fails

If creating a new service account key doesn't resolve the JWT issue, we can use an alternative approach with Google Sheets API key authentication.

## ✅ ALTERNATIVE SOLUTION: API Key Authentication

### Step 1: Enable Google Sheets API Key
1. Go to: https://console.cloud.google.com/apis/credentials?project=visat-464403
2. Click **"Create Credentials" → "API Key"**
3. Copy the generated API key
4. Click **"Restrict Key"** and select:
   - **API restrictions:** Google Sheets API
   - **Application restrictions:** None (or HTTP referrers if needed)
5. Save the key

### Step 2: Make Google Sheet Public (Read-Only)
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/19Y-BauO7RFP9gd6rV8Mf0O2QVzcPFdmCCWM3zq_7RdU/edit
2. Click **"Share"**
3. Click **"Change to anyone with the link"**
4. Set permission to **"Viewer"** (read-only)
5. Click **"Done"**

### Step 3: Add API Key to Environment
Add to your `.env` file:
```env
GOOGLE_SHEETS_API_KEY=your-api-key-here
```

### Step 4: Create API Key Sheets Client
I'll create a new client that uses API key instead of service account authentication.

### Step 5: Update Monitoring System
Update the sheets monitor to use the API key client instead of service account.

## 🔒 Security Considerations
- **Read-only access:** API key can only read the sheet, not modify it
- **Public sheet:** The sheet becomes publicly readable (but not editable)
- **API key restrictions:** Limited to Google Sheets API only

## ✅ Benefits
- **No JWT authentication issues**
- **Simpler authentication**
- **More reliable for read-only operations**
- **No service account management needed**

---

Would you like me to implement this API key solution as a backup plan? 