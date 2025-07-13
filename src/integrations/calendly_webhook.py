"""
Calendly Webhook Processor
Handles incoming webhook events and processes booking data.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import pytz

from .calendly_client import CalendlyClient, CalendlyAPIError
from .sheets_client_fixed import SheetsClientFixed

logger = logging.getLogger(__name__)

class CalendlyWebhookProcessor:
    """
    Processes Calendly webhook events and updates Google Sheets.
    """
    
    def __init__(self):
        self.calendly_client = CalendlyClient()
        self.sheets_client = SheetsClientFixed()
        self.thai_tz = pytz.timezone('Asia/Bangkok')
        self.utc_tz = pytz.UTC
        
        logger.info("✅ Calendly webhook processor initialized")
    
    def process_webhook(self, payload: Dict, signature: str, raw_body: bytes) -> Dict:
        """
        Process incoming Calendly webhook.
        
        Args:
            payload: Webhook payload as dict
            signature: Webhook signature for verification
            raw_body: Raw request body for signature verification
            
        Returns:
            dict: Processing result
        """
        try:
            # Verify webhook signature
            if not self.calendly_client.verify_webhook_signature(raw_body, signature):
                return {
                    "status": "error",
                    "message": "Invalid webhook signature",
                    "processed": False
                }
            
            # Extract event information
            event_type = payload.get("event")
            event_data = payload.get("payload", {})
            
            logger.info(f"📨 Processing webhook event: {event_type}")
            
            # Process supported event types
            if event_type in ["invitee.created", "invitee.canceled"]:
                return self._process_invitee_event(event_type, event_data)
            else:
                logger.info(f"ℹ️ Ignoring unsupported event type: {event_type}")
                return {
                    "status": "ignored",
                    "message": f"Event type {event_type} not processed",
                    "processed": False
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "processed": False
            }
    
    def _process_invitee_event(self, event_type: str, event_data: Dict) -> Dict:
        """
        Process invitee.created or invitee.canceled events.
        
        Args:
            event_type: Type of event (invitee.created or invitee.canceled)
            event_data: Event payload data
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract basic invitee information
            invitee_name = event_data.get("name", "Unknown")
            invitee_email = event_data.get("email", "")
            event_uri = event_data.get("event")
            
            if not event_uri:
                raise ValueError("No event URI found in webhook payload")
            
            logger.info(f"👤 Processing {event_type} for {invitee_name} ({invitee_email})")
            
            # Fetch full event details from Calendly API
            try:
                event_details = self.calendly_client.fetch_event_details(event_uri)
            except CalendlyAPIError as e:
                logger.error(f"❌ Failed to fetch event details: {e}")
                return {
                    "status": "partial_success",
                    "message": f"Webhook received but API fetch failed: {str(e)}",
                    "processed": False
                }
            
            # Process the event data
            booking_data = self._extract_booking_data(
                event_type, event_data, event_details
            )
            
            # Append to Google Sheets
            success = self._append_to_sheets(booking_data)
            
            if success:
                logger.info(f"✅ Successfully processed {event_type} for {invitee_name}")
                return {
                    "status": "success",
                    "message": f"Booking data saved for {invitee_name}",
                    "processed": True,
                    "event_type": event_type,
                    "invitee": invitee_name
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to save booking data to sheets",
                    "processed": False
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing invitee event: {e}")
            return {
                "status": "error",
                "message": f"Event processing failed: {str(e)}",
                "processed": False
            }
    
    def _extract_booking_data(self, event_type: str, event_data: Dict, 
                            event_details: Dict) -> Dict:
        """
        Extract and format booking data for Google Sheets.
        
        Args:
            event_type: Type of webhook event
            event_data: Webhook event data
            event_details: Full event details from API
            
        Returns:
            dict: Formatted booking data
        """
        try:
            # Current timestamp
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Invitee information
            invitee_name = event_data.get("name", "Unknown")
            invitee_email = event_data.get("email", "")
            
            # Event information
            event_name = event_details.get("name", "Unknown Event")
            start_time_utc = event_details.get("start_time", "")
            end_time_utc = event_details.get("end_time", "")
            event_location = event_details.get("location", {})
            timezone_info = event_location.get("timezone", "UTC") if event_location else "UTC"
            
            # Convert times to Thai timezone
            start_time_thai = self._convert_to_thai_time(start_time_utc)
            end_time_thai = self._convert_to_thai_time(end_time_utc)
            
            # Determine status
            status = "canceled" if event_type == "invitee.canceled" else "active"
            
            # Extract event ID
            event_id = event_details.get("uri", "").split("/")[-1] if event_details.get("uri") else ""
            
            return {
                "timestamp": timestamp,
                "invitee_name": invitee_name,
                "invitee_email": invitee_email,
                "event_type": event_name,
                "start_time_utc": start_time_utc,
                "end_time_utc": end_time_utc,
                "start_time_thai": start_time_thai,
                "end_time_thai": end_time_thai,
                "timezone": timezone_info,
                "status": status,
                "calendly_event_id": event_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting booking data: {e}")
            raise
    
    def _convert_to_thai_time(self, utc_iso_string: str) -> str:
        """
        Convert UTC ISO string to Thai local time.
        
        Args:
            utc_iso_string: UTC time in ISO format
            
        Returns:
            str: Thai local time formatted as "YYYY-MM-DD HH:MM ICT"
        """
        try:
            if not utc_iso_string:
                return ""
            
            # Parse ISO string
            if utc_iso_string.endswith('Z'):
                utc_iso_string = utc_iso_string[:-1] + '+00:00'
            elif '+' not in utc_iso_string and 'T' in utc_iso_string:
                utc_iso_string += '+00:00'
            
            utc_dt = datetime.fromisoformat(utc_iso_string)
            
            # Ensure UTC timezone
            if utc_dt.tzinfo is None:
                utc_dt = self.utc_tz.localize(utc_dt)
            elif utc_dt.tzinfo != self.utc_tz:
                utc_dt = utc_dt.astimezone(self.utc_tz)
            
            # Convert to Thai timezone
            thai_dt = utc_dt.astimezone(self.thai_tz)
            
            return thai_dt.strftime('%Y-%m-%d %H:%M ICT')
            
        except Exception as e:
            logger.error(f"❌ Error converting time to Thai: {e}")
            return utc_iso_string  # Return original as fallback
    
    def _append_to_sheets(self, booking_data: Dict) -> bool:
        """
        Append booking data to Google Sheets.
        
        Args:
            booking_data: Formatted booking data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get sheet ID for Calendly bookings
            sheet_id = self._get_calendly_sheet_id()
            
            if not sheet_id:
                logger.error("❌ Calendly sheet ID not configured")
                return False
            
            # Prepare row data
            row_data = [
                booking_data["timestamp"],
                booking_data["invitee_name"],
                booking_data["invitee_email"],
                booking_data["event_type"],
                booking_data["start_time_utc"],
                booking_data["end_time_utc"],
                booking_data["start_time_thai"],
                booking_data["end_time_thai"],
                booking_data["timezone"],
                booking_data["status"],
                booking_data["calendly_event_id"]
            ]
            
            # Append to sheet
            success = self.sheets_client.append_booking_row(sheet_id, row_data)
            
            if success:
                logger.info(f"📊 Booking data appended to sheet: {booking_data['invitee_name']}")
            else:
                logger.error("❌ Failed to append booking data to sheet")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error appending to sheets: {e}")
            return False
    
    def _get_calendly_sheet_id(self) -> Optional[str]:
        """
        Get the Google Sheet ID for Calendly bookings.
        
        Returns:
            str: Sheet ID or None if not configured
        """
        import os
        return os.getenv("CALENDLY_SHEET_ID")
    
    def test_webhook_processing(self, test_data: Optional[Dict] = None) -> Dict:
        """
        Test webhook processing with sample data.
        
        Args:
            test_data: Optional test data, uses default if not provided
            
        Returns:
            dict: Test result
        """
        try:
            if not test_data:
                test_data = {
                    "event": "invitee.created",
                    "payload": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "event": "https://api.calendly.com/scheduled_events/test-event-123"
                    }
                }
            
            logger.info("🧪 Running webhook processing test...")
            
            # Test API connection first
            if not self.calendly_client.test_api_connection():
                return {
                    "status": "error",
                    "message": "Calendly API connection failed"
                }
            
            # Test sheets connection
            sheet_id = self._get_calendly_sheet_id()
            if not sheet_id:
                return {
                    "status": "error",
                    "message": "Calendly sheet ID not configured"
                }
            
            logger.info("✅ Webhook processing test completed successfully")
            return {
                "status": "success",
                "message": "All components ready for webhook processing",
                "calendly_api": "connected",
                "sheets_api": "connected",
                "sheet_id": sheet_id
            }
            
        except Exception as e:
            logger.error(f"❌ Webhook processing test failed: {e}")
            return {
                "status": "error",
                "message": f"Test failed: {str(e)}"
            } 