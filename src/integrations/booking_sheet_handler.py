import logging
from datetime import datetime
from .sheets_client_fixed import SheetsClientFixed
import os

logger = logging.getLogger(__name__)

class BookingSheetHandler:
    def __init__(self):
        self.sheets_client = SheetsClientFixed()
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.sheet_name = "Form Responses 1"  # Use existing form responses sheet
        logger.info("📊 BookingSheetHandler initialized for existing form responses")
    
    def update_booking_info(self, invitee_email, scheduled_time_utc, is_canceled=False):
        """
        Update booking information for an existing form response based on email
        
        Args:
            invitee_email: Email to match in the form responses
            scheduled_time_utc: Scheduled time in UTC format
            is_canceled: Boolean indicating if booking is canceled
        """
        try:
            if not self.spreadsheet_id:
                logger.error("GOOGLE_SHEETS_ID not configured")
                return False
            
            # Get all form data to find the matching email
            form_data = self._get_form_data()
            if not form_data:
                logger.warning("No form data found")
                return False
            
            # Find the row with matching email
            email_column_index = self._find_email_column_index(form_data[0])  # Headers row
            scheduled_time_column_index = self._find_scheduled_time_column_index(form_data[0])
            canceled_column_index = self._find_canceled_column_index(form_data[0])
            
            if email_column_index == -1:
                logger.error("Could not find email column in form responses")
                return False
            
            # Find matching row
            matching_row_index = None
            for i, row in enumerate(form_data[1:], start=2):  # Start from row 2 (skip headers)
                if len(row) > email_column_index and row[email_column_index] == invitee_email:
                    matching_row_index = i
                    break
            
            if not matching_row_index:
                logger.warning(f"No form response found for email: {invitee_email}")
                return False
            
            # Update the booking information
            updates_made = False
            
            # Update Scheduled Time (UTC)
            if scheduled_time_column_index != -1 and scheduled_time_utc:
                success = self._update_cell(matching_row_index, scheduled_time_column_index + 1, scheduled_time_utc)
                if success:
                    logger.info(f"✅ Updated scheduled time for {invitee_email}: {scheduled_time_utc}")
                    updates_made = True
                else:
                    logger.error(f"Failed to update scheduled time for {invitee_email}")
            
            # Update Canceled status
            if canceled_column_index != -1:
                canceled_value = "TRUE" if is_canceled else "FALSE"
                success = self._update_cell(matching_row_index, canceled_column_index + 1, canceled_value)
                if success:
                    logger.info(f"✅ Updated canceled status for {invitee_email}: {canceled_value}")
                    updates_made = True
                else:
                    logger.error(f"Failed to update canceled status for {invitee_email}")
            
            return updates_made
            
        except Exception as e:
            logger.error(f"Error updating booking info for {invitee_email}: {e}")
            return False
    
    def _get_form_data(self):
        """Get all form response data"""
        try:
            return self.sheets_client.get_sheet_data(self.sheet_name, "A:Z")
        except Exception as e:
            logger.error(f"Error getting form data: {e}")
            return []
    
    def _find_email_column_index(self, headers):
        """Find the index of the email column"""
        email_keywords = ['email', 'Email Address', 'Your Email Address']
        for keyword in email_keywords:
            for i, header in enumerate(headers):
                if keyword in str(header):
                    return i
        return -1
    
    def _find_scheduled_time_column_index(self, headers):
        """Find the index of the Scheduled Time (UTC) column"""
        for i, header in enumerate(headers):
            if 'Scheduled Time (UTC)' in str(header):
                return i
        return -1
    
    def _find_canceled_column_index(self, headers):
        """Find the index of the Canceled? column"""
        for i, header in enumerate(headers):
            if 'Canceled?' in str(header):
                return i
        return -1
    
    def _update_cell(self, row_index, col_index, value):
        """Update a specific cell in the sheet"""
        try:
            # Convert column index to letter (A=1, B=2, etc.)
            col_letter = chr(ord('A') + col_index - 1)
            range_name = f"{self.sheet_name}!{col_letter}{row_index}"
            
            body = {
                "values": [[value]]
            }
            
            result = self.sheets_client.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            return updated_cells > 0
            
        except Exception as e:
            logger.error(f"Error updating cell {row_index},{col_index}: {e}")
            return False
    
    def upsert_booking(self, booking_data):
        """
        Legacy method - now redirects to update_booking_info for existing form responses
        
        Args:
            booking_data: dict containing booking information
        """
        try:
            invitee_email = booking_data.get('invitee_email')
            scheduled_time = booking_data.get('scheduled_time')
            is_canceled = booking_data.get('status') == 'canceled'
            
            if not invitee_email:
                logger.warning("No invitee email provided in booking data")
                return False
            
            return self.update_booking_info(invitee_email, scheduled_time, is_canceled)
            
        except Exception as e:
            logger.error(f"Error in upsert_booking: {e}")
            return False
    
    def get_latest_booking_timestamp(self):
        """Get the timestamp of the most recent booking to optimize polling"""
        try:
            # Get form data and check Scheduled Time column
            form_data = self._get_form_data()
            if not form_data or len(form_data) < 2:
                return None
            
            headers = form_data[0]
            scheduled_time_index = self._find_scheduled_time_column_index(headers)
            
            if scheduled_time_index == -1:
                return None
            
            # Find the most recent scheduled time
            latest_timestamp = None
            for row in form_data[1:]:  # Skip headers
                if len(row) > scheduled_time_index:
                    scheduled_time = row[scheduled_time_index]
                    if scheduled_time:
                        try:
                            # Parse ISO format timestamp
                            timestamp = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                            if not latest_timestamp or timestamp > latest_timestamp:
                                latest_timestamp = timestamp
                        except:
                            continue
            
            return latest_timestamp
            
        except Exception as e:
            logger.warning(f"Could not get latest booking timestamp: {e}")
            return None
    
    def get_booking_stats(self):
        """Get basic statistics about bookings from form responses"""
        try:
            form_data = self._get_form_data()
            if not form_data or len(form_data) < 2:
                return {
                    'total_bookings': 0,
                    'active_bookings': 0,
                    'canceled_bookings': 0
                }
            
            headers = form_data[0]
            scheduled_time_index = self._find_scheduled_time_column_index(headers)
            canceled_index = self._find_canceled_column_index(headers)
            
            total_bookings = 0
            active_bookings = 0
            canceled_bookings = 0
            
            for row in form_data[1:]:  # Skip headers
                # Count entries that have scheduled times
                if (scheduled_time_index != -1 and 
                    len(row) > scheduled_time_index and 
                    row[scheduled_time_index]):
                    
                    total_bookings += 1
                    
                    # Check if canceled
                    if (canceled_index != -1 and 
                        len(row) > canceled_index and 
                        row[canceled_index] == 'TRUE'):
                        canceled_bookings += 1
                    else:
                        active_bookings += 1
            
            return {
                'total_bookings': total_bookings,
                'active_bookings': active_bookings,
                'canceled_bookings': canceled_bookings
            }
            
        except Exception as e:
            logger.error(f"Error getting booking stats: {e}")
            return {
                'total_bookings': 0,
                'active_bookings': 0,
                'canceled_bookings': 0
            } 