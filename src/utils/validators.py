#!/usr/bin/env python3
"""
Data Validators
Validation utilities for VisaT system
"""

import re
import logging

logger = logging.getLogger(__name__)

def validate_email(email):
    """
    Validate email address format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid email format
    """
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))

def validate_phone_number(phone):
    """
    Validate phone number format (international format)
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid phone format
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove spaces, dashes, and parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone.strip())
    
    # Check for international format (+ followed by 7-15 digits)
    phone_pattern = r'^\+\d{7,15}$'
    return bool(re.match(phone_pattern, cleaned_phone))

def validate_nationality(nationality):
    """
    Validate nationality field
    
    Args:
        nationality (str): Nationality to validate
        
    Returns:
        bool: True if valid nationality
    """
    if not nationality or not isinstance(nationality, str):
        return False
    
    # Basic validation - should be alphabetic and reasonable length
    cleaned = nationality.strip()
    return len(cleaned) >= 2 and len(cleaned) <= 50 and cleaned.replace(' ', '').isalpha()

def sanitize_string(input_string, max_length=255):
    """
    Sanitize string input
    
    Args:
        input_string (str): String to sanitize
        max_length (int): Maximum allowed length
        
    Returns:
        str: Sanitized string
    """
    if not input_string or not isinstance(input_string, str):
        return ''
    
    # Remove leading/trailing whitespace and limit length
    sanitized = input_string.strip()[:max_length]
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    return sanitized

def validate_prospect_data(prospect_data):
    """
    Validate complete prospect data
    
    Args:
        prospect_data (dict): Prospect data to validate
        
    Returns:
        dict: Validation result with errors if any
    """
    errors = []
    warnings = []
    
    # Required fields validation
    required_fields = ['full_name', 'email', 'nationality']
    for field in required_fields:
        if not prospect_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Email validation
    email = prospect_data.get('email')
    if email and not validate_email(email):
        errors.append("Invalid email format")
    
    # Phone validation (if provided)
    phone = prospect_data.get('whatsapp_number')
    if phone and not validate_phone_number(phone):
        warnings.append("Phone number format may be invalid")
    
    # Nationality validation
    nationality = prospect_data.get('nationality')
    if nationality and not validate_nationality(nationality):
        errors.append("Invalid nationality format")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def sanitize_prospect_data(prospect_data):
    """
    Sanitize prospect data
    
    Args:
        prospect_data (dict): Prospect data to sanitize
        
    Returns:
        dict: Sanitized prospect data
    """
    sanitized = {}
    
    string_fields = [
        'full_name', 'email', 'nationality', 'current_location',
        'current_visa_type', 'whatsapp_number', 'how_heard', 'additional_questions'
    ]
    
    for field in string_fields:
        if field in prospect_data:
            sanitized[field] = sanitize_string(prospect_data[field])
    
    # Handle boolean fields
    if 'financial_status' in prospect_data:
        sanitized['financial_status'] = bool(prospect_data['financial_status'])
    
    return sanitized 