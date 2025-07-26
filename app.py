#!/usr/bin/env python3
"""
VisaT - Visa Consulting Automation System
Main Flask Application
"""

import os
import asyncio
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import VisaT modules
from src.handlers.contact_handler import ContactHandler
from src.handlers.form_processor import FormProcessor
from src.engines.qualification_engine import QualificationEngine
from src.integrations.gmail_client import GmailClient
from src.integrations.whatsapp_client import WhatsAppClient
from src.integrations.sheets_client import SheetsClient
from src.integrations.calendly_client import CalendlyClient
from src.integrations.sheets_monitor import SheetsMonitor
from src.integrations.calendly_poller import CalendlyPoller
from src.integrations.calendly_poller import CalendlyPoller

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize components
contact_handler = ContactHandler()
form_processor = FormProcessor()
calendly_poller = CalendlyPoller()
qualification_engine = QualificationEngine()

# Initialize integrations
gmail_client = GmailClient()
whatsapp_client = WhatsAppClient()
sheets_client = SheetsClient()
calendly_client = CalendlyClient()

# Initialize the sheets monitor
sheets_monitor = SheetsMonitor()

# Add after the existing imports
from src.integrations.calendly_poller import CalendlyPoller

# Add after other global instances (near where form_processor is defined)
calendly_poller = CalendlyPoller()

# Calendly Polling API Endpoints
@app.route('/api/calendly/poll/start', methods=['POST'])
def start_calendly_polling():
    """Start Calendly polling (every 5 minutes)"""
    try:
        calendly_poller.start_polling()
        return jsonify({
            "status": "success",
            "message": "Calendly polling started (every 5 minutes)"
        })
    except Exception as e:
        logger.error(f"Failed to start Calendly polling: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/calendly/poll/stop', methods=['POST'])
def stop_calendly_polling():
    """Stop Calendly polling"""
    try:
        calendly_poller.stop_polling()
        return jsonify({
            "status": "success",
            "message": "Calendly polling stopped"
        })
    except Exception as e:
        logger.error(f"Failed to stop Calendly polling: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/calendly/poll/status', methods=['GET'])
def get_calendly_polling_status():
    """Get Calendly polling status"""
    try:
        status = calendly_poller.get_status()
        return jsonify({
            "status": "success",
            "data": status
        })
    except Exception as e:
        logger.error(f"Failed to get Calendly polling status: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/calendly/poll', methods=['POST'])
def manual_calendly_poll():
    """Manually trigger Calendly polling"""
    try:
        result = calendly_poller.manual_poll()
        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Failed to manually poll Calendly: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "VisaT - Visa Consulting Automation",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """WhatsApp webhook endpoint"""
    try:
        if request.method == 'GET':
            # Webhook verification
            verify_token = request.args.get('hub.verify_token')
            if verify_token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
                logger.info("WhatsApp webhook verified successfully")
                return request.args.get('hub.challenge')
            logger.warning("WhatsApp webhook verification failed")
            return 'Verification failed', 403
        
        elif request.method == 'POST':
            # Process incoming WhatsApp message
            data = request.get_json()
            logger.info(f"WhatsApp webhook received: {data}")
            
            # Handle message asynchronously
            result = contact_handler.handle_whatsapp_message(data)
            
            return jsonify({"status": "received", "result": result})
            
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        return jsonify({"error": "Processing failed"}), 500
    
@app.route('/api/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    """WhatsApp message sending endpoint"""
    try:
        data = request.get_json()
        logger.info(f"WhatsApp send request received: {data}")
        
        # Validate required fields
        if not all(k in data for k in ['to', 'template_name']):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Get WhatsApp access token from environment
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        if not access_token:
            logger.error("WhatsApp access token not found in environment")
            return jsonify({"error": "Configuration error"}), 500
        
        # Send message using WhatsApp client
        result = whatsapp_client.send_template_message(
            to=data['to'],
            template_name=data['template_name'],
            template_params=data.get('template_params', {}),
            access_token=access_token
        )
        
        logger.info(f"WhatsApp message sent: {result}")
        return jsonify({"status": "sent", "result": result})
        
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return jsonify({"error": "Sending failed"}), 500

@app.route('/webhook/facebook', methods=['GET', 'POST'])
def facebook_webhook():
    """Facebook Messenger webhook endpoint"""
    try:
        if request.method == 'GET':
            # Webhook verification
            verify_token = request.args.get('hub.verify_token')
            if verify_token == os.getenv('FACEBOOK_VERIFY_TOKEN'):
                logger.info("Facebook webhook verified successfully")
                return request.args.get('hub.challenge')
            logger.warning("Facebook webhook verification failed")
            return 'Verification failed', 403
        
        elif request.method == 'POST':
            # Process incoming Facebook message
            data = request.get_json()
            logger.info(f"Facebook webhook received: {data}")
            
            # Handle message asynchronously
            result = contact_handler.handle_facebook_message(data)
            
            return jsonify({"status": "received", "result": result})
            
    except Exception as e:
        logger.error(f"Facebook webhook error: {e}")
        return jsonify({"error": "Processing failed"}), 500

def map_form_data(raw_data):
    """Map Google Forms field names to expected keys"""
    try:
        mapped_data = {}
        
        # Define field mappings
        field_mappings = {
            'Your Full Name (as on passport)': 'name',
            'Your Full Name': 'name',  # Alternative
            'Your Email Address': 'email',
            'Email Address': 'email',  # Alternative
            'Your Nationality': 'nationality',
            'Nationality': 'nationality',  # Alternative
            'Country of Current': 'current_location',
            'Current Country': 'current_location',  # Alternative
            'Do you have more than 500,000 THB': 'financial_status',
            'Do you have more than 500k BTH in your bank account?': 'financial_status',  # Alternative
            'If you are currently in Thailand': 'current_visa_type',
            'Your WhatsApp Number (include country code)': 'whatsapp_number',
            'Your WhatsApp Number': 'whatsapp_number',  # Alternative
            'WhatsApp Number (with country code)': 'whatsapp_number'  # Alternative
        }
        
        # Map fields
        for form_field, value in raw_data.items():
            if form_field in field_mappings:
                mapped_key = field_mappings[form_field]
                mapped_data[mapped_key] = value
            else:
                # Keep unmapped fields as-is
                mapped_data[form_field] = value
        
        # Convert financial status to boolean
        if 'financial_status' in mapped_data:
            financial_answer = str(mapped_data['financial_status']).lower()
            mapped_data['financial_status'] = financial_answer in ['yes', 'true', '1', 'อยู่']
        
        # Ensure we have required fields
        if 'email' not in mapped_data:
            mapped_data['email'] = 'unknown'
        
        if 'name' not in mapped_data:
            mapped_data['name'] = mapped_data.get('email', 'Anonymous')
        
        logger.info(f"📋 Mapped form data: {mapped_data}")
        return mapped_data
        
    except Exception as e:
        logger.error(f"Error mapping form data: {e}")
        return raw_data

@app.route('/webhook/forms', methods=['POST'])
def forms_webhook():
    """Google Forms webhook endpoint"""
    try:
        raw_data = request.get_json()
        logger.info(f"📋 Forms webhook received raw data: {raw_data}")
        
        # Map form field names to expected keys
        mapped_data = map_form_data(raw_data)
        
        # Process form submission
        result = form_processor.process_form_submission(mapped_data)
        
        logger.info(f"📊 Form processing result: {result}")
        return jsonify({"status": "received", "result": result})
        
    except Exception as e:
        logger.error(f"Forms webhook error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"error": "Processing failed"}), 500

@app.route('/api/qualify', methods=['POST'])
def qualify_lead():
    """Manual lead qualification endpoint for testing"""
    try:
        data = request.get_json()
        
        # Validate input data
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Process qualification
        result = qualification_engine.evaluate_prospect(data)
        
        logger.info(f"Manual qualification result: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Qualification error: {e}")
        return jsonify({"error": "Qualification failed"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        # Get basic stats from Google Sheets
        stats = sheets_client.get_lead_statistics()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            "error": "Stats unavailable",
            "fallback_stats": {
                "total_leads": 0,
                "qualified_leads": 0,
                "appointments_booked": 0,
                "conversion_rate": 0.0
            }
        }), 200

@app.route('/api/test-whatsapp', methods=['POST'])
def test_whatsapp():
    """Test WhatsApp message sending"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"error": "Phone and message required"}), 400
            
        result = whatsapp_client.send_message(phone, message)
        return jsonify({"status": "sent", "result": result})
        
    except Exception as e:
        logger.error(f"WhatsApp test error: {e}")
        return jsonify({"error": "Test failed"}), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email sending"""
    try:
        data = request.get_json()
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not email or not subject or not message:
            return jsonify({"error": "Email, subject, and message required"}), 400
            
        result = gmail_client.send_email(email, subject, message)
        return jsonify({"status": "sent", "result": result})
        
    except Exception as e:
        logger.error(f"Email test error: {e}")
        return jsonify({"error": "Test failed"}), 500

@app.route('/api/test-follow-up', methods=['POST'])
def test_follow_up():
    """Test follow-up message functionality"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        name = data.get('name', 'Test User')
        qualified = data.get('qualified', True)
        
        if not phone:
            return jsonify({"error": "Phone number required"}), 400
        
        # Test the complete follow-up flow
        result = whatsapp_client.send_follow_up(phone, name, qualified)
        return jsonify({"status": "tested", "result": result})
        
    except Exception as e:
        logger.error(f"Follow-up test error: {e}")
        return jsonify({"error": "Follow-up test failed"}), 500

@app.route('/api/whatsapp-status', methods=['GET'])
def whatsapp_status():
    """Get WhatsApp client status"""
    try:
        status = whatsapp_client.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"WhatsApp status error: {e}")
        return jsonify({"error": "Failed to get WhatsApp status"}), 500

@app.route('/api/whatsapp-restart', methods=['POST'])
def whatsapp_restart():
    """Restart WhatsApp personal session"""
    try:
        if whatsapp_client.get_mode() == 'personal':
            success = whatsapp_client.restart_personal_session()
            return jsonify({
                "status": "success" if success else "failed",
                "message": "Personal WhatsApp session restart attempted"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Restart only available for personal mode"
            }), 400
    except Exception as e:
        logger.error(f"WhatsApp restart error: {e}")
        return jsonify({"error": "Failed to restart WhatsApp session"}), 500

@app.route('/api/whatsapp-start', methods=['POST'])
def whatsapp_start():
    """Start WhatsApp personal session"""
    try:
        if whatsapp_client.get_mode() == 'personal':
            success = whatsapp_client.start_personal_session()
            return jsonify({
                "status": "success" if success else "failed",
                "message": "Personal WhatsApp session start attempted"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Start only available for personal mode"
            }), 400
    except Exception as e:
        logger.error(f"WhatsApp start error: {e}")
        return jsonify({"error": "Failed to start WhatsApp session"}), 500

@app.route('/api/whatsapp-stop', methods=['POST'])
def whatsapp_stop():
    """Stop WhatsApp personal session"""
    try:
        if whatsapp_client.get_mode() == 'personal':
            success = whatsapp_client.stop_personal_session()
            return jsonify({
                "status": "success" if success else "failed",
                "message": "Personal WhatsApp session stop attempted"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Stop only available for personal mode"
            }), 400
    except Exception as e:
        logger.error(f"WhatsApp stop error: {e}")
        return jsonify({"error": "Failed to stop WhatsApp session"}), 500

@app.route('/api/whatsapp-force-monitoring', methods=['POST'])
def whatsapp_force_monitoring():
    """Force start WhatsApp message monitoring"""
    try:
        if whatsapp_client.get_mode() == 'personal':
            success = whatsapp_client.start_monitoring(force=True)
            return jsonify({
                "status": "success" if success else "failed",
                "message": "WhatsApp monitoring force started"
            })
        else:
            return jsonify({"error": "Only available in personal mode"}), 400
    except Exception as e:
        logger.error(f"Error force starting monitoring: {e}")
        return jsonify({"error": "Failed to force start monitoring"}), 500

@app.route('/api/whatsapp-template-status', methods=['GET'])
def whatsapp_template_status():
    """Get WhatsApp template system status"""
    try:
        from src.utils.whatsapp_templates import template_manager
        
        # Get current template
        current_template = template_manager.get_auto_reply_template()
        validation = template_manager.validate_template(current_template)
        
        return jsonify({
            "current_template_type": os.getenv('WHATSAPP_AUTO_REPLY_TEMPLATE', 'default'),
            "available_templates": template_manager.get_available_templates(),
            "template_validation": validation,
            "template_preview": current_template[:200] + "..." if len(current_template) > 200 else current_template,
            "consultant_name": os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava')
        })
        
    except Exception as e:
        logger.error(f"Template status error: {e}")
        return jsonify({"error": "Template status failed"}), 500

@app.route('/api/whatsapp-session-status', methods=['GET'])
def whatsapp_session_status():
    """Get WhatsApp session management status (Personal mode only)"""
    try:
        if whatsapp_client.get_mode() != 'personal':
            return jsonify({
                "error": "Session status only available in personal mode",
                "current_mode": whatsapp_client.get_mode()
            }), 400
        
        # Get session manager status from personal client
        client = whatsapp_client.client
        if hasattr(client, 'session_manager'):
            session_status = client.session_manager.get_session_status()
            return jsonify({
                "session_management": session_status,
                "whatsapp_status": whatsapp_client.get_status()
            })
        else:
            return jsonify({
                "error": "Session manager not available",
                "whatsapp_status": whatsapp_client.get_status()
            }), 400
        
    except Exception as e:
        logger.error(f"Session status error: {e}")
        return jsonify({"error": "Session status failed"}), 500

@app.route('/api/whatsapp-performance-stats', methods=['GET'])
def whatsapp_performance_stats():
    """Get WhatsApp performance statistics (Personal mode only)"""
    try:
        if whatsapp_client.get_mode() != 'personal':
            return jsonify({
                "error": "Performance stats only available in personal mode",
                "current_mode": whatsapp_client.get_mode()
            }), 400
        
        # Get performance stats from detection engine
        client = whatsapp_client.client
        if hasattr(client, 'detection_engine') and client.detection_engine:
            stats = client.detection_engine.get_performance_stats()
            return jsonify({
                "performance_stats": stats,
                "whatsapp_status": whatsapp_client.get_status()
            })
        else:
            return jsonify({
                "error": "Detection engine not available",
                "whatsapp_status": whatsapp_client.get_status()
            }), 400
        
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return jsonify({"error": "Performance stats failed"}), 500

@app.route('/api/whatsapp-test-simplified', methods=['POST'])
def whatsapp_test_simplified():
    """Test simplified message detection manually"""
    try:
        # Get personal WhatsApp client instance
        from src.integrations.personal_whatsapp_client import PersonalWhatsAppClient
        client = PersonalWhatsAppClient.get_instance()
        
        if not client._driver:
            return jsonify({
                "status": "error",
                "message": "WhatsApp session not active"
            }), 400
        
        # Test simplified detection
        unread_selectors = [
            'span[aria-label*="unread"]',
            'div[data-testid="unread-count"]',
            'span[data-testid="icon-unread-count"]',
            'div[class*="unread"]'
        ]
        
        found_elements = []
        
        for selector in unread_selectors:
            try:
                elements = client._driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    found_elements.append({
                        "selector": selector,
                        "count": len(elements),
                        "elements": [elem.text for elem in elements[:3]]  # Show first 3
                    })
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return jsonify({
            "status": "success",
            "message": "Simplified detection test completed",
            "results": {
                "selectors_tested": len(unread_selectors),
                "selectors_with_results": len(found_elements),
                "found_elements": found_elements
            }
        })
        
    except Exception as e:
        logger.error(f"Error testing simplified detection: {e}")
        return jsonify({
            "status": "error",
            "message": f"Test failed: {str(e)}"
        }), 500

@app.route('/api/sheets-monitor/start', methods=['POST'])
def start_sheets_monitoring():
    """Start Google Sheets monitoring"""
    try:
        success = sheets_monitor.start_monitoring()
        return jsonify({
            "status": "success" if success else "failed",
            "message": "Google Sheets monitoring started" if success else "Failed to start monitoring"
        })
    except Exception as e:
        logger.error(f"Error starting sheets monitoring: {e}")
        return jsonify({"error": "Failed to start sheets monitoring"}), 500

@app.route('/api/sheets-monitor/stop', methods=['POST'])
def stop_sheets_monitoring():
    """Stop Google Sheets monitoring"""
    try:
        success = sheets_monitor.stop_monitoring()
        return jsonify({
            "status": "success" if success else "failed",
            "message": "Google Sheets monitoring stopped" if success else "Failed to stop monitoring"
        })
    except Exception as e:
        logger.error(f"Error stopping sheets monitoring: {e}")
        return jsonify({"error": "Failed to stop sheets monitoring"}), 500

@app.route('/api/sheets-monitor/status', methods=['GET'])
def sheets_monitoring_status():
    """Get Google Sheets monitoring status"""
    try:
        status = sheets_monitor.get_monitoring_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting sheets monitoring status: {e}")
        return jsonify({"error": "Failed to get monitoring status"}), 500

@app.route('/api/sheets-monitor/process', methods=['POST'])
def process_new_sheets_rows():
    """Manually trigger processing of new sheet rows"""
    try:
        success = sheets_monitor.manual_process_new_rows()
        return jsonify({
            "status": "success" if success else "failed",
            "message": "Manual processing completed" if success else "Failed to process rows"
        })
    except Exception as e:
        logger.error(f"Error processing sheets rows: {e}")
        return jsonify({"error": "Failed to process rows"}), 500

@app.route('/api/sheets-monitor/process-row', methods=['POST'])
def process_specific_row():
    """Manually process a specific row for debugging"""
    try:
        data = request.get_json()
        row_number = data.get('row_number')
        
        if not row_number:
            return jsonify({"error": "Row number required"}), 400
        
        # Get sheet data
        sheet_data = sheets_monitor._get_sheet_data()
        
        if row_number > len(sheet_data) or row_number < 1:
            return jsonify({"error": f"Invalid row number. Sheet has {len(sheet_data)} rows"}), 400
        
        # Process the specific row (convert to 0-based index)
        row_data = sheet_data[row_number - 1]
        result = sheets_monitor._process_form_submission(row_data, row_number)
        
        return jsonify({
            "status": "processed",
            "row_number": row_number,
            "row_data": row_data,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Row processing error: {e}")
        return jsonify({"error": "Row processing failed"}), 500

@app.route('/api/sheets-monitor/reset', methods=['POST'])
def reset_sheets_monitoring():
    """Reset sheets monitor to reprocess recent submissions"""
    try:
        data = request.get_json() or {}
        reprocess_last_n = data.get('reprocess_last_n', 5)  # Default to last 5 submissions
        
        # Get current sheet data
        sheet_data = sheets_monitor._get_sheet_data()
        current_rows = len(sheet_data)
        
        if current_rows == 0:
            return jsonify({"error": "No data in sheet"}), 400
        
        # Reset to process last N rows
        new_processed_row = max(0, current_rows - reprocess_last_n)
        sheets_monitor.last_processed_row = new_processed_row
        
        logger.info(f"Reset sheets monitor: will reprocess rows {new_processed_row + 1} to {current_rows}")
        
        # Trigger immediate processing
        sheets_monitor._check_for_new_submissions()
        
        return jsonify({
            "status": "reset",
            "previous_processed_row": current_rows,
            "new_processed_row": new_processed_row,
            "will_reprocess_rows": list(range(new_processed_row + 1, current_rows + 1)),
            "message": f"Reset to reprocess last {reprocess_last_n} submissions"
        })
        
    except Exception as e:
        logger.error(f"Sheets monitor reset error: {e}")
        return jsonify({"error": "Reset failed"}), 500

# =============================================================================
# CALENDLY WEBHOOK INTEGRATION
# =============================================================================

@app.route('/api/calendly/webhook', methods=['POST'])
def calendly_webhook():
    """Handle Calendly webhook events"""
    try:
        from src.integrations.calendly_webhook import CalendlyWebhookProcessor
        
        # Get raw body for signature verification
        raw_body = request.get_data()
        
        # Get signature from headers
        signature = request.headers.get('X-Calendly-Signature', '')
        
        # Parse JSON payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({
                "status": "error",
                "message": "No JSON payload received"
            }), 400
        
        # Process webhook
        processor = CalendlyWebhookProcessor()
        result = processor.process_webhook(payload, signature, raw_body)
        
        # Return appropriate status code
        if result.get("status") == "success":
            return jsonify(result), 200
        elif result.get("status") == "ignored":
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Calendly webhook error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Webhook processing failed: {str(e)}"
        }), 500

@app.route('/api/calendly/status', methods=['GET'])
def calendly_status():
    """Check Calendly integration status"""
    try:
        from src.integrations.calendly_webhook import CalendlyWebhookProcessor
        
        processor = CalendlyWebhookProcessor()
        result = processor.test_webhook_processing()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Calendly status check error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Status check failed: {str(e)}"
        }), 500

@app.route('/api/calendly/test', methods=['POST'])
def test_calendly():
    """Test Calendly webhook processing"""
    try:
        from src.integrations.calendly_webhook import CalendlyWebhookProcessor
        
        # Get test data from request or use default
        test_data = request.get_json() if request.is_json else None
        
        processor = CalendlyWebhookProcessor()
        result = processor.test_webhook_processing(test_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Calendly test error: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Test failed: {str(e)}"
        }), 500

@app.route('/api/calendly/bookings', methods=['GET'])
def get_calendly_bookings():
    """Get recent Calendly bookings"""
    try:
        from src.integrations.sheets_client_fixed import SheetsClientFixed
        import os
        
        sheet_id = os.getenv("CALENDLY_SHEET_ID")
        if not sheet_id:
            return jsonify({
                "status": "error",
                "message": "Calendly sheet ID not configured"
            }), 400
        
        # Get limit from query params
        limit = request.args.get('limit', 50, type=int)
        
        sheets_client = SheetsClientFixed()
        bookings = sheets_client.get_booking_sheet_data(sheet_id, limit)
        
        return jsonify({
            "status": "success",
            "bookings": bookings,
            "count": len(bookings)
        }), 200
        
    except Exception as e:
        logger.error(f"Get bookings error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to retrieve bookings: {str(e)}"
        }), 500

@app.route('/api/calendly/setup-headers', methods=['POST'])
def setup_calendly_headers():
    """Setup headers for Calendly bookings sheet"""
    try:
        from src.integrations.sheets_client_fixed import SheetsClientFixed
        import os
        
        sheet_id = os.getenv("CALENDLY_SHEET_ID")
        if not sheet_id:
            return jsonify({
                "status": "error",
                "message": "Calendly sheet ID not configured"
            }), 400
        
        sheets_client = SheetsClientFixed()
        success = sheets_client.create_booking_sheet_headers(sheet_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Booking sheet headers created successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to create booking sheet headers"
            }), 500
        
    except Exception as e:
        logger.error(f"Setup headers error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to setup headers: {str(e)}"
        }), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting VisaT application on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug) 