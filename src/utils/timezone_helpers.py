"""
Timezone conversion utilities for Calendly webhook integration.
Handles UTC to Thai timezone conversions with proper DST handling.
"""

import pytz
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TimezoneConverter:
    """
    Utility class for timezone conversions, specifically UTC to Thai time.
    """
    
    def __init__(self):
        self.thai_tz = pytz.timezone('Asia/Bangkok')
        self.utc_tz = pytz.UTC
        
        logger.info("✅ Timezone converter initialized (UTC ↔ Asia/Bangkok)")
    
    def convert_utc_to_thai(self, utc_iso_string: str) -> str:
        """
        Convert UTC ISO string to Thai local time string.
        
        Args:
            utc_iso_string: UTC time in ISO format (e.g., "2025-01-15T09:00:00Z")
            
        Returns:
            str: Thai local time formatted as "YYYY-MM-DD HH:MM ICT"
        """
        try:
            # Parse ISO string and handle different formats
            if utc_iso_string.endswith('Z'):
                # Remove 'Z' and add UTC offset
                utc_iso_string = utc_iso_string[:-1] + '+00:00'
            elif '+' not in utc_iso_string and 'T' in utc_iso_string:
                # Add UTC offset if missing
                utc_iso_string += '+00:00'
            
            # Parse the datetime
            utc_dt = datetime.fromisoformat(utc_iso_string)
            
            # Ensure it's UTC timezone aware
            if utc_dt.tzinfo is None:
                utc_dt = self.utc_tz.localize(utc_dt)
            elif utc_dt.tzinfo != self.utc_tz:
                utc_dt = utc_dt.astimezone(self.utc_tz)
            
            # Convert to Thai timezone
            thai_dt = utc_dt.astimezone(self.thai_tz)
            
            # Format as readable string
            formatted_time = thai_dt.strftime('%Y-%m-%d %H:%M ICT')
            
            logger.debug(f"🕐 Converted {utc_iso_string} → {formatted_time}")
            return formatted_time
            
        except Exception as e:
            logger.error(f"❌ Error converting UTC to Thai time: {e}")
            # Return original string as fallback
            return utc_iso_string
    
    def convert_utc_to_thai_detailed(self, utc_iso_string: str) -> dict:
        """
        Convert UTC ISO string to Thai time with detailed information.
        
        Args:
            utc_iso_string: UTC time in ISO format
            
        Returns:
            dict: Detailed conversion information
        """
        try:
            # Parse and convert
            if utc_iso_string.endswith('Z'):
                utc_iso_string = utc_iso_string[:-1] + '+00:00'
            elif '+' not in utc_iso_string and 'T' in utc_iso_string:
                utc_iso_string += '+00:00'
            
            utc_dt = datetime.fromisoformat(utc_iso_string)
            
            if utc_dt.tzinfo is None:
                utc_dt = self.utc_tz.localize(utc_dt)
            elif utc_dt.tzinfo != self.utc_tz:
                utc_dt = utc_dt.astimezone(self.utc_tz)
            
            thai_dt = utc_dt.astimezone(self.thai_tz)
            
            return {
                'utc_datetime': utc_dt,
                'thai_datetime': thai_dt,
                'utc_iso': utc_dt.isoformat(),
                'thai_iso': thai_dt.isoformat(),
                'thai_formatted': thai_dt.strftime('%Y-%m-%d %H:%M ICT'),
                'thai_date': thai_dt.strftime('%Y-%m-%d'),
                'thai_time': thai_dt.strftime('%H:%M'),
                'weekday': thai_dt.strftime('%A'),
                'timezone_name': 'Asia/Bangkok',
                'utc_offset': thai_dt.strftime('%z')
            }
            
        except Exception as e:
            logger.error(f"❌ Error in detailed UTC to Thai conversion: {e}")
            return {
                'error': str(e),
                'original_input': utc_iso_string
            }
    
    def is_business_hours(self, utc_iso_string: str, 
                         start_hour: int = 9, end_hour: int = 18) -> bool:
        """
        Check if the given UTC time falls within Thai business hours.
        
        Args:
            utc_iso_string: UTC time in ISO format
            start_hour: Business start hour in Thai time (default: 9 AM)
            end_hour: Business end hour in Thai time (default: 6 PM)
            
        Returns:
            bool: True if within business hours, False otherwise
        """
        try:
            conversion = self.convert_utc_to_thai_detailed(utc_iso_string)
            
            if 'error' in conversion:
                return False
            
            thai_dt = conversion['thai_datetime']
            
            # Check if it's a weekday (Monday=0, Sunday=6)
            if thai_dt.weekday() >= 5:  # Saturday or Sunday
                return False
            
            # Check if within business hours
            hour = thai_dt.hour
            return start_hour <= hour < end_hour
            
        except Exception as e:
            logger.error(f"❌ Error checking business hours: {e}")
            return False
    
    def format_duration(self, start_utc: str, end_utc: str) -> dict:
        """
        Calculate and format duration between two UTC times.
        
        Args:
            start_utc: Start time in UTC ISO format
            end_utc: End time in UTC ISO format
            
        Returns:
            dict: Duration information
        """
        try:
            start_conversion = self.convert_utc_to_thai_detailed(start_utc)
            end_conversion = self.convert_utc_to_thai_detailed(end_utc)
            
            if 'error' in start_conversion or 'error' in end_conversion:
                return {'error': 'Failed to parse times'}
            
            start_dt = start_conversion['thai_datetime']
            end_dt = end_conversion['thai_datetime']
            
            duration = end_dt - start_dt
            
            # Calculate duration components
            total_minutes = int(duration.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            return {
                'start_thai': start_conversion['thai_formatted'],
                'end_thai': end_conversion['thai_formatted'],
                'duration_minutes': total_minutes,
                'duration_hours': hours,
                'duration_remaining_minutes': minutes,
                'duration_formatted': f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m",
                'same_day': start_dt.date() == end_dt.date()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating duration: {e}")
            return {'error': str(e)}

# Global instance for easy import
timezone_converter = TimezoneConverter() 