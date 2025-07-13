# 🔧 Google Sheets Access Fix

## Problem
```
❌ ERROR: invalid_grant: Invalid JWT Signature
```

This error occurs when the Google service account doesn't have access to your Google Sheet.

## Solution Steps

### Step 1: Open Your Google Sheet
1. Go to your Google Form responses sheet: https://docs.google.com/spreadsheets/d/1ImWLfR4RJiZpmIFjPZw1mnqd6SarVnRn6C4ImpqYdQ4/edit
2. Click the **"Share"** button (top right)

### Step 2: Add Service Account Access
1. In the share dialog, add this email address:
   ```
   sheet-access-visat@visat-464403.iam.gserviceaccount.com
   ```
2. Set permission to **"Editor"**
3. **UNCHECK** "Notify people" (since it's a service account)
4. Click **"Share"**

### Step 3: Verify Access
After sharing, run this test:

```bash
# Test the connection
curl -X POST http://localhost:5002/api/sheets-monitor/process
```

## Expected Result
✅ **SUCCESS:** The system should now be able to read your Google Sheet and process form submissions automatically.

## What This Fixes
- Allows the service account to read form responses from your Google Sheet
- Enables automatic processing of new form submissions
- Restores email and WhatsApp follow-up functionality

## Next Steps
1. **Share the sheet** with the service account (steps above)
2. **Test a form submission** to verify the complete flow
3. **Monitor the logs** to see automatic processing in action

---

**Service Account Email (copy this):**
```
sheet-access-visat@visat-464403.iam.gserviceaccount.com
``` 