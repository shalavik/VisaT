#!/usr/bin/env python3
"""
Calendly API Client
Handles appointment booking integration
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

class CalendlyClient:
    """Calendly API client for appointment booking"""
    
    def __init__(self):
        self.access_token = os.getenv('CALENDLY_ACCESS_TOKEN')
        self.event_type_uuid = os.getenv('CALENDLY_EVENT_TYPE_UUID')
        self.static_link = os.getenv('CALENDLY_STATIC_LINK')
        self.api_base = 'https://api.calendly.com'
        
        if not self.access_token:
            logger.warning("Calendly access token not configured")
    
    def get_booking_link(self, prospect_data=None):
        """
        Get Calendly booking link
        
        Args:
            prospect_data (dict, optional): Prospect information for personalization
            
        Returns:
            str: Calendly booking link
        """
        # For now, return static link
        # In future, could be personalized with prospect data
        return self.static_link or "https://calendly.com/visat-consultation"
    
    def create_scheduled_event(self, prospect_email, prospect_name):
        """
        Create a scheduled event (requires webhook or advanced integration)
        
        Args:
            prospect_email (str): Prospect email
            prospect_name (str): Prospect name
            
        Returns:
            dict: Result of operation
        """
        try:
            if not self.access_token:
                return {
                    "status": "failed",
                    "error": "Calendly access token not configured",
                    "booking_link": self.get_booking_link()
                }
            
            # Note: Direct event creation requires specific event type setup
            # For most use cases, directing users to booking link is sufficient
            
            logger.info(f"Booking link provided for {prospect_email}")
            return {
                "status": "success",
                "message": "Booking link provided",
                "booking_link": self.get_booking_link(),
                "instructions": "Please use the booking link to schedule your consultation"
            }
            
        except Exception as e:
            logger.error(f"Calendly operation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "booking_link": self.get_booking_link()
            }
    
    def get_user_info(self):
        """
        Get Calendly user information
        
        Returns:
            dict: User information or error
        """
        try:
            if not self.access_token:
                return {"status": "failed", "error": "Access token not configured"}
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f'{self.api_base}/users/me', headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info("Calendly user info retrieved successfully")
                return {
                    "status": "success",
                    "user": user_data.get('resource', {})
                }
            else:
                logger.error(f"Calendly API error: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to get Calendly user info: {e}")
            return {"status": "failed", "error": str(e)}
    
    def get_event_types(self):
        """
        Get available event types
        
        Returns:
            dict: Event types or error
        """
        try:
            if not self.access_token:
                return {"status": "failed", "error": "Access token not configured"}
            
            # First get user info to get user URI
            user_info = self.get_user_info()
            if user_info.get('status') != 'success':
                return user_info
            
            user_uri = user_info['user'].get('uri')
            if not user_uri:
                return {"status": "failed", "error": "User URI not found"}
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {'user': user_uri}
            response = requests.get(f'{self.api_base}/event_types', headers=headers, params=params)
            
            if response.status_code == 200:
                event_data = response.json()
                logger.info("Calendly event types retrieved successfully")
                return {
                    "status": "success",
                    "event_types": event_data.get('collection', [])
                }
            else:
                logger.error(f"Calendly API error: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Failed to get Calendly event types: {e}")
            return {"status": "failed", "error": str(e)}
    
    def test_connection(self):
        """
        Test Calendly API connection
        
        Returns:
            dict: Connection test result
        """
        try:
            result = self.get_user_info()
            if result.get('status') == 'success':
                return {
                    "status": "success",
                    "message": "Calendly connection successful",
                    "user_name": result.get('user', {}).get('name', 'Unknown')
                }
            else:
                return {
                    "status": "failed",
                    "message": "Calendly connection failed",
                    "error": result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Calendly connection test failed: {e}")
            return {"status": "failed", "error": str(e)} 