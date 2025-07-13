# Google Form Webhook Setup Guide

## Current Issue
You're filling out the Google Form but not receiving emails or WhatsApp messages because **the form is not connected to your server**.

## Required Setup Steps

### Step 1: Open Your Google Form
1. Go to your Google Form (the one with Thailand visa questions)
2. Click **"Extensions"** in the top menu
3. Click **"Apps Script"**

### Step 2: Add the Webhook Code
1. **Delete all existing code** in the Apps Script editor
2. **Copy and paste** the entire content from `google_apps_script_webhook.js`
3. **Save the script** (Ctrl+S or Cmd+S)

### Step 3: Configure the Webhook URL
In the script, find this line:
```javascript
const WEBHOOK_URL = 'http://localhost:5002/webhook/forms';
```

**For local testing:** Keep it as is  
**For production:** Change to your public server URL

### Step 4: Install the Trigger
1. In Apps Script, select **`setupTrigger`** from the function dropdown
2. Click the **"Run"** button ▶️
3. **Authorize the script** when Google asks for permissions
4. You should see: "✅ Form submission trigger installed successfully"

### Step 5: Test the Connection
1. In Apps Script, select **`testWebhookConnection`** from the function dropdown
2. Click **"Run"** ▶️
3. Check the execution log - you should see "✅ Webhook test successful!"

## Verification Checklist

✅ **Apps Script Added**: Code from `google_apps_script_webhook.js` is in your form  
✅ **Trigger Installed**: `setupTrigger()` ran successfully  
✅ **Connection Tested**: `testWebhookConnection()` shows success  
✅ **Application Running**: Your Flask app is running on port 5002  

## Expected Behavior After Setup

1. **Fill out Google Form** → Apps Script sends data to webhook
2. **Server processes** → Qualification engine evaluates prospect
3. **If qualified** → Email + WhatsApp with Calendly link sent
4. **If unqualified** → Email only sent

## Troubleshooting

### If testWebhookConnection() Fails:
- Check if your Flask app is running (`python app.py`)
- Verify the WEBHOOK_URL matches your server
- For local testing, use: `http://localhost:5002/webhook/forms`

### If No Emails/WhatsApp After Form Submission:
- Check Apps Script execution log for errors
- Verify the trigger is installed
- Check your Flask app terminal for webhook logs

### If WhatsApp Follow-up Fails:
- Make sure your WhatsApp number is in international format: `+34666123456`
- Check that the contact exists on WhatsApp

## Manual Test Commands

Test the webhook directly:
```bash
curl -X POST http://localhost:5002/webhook/forms \
  -H "Content-Type: application/json" \
  -d '{
    "Full Name": "Test User",
    "Email Address": "test@example.com",
    "Nationality": "Spain",
    "Current Country": "Thailand",
    "Do you have more than 500k BTH in your bank account?": "Yes",
    "WhatsApp Number (with country code)": "+34666123456"
  }'
```

## Common Google Apps Script Permissions

When you run `setupTrigger()`, Google will ask for permissions:
- **View and manage forms** - Required to detect form submissions
- **Connect to external service** - Required to send data to your webhook
- **Send email** - For error notifications (optional)

**Grant all permissions** for the integration to work properly.

## Success Indicators

After completing setup, when you fill out the form:
1. **Apps Script Log**: Shows "✅ Successfully sent form data to webhook"
2. **Flask Terminal**: Shows "Forms webhook received: {your form data}"
3. **Email Received**: Welcome email in your inbox
4. **WhatsApp Received**: Follow-up message with Calendly link (if qualified)

## Next Steps

1. Complete the setup above
2. Fill out your form with qualified information
3. Check your email and WhatsApp for messages
4. If still not working, check the Apps Script execution log for error details 