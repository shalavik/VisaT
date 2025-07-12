#!/usr/bin/env python3
"""
Google Sheets Client - Fixed Version
Handles JWT signature issues and authentication problems
"""

import os
import json
import logging
import time
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class SheetsClientFixed:
    """Google Sheets client with JWT signature fixes"""
    
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.service_account_file = 'config/google_service_account.json'
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        try:
            if os.path.exists(self.service_account_file):
                # Load credentials with specific configurations
                credentials = Credentials.from_service_account_file(
                    self.service_account_file, 
                    scopes=self.scopes
                )
                
                # Force refresh to handle clock skew issues
                credentials.refresh(Request())
                
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info("Google Sheets client initialized successfully")
            else:
                logger.warning(f"Service account file not found: {self.service_account_file}")
                self.service = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            # Try alternative initialization method
            try:
                self.service = self._init_with_retry()
            except Exception as e2:
                logger.error(f"Retry initialization also failed: {e2}")
                self.service = None
    
    def _init_with_retry(self):
        """Alternative initialization method with retry logic"""
        try:
            # Load service account info directly
            with open(self.service_account_file, 'r') as f:
                service_account_info = json.load(f)
            
            # Create credentials from info
            credentials = Credentials.from_service_account_info(
                service_account_info,
                scopes=self.scopes
            )
            
            # Build service
            service = build('sheets', 'v4', credentials=credentials)
            logger.info("Alternative Google Sheets initialization successful")
            return service
            
        except Exception as e:
            logger.error(f"Alternative initialization failed: {e}")
            raise e
    
    def test_connection(self):
        """Test connection to Google Sheets"""
        try:
            if not self.service:
                return {"status": "failed", "error": "Service not initialized"}
            
            if not self.spreadsheet_id:
                return {"status": "failed", "error": "No spreadsheet ID configured"}
            
            # Test by getting spreadsheet metadata
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            title = spreadsheet.get('properties', {}).get('title', 'Unknown')
            sheet_count = len(spreadsheet.get('sheets', []))
            
            return {
                "status": "success",
                "title": title,
                "sheet_count": sheet_count,
                "spreadsheet_id": self.spreadsheet_id
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def get_sheet_data(self, sheet_name="Form Responses 1", range_spec="A:Z"):
        """Get data from the Google Sheets with error handling"""
        try:
            if not self.service:
                raise Exception("Sheets service not available")
            
            # Get all data from the sheet
            range_name = f"{sheet_name}!{range_spec}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Retrieved {len(values)} rows from sheet")
            
            return values
            
        except Exception as e:
            logger.error(f"Failed to get sheet data: {e}")
            
            # If JWT error, try to reinitialize
            if "invalid_grant" in str(e).lower() or "jwt" in str(e).lower():
                logger.info("JWT error detected, trying to reinitialize...")
                try:
                    self.__init__()  # Reinitialize
                    if self.service:
                        # Retry the request
                        range_name = f"{sheet_name}!{range_spec}"
                        result = self.service.spreadsheets().values().get(
                            spreadsheetId=self.spreadsheet_id,
                            range=range_name
                        ).execute()
                        values = result.get('values', [])
                        logger.info(f"Retry successful: Retrieved {len(values)} rows")
                        return values
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
            
            raise e
    
    def get_headers(self, sheet_name="Form Responses 1"):
        """Get header row from the sheet"""
        try:
            data = self.get_sheet_data(sheet_name, "A1:Z1")
            return data[0] if data else []
        except Exception as e:
            logger.error(f"Failed to get headers: {e}")
            return []
    
    def get_data_rows(self, sheet_name="Form Responses 1"):
        """Get data rows (excluding header)"""
        try:
            data = self.get_sheet_data(sheet_name, "A:Z")
            return data[1:] if len(data) > 1 else []
        except Exception as e:
            logger.error(f"Failed to get data rows: {e}")
            return [] 