#!/usr/bin/env python3
"""
Qualification Engine
Evaluates prospects based on configurable business rules
"""

import json
import logging

logger = logging.getLogger(__name__)

class QualificationEngine:
    """Evaluates prospects based on business rules"""
    
    def __init__(self, rules_file='config/rules.json'):
        self.rules_file = rules_file
        self.rules = self._load_rules()
    
    def _load_rules(self):
        """Load business rules from JSON file"""
        try:
            with open(self.rules_file, 'r') as f:
                rules = json.load(f)
                logger.info("Business rules loaded successfully")
                return rules
        except Exception as e:
            logger.error(f"Failed to load rules from {self.rules_file}: {e}")
            # Return default rules if file loading fails
            return self._get_default_rules()
    
    def _get_default_rules(self):
        """Get default business rules"""
        return {
            "blocked_nationalities": [
                "Myanmar", "North Korea", "Iran", "Syria", "Afghanistan",
                "Somalia", "Libya", "Yemen", "Sudan", "Venezuela"
            ],
            "financial_threshold": 500000,
            "currency": "BTH",
            "special_rules": {
                "thailand_residents": {
                    "description": "Special rules for Thailand residents",
                    "required_visa_types": ["Tourist", "Education", "Retirement", "Other"],
                    "financial_multiplier": 1.2
                }
            }
        }
    
    def evaluate_prospect(self, prospect_data):
        """
        Evaluate prospect based on business rules
        
        Args:
            prospect_data (dict): Prospect information
            
        Returns:
            dict: Qualification result with reason and message
        """
        try:
            nationality = prospect_data.get('nationality', '').strip()
            current_location = prospect_data.get('current_location', '').strip()
            financial_status = prospect_data.get('financial_status', False)
            current_visa_type = prospect_data.get('current_visa_type', '').strip()
            
            # Rule 1: Check blocked nationalities
            blocked_nationalities = self.rules.get('blocked_nationalities', [])
            if nationality in blocked_nationalities:
                return {
                    "qualified": False,
                    "reason": "blocked_nationality",
                    "message": f"Unfortunately, we cannot process applications for {nationality} nationals at this time due to current regulations.",
                    "details": {
                        "nationality": nationality,
                        "rule": "blocked_nationalities"
                    }
                }
            
            # Rule 2: Check financial requirements
            if not financial_status:
                financial_threshold = self.rules.get('financial_threshold', 500000)
                currency = self.rules.get('currency', 'BTH')
                
                return {
                    "qualified": False,
                    "reason": "insufficient_funds",
                    "message": f"Thailand visa applications require a minimum of {financial_threshold:,} {currency} in bank statements. Please ensure you meet this requirement before applying.",
                    "details": {
                        "required_amount": financial_threshold,
                        "currency": currency,
                        "rule": "financial_threshold"
                    }
                }
            
            # Rule 3: Special rules for Thailand residents
            special_rules = self.rules.get('special_rules', {})
            thailand_rules = special_rules.get('thailand_residents', {})
            
            if current_location.lower() in ['thailand', 'thai']:
                required_visa_types = thailand_rules.get('required_visa_types', [])
                if current_visa_type and current_visa_type not in required_visa_types:
                    return {
                        "qualified": False,
                        "reason": "invalid_visa_type",
                        "message": f"For Thailand residents, we require specific visa types. Your current visa type '{current_visa_type}' may need additional documentation.",
                        "details": {
                            "current_visa": current_visa_type,
                            "required_types": required_visa_types,
                            "rule": "thailand_residents"
                        }
                    }
            
            # If all rules pass, prospect is qualified
            return {
                "qualified": True,
                "reason": "meets_requirements",
                "message": "Congratulations! You meet our initial qualification criteria for Thailand visa consultation. Our team will contact you shortly to discuss your options.",
                "details": {
                    "nationality": nationality,
                    "financial_status": "confirmed",
                    "location": current_location,
                    "rules_passed": ["nationality_check", "financial_check"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error evaluating prospect: {e}")
            return {
                "qualified": False,
                "reason": "evaluation_error",
                "message": "We encountered an issue processing your application. Please try again or contact support.",
                "details": {
                    "error": str(e)
                }
            }
    
    def get_qualification_summary(self, prospect_data):
        """
        Get detailed qualification summary
        
        Args:
            prospect_data (dict): Prospect information
            
        Returns:
            dict: Detailed qualification analysis
        """
        result = self.evaluate_prospect(prospect_data)
        
        summary = {
            "prospect_email": prospect_data.get('email'),
            "prospect_name": prospect_data.get('full_name'),
            "qualification_result": result,
            "rules_applied": {
                "nationality_check": {
                    "nationality": prospect_data.get('nationality'),
                    "blocked": prospect_data.get('nationality') in self.rules.get('blocked_nationalities', []),
                    "status": "pass" if prospect_data.get('nationality') not in self.rules.get('blocked_nationalities', []) else "fail"
                },
                "financial_check": {
                    "meets_requirement": prospect_data.get('financial_status', False),
                    "required_amount": self.rules.get('financial_threshold', 500000),
                    "status": "pass" if prospect_data.get('financial_status') else "fail"
                }
            }
        }
        
        return summary
    
    def reload_rules(self):
        """Reload business rules from file"""
        self.rules = self._load_rules()
        logger.info("Business rules reloaded")
        return self.rules 