#!/usr/bin/env python3
"""
Google Sheets Monitor
Monitors Google Sheets for new form submissions and processes them automatically
"""

import logging
import time
import threading
from datetime import datetime
import os

from .sheets_client_fixed import SheetsClientFixed
from .gmail_client import GmailClient
from .whatsapp_client import WhatsAppClient
from ..engines.qualification_engine import QualificationEngine
from ..integrations.calendly_client import CalendlyClient

logger = logging.getLogger(__name__)

class SheetsMonitor:
    """Monitors Google Sheets for new form submissions"""
    
    def __init__(self, spreadsheet_id=None):
        """
        Initialize the sheets monitor
        
        Args:
            spreadsheet_id (str): Google Sheets ID to monitor
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SHEETS_ID')
        self.sheets_client = SheetsClientFixed()
        self.gmail_client = GmailClient()
        self.whatsapp_client = WhatsAppClient()
        self.qualification_engine = QualificationEngine()
        self.calendly_client = CalendlyClient()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.last_processed_row = 0
        self.processed_rows = set()
        
        # Configuration
        self.sheet_name = "Form Responses 1"  # Default Google Forms sheet name
        self.polling_interval = 30  # Check every 30 seconds
        
        logger.info(f"Sheets Monitor initialized for spreadsheet: {self.spreadsheet_id}")
    
    def start_monitoring(self):
        """Start monitoring the Google Sheets for new submissions"""
        if self.is_monitoring:
            logger.warning("Sheets monitoring is already running")
            return False
        
        if not self.spreadsheet_id:
            logger.error("No Google Sheets ID configured")
            return False
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ Started Google Sheets monitoring")
        return True
    
    def stop_monitoring(self):
        """Stop monitoring the Google Sheets"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("⏹️ Stopped Google Sheets monitoring")
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread"""
        logger.info(f"🔍 Starting sheets monitoring loop (checking every {self.polling_interval}s)")
        
        # Get initial row count to establish baseline
        try:
            initial_data = self._get_sheet_data()
            if initial_data:
                self.last_processed_row = len(initial_data)
                logger.info(f"📊 Initial sheet has {self.last_processed_row} rows")
        except Exception as e:
            logger.error(f"Failed to get initial sheet data: {e}")
            self.last_processed_row = 0
        
        while self.is_monitoring:
            try:
                self._check_for_new_submissions()
                time.sleep(self.polling_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.polling_interval)
    
    def _check_for_new_submissions(self):
        """Check for new form submissions and process them"""
        try:
            # Get current sheet data
            sheet_data = self._get_sheet_data()
            if not sheet_data:
                return
            
            current_row_count = len(sheet_data)
            
            # Check if there are new rows
            if current_row_count > self.last_processed_row:
                new_rows = sheet_data[self.last_processed_row:]
                logger.info(f"📝 Found {len(new_rows)} new form submissions")
                
                # Process each new row
                for i, row_data in enumerate(new_rows):
                    row_number = self.last_processed_row + i + 1
                    self._process_form_submission(row_data, row_number)
                
                # Update processed row count
                self.last_processed_row = current_row_count
                
        except Exception as e:
            logger.error(f"Error checking for new submissions: {e}")
    
    def _get_sheet_data(self):
        """Get data from the Google Sheets using fixed client"""
        try:
            # Use the fixed client's get_data_rows method
            data_rows = self.sheets_client.get_data_rows(self.sheet_name)
            return data_rows
            
        except Exception as e:
            logger.error(f"Failed to get sheet data: {e}")
            return []
    
    def _process_form_submission(self, row_data, row_number):
        """Process a single form submission"""
        try:
            # Extract prospect data from the row
            prospect_data = self._extract_prospect_data_from_row(row_data, row_number)
            
            if not prospect_data:
                logger.warning(f"Could not extract prospect data from row {row_number}")
                return
            
            logger.info(f"📋 Processing form submission from row {row_number}: {prospect_data.get('email')}")
            
            # Qualify the prospect
            qualification_result = self.qualification_engine.evaluate_prospect(prospect_data)
            qualified = qualification_result.get('qualified', False)
            
            logger.info(f"📊 Qualification result for {prospect_data.get('email')}: {qualified}")
            
            # Send email response
            calendly_link = self.calendly_client.get_booking_link(prospect_data) if qualified else None
            email_result = self.gmail_client.send_qualification_email(
                prospect_data, 
                qualified=qualified, 
                calendly_link=calendly_link
            )
            
            # Send WhatsApp follow-up (if qualified and has WhatsApp)
            whatsapp_result = None
            whatsapp_number = prospect_data.get('whatsapp_number')
            if qualified and whatsapp_number:
                whatsapp_result = self.whatsapp_client.send_follow_up(
                    whatsapp_number, 
                    prospect_data.get('full_name', 'Client'),
                    qualified=True
                )
            elif not qualified:
                logger.info(f"Client {prospect_data.get('full_name')} not qualified, skipping WhatsApp follow-up")
                whatsapp_result = {"status": "skipped", "reason": "not_qualified"}
            
            # Log results
            logger.info(f"✅ Processed row {row_number} - Email: {email_result.get('status')}, WhatsApp: {whatsapp_result.get('status') if whatsapp_result else 'N/A'}")
            
            return {
                "row_number": row_number,
                "prospect_email": prospect_data.get('email'),
                "qualified": qualified,
                "qualification_reason": qualification_result.get('reason'),
                "email_result": email_result,
                "whatsapp_result": whatsapp_result,
                "calendly_link": calendly_link
            }
            
        except Exception as e:
            logger.error(f"Error processing row {row_number}: {e}")
            return None
    
    def _extract_prospect_data_from_row(self, row_data, row_number):
        """Extract prospect data from a Google Sheets row"""
        try:
            # Google Forms typically creates columns in this order:
            # [Timestamp, Name, Email, Nationality, Location, Financial Status, WhatsApp, etc.]
            
            if len(row_data) < 4:  # Need at least basic info
                logger.warning(f"Row {row_number} has insufficient data: {len(row_data)} columns")
                return None
            
            # Map common Google Forms column patterns
            prospect_data = {}
            
            # Try to extract data based on common patterns
            for i, cell_value in enumerate(row_data):
                cell_value = str(cell_value).strip() if cell_value else ""
                
                # Column 0: Timestamp (skip)
                if i == 0:
                    continue
                
                # Column 1: Usually full name
                elif i == 1 and cell_value and not prospect_data.get('full_name'):
                    prospect_data['full_name'] = cell_value
                
                # Look for email pattern
                elif '@' in cell_value and '.' in cell_value and not prospect_data.get('email'):
                    prospect_data['email'] = cell_value
                
                # Look for phone number pattern
                elif ('+' in cell_value or cell_value.replace(' ', '').replace('-', '').isdigit()) and len(cell_value.replace(' ', '').replace('-', '').replace('+', '')) >= 8:
                    if not prospect_data.get('whatsapp_number'):
                        prospect_data['whatsapp_number'] = cell_value
                
                # Look for nationality/country
                elif i >= 2 and cell_value and len(cell_value) > 2 and not cell_value.replace(' ', '').isdigit():
                    if not prospect_data.get('nationality') and any(country in cell_value.lower() for country in ['spain', 'usa', 'uk', 'germany', 'france', 'italy', 'thailand', 'singapore', 'australia', 'canada', 'afghanistan', 'pakistan']):
                        prospect_data['nationality'] = cell_value
                    elif not prospect_data.get('current_location'):
                        prospect_data['current_location'] = cell_value
                
                # Look for financial status
                elif cell_value.lower() in ['yes', 'no', 'true', 'false']:
                    if not prospect_data.get('financial_status'):
                        prospect_data['financial_status'] = cell_value.lower() in ['yes', 'true']
            
            # Validate required fields
            if not prospect_data.get('email') or not prospect_data.get('full_name'):
                logger.warning(f"Row {row_number} missing required fields - Email: {prospect_data.get('email')}, Name: {prospect_data.get('full_name')}")
                logger.debug(f"Row data: {row_data}")
                return None
            
            # Set defaults for missing optional fields
            if 'nationality' not in prospect_data:
                prospect_data['nationality'] = 'Unknown'
            if 'current_location' not in prospect_data:
                prospect_data['current_location'] = 'Unknown'
            if 'financial_status' not in prospect_data:
                prospect_data['financial_status'] = False
            
            logger.info(f"✅ Extracted prospect data from row {row_number}: {prospect_data.get('full_name')} ({prospect_data.get('email')})")
            return prospect_data
            
        except Exception as e:
            logger.error(f"Error extracting prospect data from row {row_number}: {e}")
            return None
    
    def get_monitoring_status(self):
        """Get current monitoring status"""
        return {
            "is_monitoring": self.is_monitoring,
            "spreadsheet_id": self.spreadsheet_id,
            "sheet_name": self.sheet_name,
            "last_processed_row": self.last_processed_row,
            "polling_interval": self.polling_interval,
            "processed_count": len(self.processed_rows)
        }
    
    def manual_process_new_rows(self):
        """Manually trigger processing of new rows"""
        logger.info("🔄 Manually checking for new form submissions...")
        try:
            self._check_for_new_submissions()
            return True
        except Exception as e:
            logger.error(f"Manual processing failed: {e}")
            return False 