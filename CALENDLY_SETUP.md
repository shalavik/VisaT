# Calendly Webhook Integration Setup Guide

## Overview

This guide will help you set up the Calendly webhook integration to automatically track appointment bookings in your Google Sheets.

## Prerequisites

1. **Calendly Account**: Professional plan or higher (required for webhooks)
2. **Google Sheets**: Existing sheet for booking tracking
3. **VisaT System**: Running Flask application
4. **ngrok or Public URL**: For webhook endpoint access

## Step 1: Get Calendly Personal Access Token (PAT)

1. Log into your Calendly account
2. Go to **Integrations & Apps** → **API & Webhooks**
3. Click **Generate New Token**
4. Copy the Personal Access Token
5. Add to your `.env` file:
   ```bash
   CALENDLY_PAT=your_personal_access_token_here
   ```

## Step 2: Create Google Sheet for Bookings

1. Create a new Google Sheet or use existing one
2. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
   ```
3. Add to your `.env` file:
   ```bash
   CALENDLY_SHEET_ID=your_sheet_id_here
   ```

## Step 3: Set Up Webhook Endpoint

### Option A: Using ngrok (for testing)
```bash
# Install ngrok if not already installed
# Start your Flask app
python app.py

# In another terminal, expose port 5000
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Option B: Production deployment
Deploy your Flask app to a service with a public HTTPS URL.

## Step 4: Create Calendly Webhook

1. Go to Calendly **Integrations & Apps** → **API & Webhooks**
2. Click **Create Webhook**
3. Configure webhook:
   - **Endpoint URL**: `https://your-domain.com/api/calendly/webhook`
   - **Events**: Select `invitee.created` and `invitee.canceled`
   - **Signing Key**: Copy this key for verification
4. Save the webhook
5. Add the signing key to your `.env` file:
   ```bash
   CALENDLY_WEBHOOK_SECRET=your_webhook_signing_key_here
   ```

## Step 5: Environment Variables

Add these variables to your `.env` file:

```bash
# Calendly Integration
CALENDLY_PAT=your_calendly_personal_access_token_here
CALENDLY_WEBHOOK_SECRET=your_calendly_webhook_secret_here
CALENDLY_SHEET_ID=your_google_sheet_id_for_calendly_bookings_here
TZ_DEFAULT=Asia/Bangkok
```

## Step 6: Initialize Sheet Headers

1. Start your Flask application:
   ```bash
   python app.py
   ```

2. Create the sheet headers:
   ```bash
   curl -X POST http://localhost:5000/api/calendly/setup-headers
   ```

   This will create the following columns in your sheet:
   - Timestamp
   - Invitee Name
   - Invitee Email
   - Event Type
   - Start Time (UTC)
   - End Time (UTC)
   - Start Time (Thai)
   - End Time (Thai)
   - Timezone
   - Status
   - Calendly Event ID

## Step 7: Test the Integration

### Test API Connection
```bash
curl http://localhost:5000/api/calendly/status
```

### Test Webhook Processing
```bash
curl -X POST http://localhost:5000/api/calendly/test \
  -H "Content-Type: application/json" \
  -d '{
    "event": "invitee.created",
    "payload": {
      "name": "Test User",
      "email": "test@example.com",
      "event": "https://api.calendly.com/scheduled_events/test-123"
    }
  }'
```

### View Recent Bookings
```bash
curl http://localhost:5000/api/calendly/bookings
```

## Step 8: Verify Webhook Reception

1. Book a test appointment in Calendly
2. Check your Flask application logs for webhook processing
3. Verify the booking appears in your Google Sheet
4. Check that times are correctly converted to Thai timezone

## Troubleshooting

### Common Issues

1. **Webhook not received**
   - Check that your endpoint is publicly accessible
   - Verify the webhook URL in Calendly settings
   - Check Flask application logs

2. **Signature verification failed**
   - Ensure `CALENDLY_WEBHOOK_SECRET` matches the signing key
   - Check that the secret is correctly set in environment

3. **API connection failed**
   - Verify `CALENDLY_PAT` is correct and active
   - Check internet connectivity
   - Ensure PAT has required permissions

4. **Sheet update failed**
   - Verify `CALENDLY_SHEET_ID` is correct
   - Check Google Service Account permissions
   - Ensure sheet exists and is accessible

### Debug Commands

```bash
# Check environment variables
python -c "import os; print('PAT:', bool(os.getenv('CALENDLY_PAT'))); print('Secret:', bool(os.getenv('CALENDLY_WEBHOOK_SECRET'))); print('Sheet:', bool(os.getenv('CALENDLY_SHEET_ID')))"

# Test Calendly API directly
curl -H "Authorization: Bearer YOUR_PAT" https://api.calendly.com/users/me

# Check webhook endpoint
curl -X POST http://localhost:5000/api/calendly/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## API Endpoints Reference

- `POST /api/calendly/webhook` - Receives Calendly webhook events
- `GET /api/calendly/status` - Check integration health
- `POST /api/calendly/test` - Test webhook processing
- `GET /api/calendly/bookings` - Get recent bookings
- `POST /api/calendly/setup-headers` - Initialize sheet headers

## Data Schema

Each booking creates a row with:

| Column | Description | Example |
|--------|-------------|---------|
| Timestamp | When webhook was received | 2025-01-12T14:30:00Z |
| Invitee Name | Client name | John Doe |
| Invitee Email | Client email | john@example.com |
| Event Type | Calendly event name | 30-min Test Meeting |
| Start Time (UTC) | Appointment start UTC | 2025-01-15T09:00:00Z |
| End Time (UTC) | Appointment end UTC | 2025-01-15T09:30:00Z |
| Start Time (Thai) | Local Thai time | 2025-01-15 16:00 ICT |
| End Time (Thai) | Local Thai time | 2025-01-15 16:30 ICT |
| Timezone | Event timezone | Asia/Bangkok |
| Status | Booking status | active/canceled |
| Calendly Event ID | Unique event ID | evt_12345 |

## Security Notes

- Webhook signatures are verified using HMAC-SHA256
- All API requests use Bearer token authentication
- Environment variables protect sensitive credentials
- HTTPS is required for webhook endpoints in production

## Support

If you encounter issues:

1. Check the Flask application logs
2. Verify all environment variables are set
3. Test each component individually
4. Review Calendly webhook delivery logs
5. Check Google Sheets API quotas and permissions

The integration is now ready to automatically track all Calendly bookings in your Google Sheet with proper Thai timezone conversion! 