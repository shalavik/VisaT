#!/usr/bin/env python3
"""
Form Processor
Handles Google Forms submissions and triggers qualification workflow
"""

import logging
from src.engines.qualification_engine import QualificationEngine
from src.integrations.gmail_client import GmailClient
from src.integrations.whatsapp_client import WhatsAppClient
from src.integrations.sheets_client import SheetsClient
from src.integrations.calendly_client import CalendlyClient

logger = logging.getLogger(__name__)

class FormProcessor:
    """Processes Google Forms submissions"""
    
    def __init__(self):
        self.qualification_engine = QualificationEngine()
        self.gmail_client = GmailClient()
        self.whatsapp_client = WhatsAppClient()
        self.sheets_client = SheetsClient()
        self.calendly_client = CalendlyClient()
    
    def process_submission(self, form_data):
        """
        Process Google Form submission
        
        Args:
            form_data (dict): Form submission data
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract prospect data from form submission
            prospect_data = self._extract_prospect_data(form_data)
            
            if not prospect_data:
                return {"status": "failed", "error": "Could not extract prospect data"}
            
            logger.info(f"Processing form submission for {prospect_data.get('email')}")
            
            # Step 1: Qualify the prospect
            qualification_result = self.qualification_engine.evaluate_prospect(prospect_data)
            qualified = qualification_result.get('qualified', False)
            
            # Step 2: Store in Google Sheets
            sheets_result = self.sheets_client.add_lead(
                prospect_data, 
                qualified=qualified, 
                status="form_submitted"
            )
            
            # Step 3: Send email response
            calendly_link = self.calendly_client.get_booking_link(prospect_data) if qualified else None
            email_result = self.gmail_client.send_qualification_email(
                prospect_data, 
                qualified=qualified, 
                calendly_link=calendly_link
            )
            
            # Step 4: Send WhatsApp follow-up (if WhatsApp number provided)
            whatsapp_result = None
            whatsapp_number = prospect_data.get('whatsapp_number')
            if whatsapp_number:
                whatsapp_result = self.whatsapp_client.send_follow_up(
                    whatsapp_number, 
                    prospect_data.get('full_name', 'Client'),
                    qualified=qualified
                )
            
            # Compile results
            result = {
                "status": "processed",
                "prospect_email": prospect_data.get('email'),
                "qualified": qualified,
                "qualification_reason": qualification_result.get('reason'),
                "sheets_result": sheets_result,
                "email_result": email_result,
                "whatsapp_result": whatsapp_result,
                "calendly_link": calendly_link
            }
            
            logger.info(f"Form processing completed for {prospect_data.get('email')}: qualified={qualified}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing form submission: {e}")
            return {"status": "error", "error": str(e)}
    
    def _extract_prospect_data(self, form_data):
        """
        Extract prospect data from form submission
        
        Args:
            form_data (dict): Raw form data
            
        Returns:
            dict: Extracted prospect data
        """
        try:
            # Handle different possible form data structures
            responses = form_data.get('responses', form_data)
            
            # Map form fields to prospect data
            prospect_data = {
                'full_name': self._get_form_value(responses, ['full_name', 'name', 'Full Name']),
                'email': self._get_form_value(responses, ['email', 'email_address', 'Email Address']),
                'nationality': self._get_form_value(responses, ['nationality', 'Nationality']),
                'current_location': self._get_form_value(responses, ['current_country', 'current_location', 'Current Country']),
                'financial_status': self._parse_financial_status(responses),
                'current_visa_type': self._get_form_value(responses, ['current_visa_type', 'visa_type', 'If you\'re currently in Thailand, what visa type do you hold?']),
                'whatsapp_number': self._get_form_value(responses, ['whatsapp_number', 'whatsapp', 'WhatsApp Number (with country code)']),
                'how_heard': self._get_form_value(responses, ['source', 'how_heard', 'Source']),
                'additional_questions': self._get_form_value(responses, ['additional_questions', 'questions', 'comments'])
            }
            
            # Validate required fields
            if not prospect_data['email'] or not prospect_data['full_name']:
                logger.error("Missing required fields: email or full_name")
                return None
            
            logger.info(f"Extracted prospect data for {prospect_data['email']}")
            return prospect_data
            
        except Exception as e:
            logger.error(f"Error extracting prospect data: {e}")
            return None
    
    def _get_form_value(self, responses, possible_keys):
        """
        Get value from form responses using multiple possible keys
        
        Args:
            responses (dict): Form responses
            possible_keys (list): List of possible field names
            
        Returns:
            str: Field value or empty string
        """
        for key in possible_keys:
            if key in responses:
                return str(responses[key]).strip()
        return ''
    
    def _parse_financial_status(self, responses):
        """
        Parse financial status from form responses
        
        Args:
            responses (dict): Form responses
            
        Returns:
            bool: True if meets financial requirements
        """
        # Look for financial status field
        financial_keys = [
            'financial_status',
            'Do you have more than 500k BTH in your bank account?',
            'financial_requirement',
            'funds'
        ]
        
        for key in financial_keys:
            if key in responses:
                value = str(responses[key]).lower().strip()
                # Check for positive responses
                if value in ['yes', 'true', '1', 'have funds', 'sufficient']:
                    return True
                elif value in ['no', 'false', '0', 'insufficient funds']:
                    return False
        
        # Default to False if not found or unclear
        return False 