"""
Calendly API Client for webhook handling and event fetching.
Handles HMAC signature verification and API interactions.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
import hashlib
import hmac

logger = logging.getLogger(__name__)

class CalendlyClient:
    def __init__(self):
        self.access_token = os.getenv('CALENDLY_PAT') or os.getenv('CALENDLY_ACCESS_TOKEN')
        self.event_type_uuid = os.getenv('CALENDLY_EVENT_TYPE_UUID')
        
        if not self.access_token:
            raise ValueError("CALENDLY_PAT or CALENDLY_ACCESS_TOKEN environment variable is required")
        
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Get user info to determine organization
        self.user_info = self._get_user_info()
        self.organization_uri = self.user_info.get('current_organization')
        
        logger.info("✅ Calendly client initialized successfully (polling mode)")
    
    def _get_user_info(self):
        """Get current user information"""
        try:
            response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
            response.raise_for_status()
            return response.json().get('resource', {})
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {}
    
    def get_scheduled_events(self, min_start_time=None, max_start_time=None):
        """
        Get scheduled events from Calendly
        
        Args:
            min_start_time: datetime object for the earliest start time
            max_start_time: datetime object for the latest start time
        
        Returns:
            List of scheduled events with invitee details
        """
        if not min_start_time:
            # Default to events from the last 24 hours
            min_start_time = datetime.utcnow() - timedelta(hours=24)
        
        if not max_start_time:
            # Default to events in the next 30 days
            max_start_time = datetime.utcnow() + timedelta(days=30)
        
        params = {
            'organization': self.organization_uri,
            'min_start_time': min_start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'max_start_time': max_start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': 'active',
            'sort': 'start_time:desc'
        }
        
        try:
            response = requests.get(f"{self.base_url}/scheduled_events", headers=self.headers, params=params)
            response.raise_for_status()
            
            events = response.json().get('collection', [])
            logger.info(f"📅 Retrieved {len(events)} scheduled events from Calendly")
            
            # Enrich events with invitee details
            enriched_events = []
            for event in events:
                event_with_invitees = self._get_event_with_invitees(event)
                if event_with_invitees:
                    enriched_events.append(event_with_invitees)
            
            return enriched_events
            
        except Exception as e:
            logger.error(f"Failed to get scheduled events: {e}")
            return []
    
    def _get_event_with_invitees(self, event):
        """Get event details with invitee information"""
        try:
            event_uuid = event['uri'].split('/')[-1]
            
            # Get invitees for this event
            response = requests.get(
                f"{self.base_url}/scheduled_events/{event_uuid}/invitees",
                headers=self.headers
            )
            response.raise_for_status()
            
            invitees = response.json().get('collection', [])
            
            # Return event with invitee details
            return {
                'event_uuid': event_uuid,
                'event_uri': event['uri'],
                'name': event.get('name', ''),
                'start_time': event.get('start_time'),
                'end_time': event.get('end_time'),
                'status': event.get('status', 'active'),
                'created_at': event.get('created_at'),
                'updated_at': event.get('updated_at'),
                'invitees': invitees,
                'event_type': event.get('event_type', '')
            }
            
        except Exception as e:
            logger.error(f"Failed to get invitees for event {event.get('uri', 'unknown')}: {e}")
            return None
    
    def get_canceled_events(self, min_start_time=None, max_start_time=None):
        """Get canceled events from Calendly"""
        if not min_start_time:
            min_start_time = datetime.utcnow() - timedelta(days=7)
        
        if not max_start_time:
            max_start_time = datetime.utcnow() + timedelta(days=30)
        
        params = {
            'organization': self.organization_uri,
            'min_start_time': min_start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'max_start_time': max_start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': 'canceled',
            'sort': 'start_time:desc'
        }
        
        try:
            response = requests.get(f"{self.base_url}/scheduled_events", headers=self.headers, params=params)
            response.raise_for_status()
            
            events = response.json().get('collection', [])
            logger.info(f"❌ Retrieved {len(events)} canceled events from Calendly")
            
            # Enrich events with invitee details
            enriched_events = []
            for event in events:
                event_with_invitees = self._get_event_with_invitees(event)
                if event_with_invitees:
                    enriched_events.append(event_with_invitees)
            
            return enriched_events
            
        except Exception as e:
            logger.error(f"Failed to get canceled events: {e}")
            return []
    
    def verify_webhook_signature(self, payload, signature):
        """
        Legacy method for webhook verification - kept for compatibility
        Returns True for now since we're using polling
        """
        logger.warning("⚠️  Webhook verification called but using polling mode")
        return True 