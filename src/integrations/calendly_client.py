"""
Calendly API Client for webhook handling and event fetching.
Handles HMAC signature verification and API interactions.
"""

import os
import hmac
import hashlib
import requests
import logging
from typing import Dict, Optional
import time

logger = logging.getLogger(__name__)

class CalendlyAPIError(Exception):
    """Exception raised for Calendly API errors."""
    pass

class CalendlyClient:
    """
    Calendly API client for webhook verification and event fetching.
    """
    
    def __init__(self):
        self.pat = os.getenv("CALENDLY_PAT")
        self.webhook_secret = os.getenv("CALENDLY_WEBHOOK_SECRET")
        
        if not self.pat:
            raise ValueError("CALENDLY_PAT environment variable is required")
        if not self.webhook_secret:
            raise ValueError("CALENDLY_WEBHOOK_SECRET environment variable is required")
        
        # Setup session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        })
        
        logger.info("✅ Calendly client initialized successfully")
    
    def verify_webhook_signature(self, raw_body: bytes, signature: str) -> bool:
        """
        Verify webhook signature using HMAC-SHA256.
        
        Args:
            raw_body: Raw request body as bytes
            signature: Signature from X-Calendly-Signature header
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            if not signature:
                logger.warning("❌ No signature provided in webhook")
                return False
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                raw_body,
                hashlib.sha256
            ).hexdigest()
            
            # Use compare_digest for timing attack protection
            is_valid = hmac.compare_digest(expected_signature, signature)
            
            if is_valid:
                logger.info("✅ Webhook signature verified successfully")
            else:
                logger.warning("❌ Webhook signature verification failed")
                
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ Error verifying webhook signature: {e}")
            return False
    
    def fetch_event_details(self, event_uri: str, max_retries: int = 3) -> Dict:
        """
        Fetch full event details from Calendly API with retry logic.
        
        Args:
            event_uri: URI of the event to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict: Event details from Calendly API
            
        Raises:
            CalendlyAPIError: If API request fails after retries
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"📡 Fetching event details from: {event_uri}")
                
                response = self.session.get(event_uri, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                event_details = data.get("resource", {})
                
                if not event_details:
                    raise CalendlyAPIError("No event resource found in API response")
                
                logger.info(f"✅ Successfully fetched event details: {event_details.get('name', 'Unknown Event')}")
                return event_details
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise CalendlyAPIError(f"Failed to fetch event details after {max_retries} attempts: {e}")
            
            except Exception as e:
                logger.error(f"❌ Unexpected error fetching event details: {e}")
                raise CalendlyAPIError(f"Unexpected error: {e}")
    
    def test_api_connection(self) -> bool:
        """
        Test API connection and authentication.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            logger.info("🔍 Testing Calendly API connection...")
            
            # Test with user endpoint
            response = self.session.get("https://api.calendly.com/users/me", timeout=10)
            response.raise_for_status()
            
            user_data = response.json()
            user_name = user_data.get("resource", {}).get("name", "Unknown")
            
            logger.info(f"✅ Calendly API connection successful. User: {user_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Calendly API connection failed: {e}")
            return False
    
    def close(self):
        """Close the HTTP session."""
        if hasattr(self, 'session'):
            self.session.close()
            logger.info("🔒 Calendly client session closed") 