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

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize components
contact_handler = ContactHandler()
form_processor = FormProcessor()
qualification_engine = QualificationEngine()

# Initialize integrations
gmail_client = GmailClient()
whatsapp_client = WhatsAppClient()
sheets_client = SheetsClient()
calendly_client = CalendlyClient()

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

@app.route('/webhook/forms', methods=['POST'])
def forms_webhook():
    """Google Forms webhook endpoint"""
    try:
        data = request.get_json()
        logger.info(f"Forms webhook received: {data}")
        
        # Process form submission
        result = form_processor.process_submission(data)
        
        return jsonify({"status": "received", "result": result})
        
    except Exception as e:
        logger.error(f"Forms webhook error: {e}")
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting VisaT application on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug) 