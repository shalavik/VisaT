#!/usr/bin/env python3
"""
Google Sheets Client
Handles data storage and analytics using Google Sheets API
"""

import os
import json
import logging
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

class SheetsClient:
    """Google Sheets client for data storage"""
    
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        self.service_account_file = 'config/google_service_account.json'
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        
        try:
            if os.path.exists(self.service_account_file):
                credentials = Credentials.from_service_account_file(
                    self.service_account_file, 
                    scopes=self.scopes
                )
                self.service = build('sheets', 'v4', credentials=credentials)
                logger.info("Google Sheets client initialized successfully")
            else:
                logger.warning(f"Service account file not found: {self.service_account_file}")
                self.service = None
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            self.service = None
    
    def add_lead(self, prospect_data, qualified=False, status="new"):
        """
        Add lead to Google Sheets
        
        Args:
            prospect_data (dict): Prospect information
            qualified (bool): Whether prospect is qualified
            status (str): Lead status
            
        Returns:
            dict: Result of operation
        """
        try:
            if not self.service:
                return {"status": "failed", "error": "Sheets service not available"}
            
            # Prepare row data
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row_data = [
                timestamp,
                prospect_data.get('full_name', ''),
                prospect_data.get('email', ''),
                prospect_data.get('nationality', ''),
                prospect_data.get('current_location', ''),
                str(prospect_data.get('financial_status', '')),
                prospect_data.get('current_visa_type', ''),
                prospect_data.get('whatsapp_number', ''),
                prospect_data.get('how_heard', ''),
                str(qualified),
                status,
                prospect_data.get('additional_questions', '')
            ]
            
            # Append to sheet
            body = {
                'values': [row_data]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='A:L',  # Adjust range based on columns
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Lead added to sheets: {prospect_data.get('email')}")
            return {
                "status": "success",
                "message": "Lead added successfully",
                "updated_cells": result.get('updates', {}).get('updatedCells', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to add lead to sheets: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def update_lead_status(self, email, new_status):
        """
        Update lead status in Google Sheets
        
        Args:
            email (str): Lead email to find
            new_status (str): New status to set
            
        Returns:
            dict: Result of operation
        """
        try:
            if not self.service:
                return {"status": "failed", "error": "Sheets service not available"}
            
            # Get all data to find the row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:L'
            ).execute()
            
            values = result.get('values', [])
            
            # Find row with matching email (assuming email is in column C)
            for i, row in enumerate(values):
                if len(row) > 2 and row[2] == email:  # Column C (index 2)
                    # Update status in column K (index 10)
                    update_range = f'K{i+1}'
                    update_body = {
                        'values': [[new_status]]
                    }
                    
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id,
                        range=update_range,
                        valueInputOption='RAW',
                        body=update_body
                    ).execute()
                    
                    logger.info(f"Updated status for {email} to {new_status}")
                    return {"status": "success", "message": "Status updated"}
            
            return {"status": "not_found", "message": "Email not found"}
            
        except Exception as e:
            logger.error(f"Failed to update lead status: {e}")
            return {"status": "failed", "error": str(e)}
    
    def get_lead_statistics(self):
        """
        Get lead statistics from Google Sheets
        
        Returns:
            dict: Statistics data
        """
        try:
            if not self.service:
                return {
                    "total_leads": 0,
                    "qualified_leads": 0,
                    "appointments_booked": 0,
                    "conversion_rate": 0.0,
                    "error": "Sheets service not available"
                }
            
            # Get all data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='A:L'
            ).execute()
            
            values = result.get('values', [])
            
            if len(values) <= 1:  # Only header or no data
                return {
                    "total_leads": 0,
                    "qualified_leads": 0,
                    "appointments_booked": 0,
                    "conversion_rate": 0.0
                }
            
            # Skip header row
            data_rows = values[1:]
            
            total_leads = len(data_rows)
            qualified_leads = 0
            appointments_booked = 0
            
            for row in data_rows:
                # Check qualification status (column J, index 9)
                if len(row) > 9 and row[9].lower() == 'true':
                    qualified_leads += 1
                
                # Check appointment status (column K, index 10)
                if len(row) > 10 and 'booked' in row[10].lower():
                    appointments_booked += 1
            
            conversion_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0.0
            
            stats = {
                "total_leads": total_leads,
                "qualified_leads": qualified_leads,
                "appointments_booked": appointments_booked,
                "conversion_rate": round(conversion_rate, 2)
            }
            
            logger.info(f"Retrieved lead statistics: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get lead statistics: {e}")
            return {
                "total_leads": 0,
                "qualified_leads": 0,
                "appointments_booked": 0,
                "conversion_rate": 0.0,
                "error": str(e)
            }
    
    def setup_headers(self):
        """
        Set up column headers in the Google Sheet
        
        Returns:
            dict: Result of operation
        """
        try:
            if not self.service:
                return {"status": "failed", "error": "Sheets service not available"}
            
            headers = [
                'Timestamp',
                'Full Name',
                'Email',
                'Nationality', 
                'Current Location',
                'Financial Status',
                'Current Visa Type',
                'WhatsApp Number',
                'Source',
                'Qualified',
                'Status',
                'Additional Questions'
            ]
            
            body = {
                'values': [headers]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range='A1:L1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info("Sheet headers set up successfully")
            return {"status": "success", "message": "Headers set up"}
            
        except Exception as e:
            logger.error(f"Failed to set up headers: {e}")
            return {"status": "failed", "error": str(e)} 