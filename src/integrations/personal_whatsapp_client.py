#!/usr/bin/env python3
"""
Personal WhatsApp Client
Selenium-based WhatsApp Web automation for personal accounts using Chrome
"""

import os
import time
import logging
import threading
import requests
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Import enhanced modules
from .whatsapp_session_manager import WhatsAppSessionManager
from .message_detection_engine import MessageDetectionEngine
from ..utils.whatsapp_templates import get_auto_reply_template

logger = logging.getLogger(__name__)

class PersonalWhatsAppClient:
    """Personal WhatsApp client using Selenium WebDriver with singleton pattern"""
    
    _instance = None
    _driver = None
    _is_logged_in = False
    _session_path = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PersonalWhatsAppClient, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            logger.info("Using existing Personal WhatsApp client instance")
            return
            
        self.poll_interval = int(os.getenv('WHATSAPP_POLL_INTERVAL', '5'))
        self.headless = os.getenv('WHATSAPP_HEADLESS', 'false').lower() == 'true'
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Use fixed session path to ensure session persistence
        base_path = os.getenv('WHATSAPP_CHROME_PROFILE_PATH', './chrome-session')
        # Create separate profile for business automation to avoid conflict with personal WhatsApp
        PersonalWhatsAppClient._session_path = f"{base_path}-business"
        
        # Initialize enhanced session manager
        self.session_manager = WhatsAppSessionManager(PersonalWhatsAppClient._session_path)
        self.detection_engine = None  # Initialize after driver is created
        
        # Ensure session directory exists
        os.makedirs(PersonalWhatsAppClient._session_path, exist_ok=True)
        
        logger.info(f"Personal WhatsApp client initialized with session path: {PersonalWhatsAppClient._session_path}")
        self._initialized = True
        
        # Auto-start session in background thread to avoid blocking app startup
        def start_session_background():
            try:
                logger.info("Auto-starting WhatsApp session in background...")
                self.start_session()
            except Exception as e:
                logger.error(f"Failed to auto-start WhatsApp session: {e}")
        
        start_thread = threading.Thread(target=start_session_background, daemon=True)
        start_thread.start()
    
    def start_session(self):
        """Start WhatsApp Web session"""
        with PersonalWhatsAppClient._lock:
            try:
                if PersonalWhatsAppClient._driver is not None:
                    logger.info("WhatsApp session already active, checking if it's still valid...")
                    try:
                        # Test if the session is still valid
                        PersonalWhatsAppClient._driver.current_url
                        logger.info("Existing session is still valid")
                        return True
                    except:
                        logger.info("Existing session is invalid, starting new session...")
                        self.stop_session()
                
                logger.info("Starting WhatsApp Web session...")
                
                # Setup Chrome options
                options = Options()
                
                # Chrome profile setup for session persistence - FIXED
                profile_path = PersonalWhatsAppClient._session_path
                os.makedirs(profile_path, exist_ok=True)
                
                # Use the profile in options
                options.add_argument(f"--user-data-dir={profile_path}")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--remote-debugging-port=9223")  # Different port to avoid conflicts
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-external-intent-requests")  # Prevent opening external apps
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Force stay in browser, don't open WhatsApp desktop app
                prefs = {
                    "profile.default_content_setting_values.notifications": 2,  # Block notifications
                    "profile.default_content_settings.popups": 0,  # Block popups
                    "profile.managed_default_content_settings.images": 1,  # Allow images
                    "protocol_handler.excluded_schemes.whatsapp": True,  # Don't handle whatsapp:// URLs
                }
                options.add_experimental_option("prefs", prefs)
                
                if self.headless:
                    options.add_argument("--headless")
                
                # Initialize driver with manually downloaded ChromeDriver
                try:
                    logger.info("Setting up ChromeDriver...")
                    
                    # Use the manually downloaded ChromeDriver
                    local_chromedriver = os.path.abspath("./chromedriver-mac-arm64/chromedriver")
                    
                    if os.path.exists(local_chromedriver) and os.access(local_chromedriver, os.X_OK):
                        logger.info(f"Using local ChromeDriver: {local_chromedriver}")
                        service = Service(local_chromedriver)
                    else:
                        # Fallback to WebDriverManager only if local doesn't exist
                        logger.info("Local ChromeDriver not found, using WebDriverManager...")
                        service = Service(ChromeDriverManager().install())
                    
                    logger.info("ChromeDriver configured successfully")
                    
                    PersonalWhatsAppClient._driver = webdriver.Chrome(service=service, options=options)
                    PersonalWhatsAppClient._driver.maximize_window()
                    
                    # Navigate to WhatsApp Web
                    PersonalWhatsAppClient._driver.get("https://web.whatsapp.com")
                    logger.info("Opened WhatsApp Web")
                
                except Exception as driver_error:
                    logger.error(f"Failed to initialize ChromeDriver: {driver_error}")
                    raise Exception(f"ChromeDriver initialization failed: {driver_error}")
                
                # Wait for WhatsApp Web to load
                PersonalWhatsAppClient._driver.get("https://web.whatsapp.com")
                
                # Wait for login - improved detection with more reliable selectors
                login_wait = 60  # Increased wait time for better reliability
                logged_in = False
                
                logger.info("Checking WhatsApp login status...")
                
                for attempt in range(login_wait):
                    try:
                        # Enhanced detection with multiple fallback selectors
                        login_selectors = [
                            # Modern WhatsApp Web selectors
                            "div[data-testid='chat-list']",
                            "div[data-testid='app-wrapper-panelheader']",
                            "div[data-testid='chatlist-header']",
                            # Fallback selectors
                            "div[id='pane-side']",
                            "div[data-testid='side']",
                            "div[data-testid='conversation-list']",
                            # Generic main interface selectors
                            "div[class*='app-wrapper-web']",
                            "div[class*='main']",
                            "header[data-testid*='header']"
                        ]
                        
                        for selector in login_selectors:
                            try:
                                element = PersonalWhatsAppClient._driver.find_element(By.CSS_SELECTOR, selector)
                                if element and element.is_displayed():
                                    logged_in = True
                                    logger.info(f"✅ Login detected using selector: {selector}")
                                    break
                            except:
                                continue
                        
                        if logged_in:
                            break
                            
                        # Check if QR code is still present (not logged in)
                        qr_present = False
                        qr_selectors = [
                            "canvas[aria-label*='qr']",
                            "canvas[aria-label*='QR']", 
                            "div[data-testid*='qr']",
                            "div[class*='qr']"
                        ]
                        
                        for qr_selector in qr_selectors:
                            try:
                                qr_element = PersonalWhatsAppClient._driver.find_element(By.CSS_SELECTOR, qr_selector)
                                if qr_element and qr_element.is_displayed():
                                    qr_present = True
                                    break
                            except:
                                continue
                        
                        if qr_present and attempt == 0:
                            logger.info("QR code detected - please scan with your phone")
                        elif not qr_present and attempt > 5:
                            # QR disappeared but main interface not detected yet - might be transitioning
                            logger.info("QR code scan detected, waiting for interface to load...")
                            
                        if attempt == 0:
                            logger.info("Waiting for WhatsApp session to be ready...")
                        time.sleep(1)
                        
                    except Exception as detection_error:
                        logger.warning(f"Error during login detection attempt {attempt}: {detection_error}")
                        time.sleep(1)
                        continue
                
                # Enhanced login confirmation with page URL check
                if not logged_in:
                    try:
                        current_url = PersonalWhatsAppClient._driver.current_url
                        if "web.whatsapp.com" in current_url and "qr" not in current_url.lower():
                            # URL suggests we're logged in even if elements weren't detected
                            logger.info("✅ Login confirmed via URL analysis")
                            logged_in = True
                    except:
                        pass
                
                if logged_in:
                    PersonalWhatsAppClient._is_logged_in = True
                    logger.info("✅ WhatsApp session is active and logged in")
                    
                    # Initialize detection engine after successful login
                    try:
                        self.detection_engine = MessageDetectionEngine(PersonalWhatsAppClient._driver)
                        logger.info("✅ Detection engine initialized successfully")
                    except Exception as engine_error:
                        logger.error(f"Failed to initialize detection engine: {engine_error}")
                        # Don't fail the session - we'll initialize it later
                    
                    # Create session backup after successful login
                    try:
                        self.session_manager.create_backup("login_success")
                    except Exception as backup_error:
                        logger.warning(f"Session backup failed: {backup_error}")
                    
                    # Auto-start message monitoring when logged in
                    logger.info("Starting message monitoring...")
                    self.start_monitoring()
                else:
                    logger.warning("⚠️ WhatsApp session timeout - please check browser window")
                    logger.info("💡 Note: You can manually start monitoring after QR scan using the API")
                    PersonalWhatsAppClient._is_logged_in = False
                
                return logged_in
                    
            except Exception as e:
                logger.error(f"Error starting WhatsApp session: {e}")
                self.stop_session()
                return False
    
    def stop_session(self):
        """Stop WhatsApp Web session"""
        with PersonalWhatsAppClient._lock:
            try:
                if PersonalWhatsAppClient._driver:
                    PersonalWhatsAppClient._driver.quit()
                    PersonalWhatsAppClient._driver = None
                    PersonalWhatsAppClient._is_logged_in = False
                    logger.info("WhatsApp session stopped")
            except Exception as e:
                logger.error(f"Error stopping WhatsApp session: {e}")
    
    def _wait_for_login(self, timeout=300):
        """Wait for WhatsApp login to complete"""
        try:
            logger.info("Waiting for WhatsApp login...")
            
            # Wait for either QR code or main interface
            wait = WebDriverWait(PersonalWhatsAppClient._driver, timeout)
            
            # Check if already logged in
            try:
                wait.until(EC.presence_of_element_located((By.ID, "pane-side")))
                logger.info("Already logged in!")
                return True
            except:
                pass
            
            # Wait for QR code scanning
            logger.info("⌛ Please scan QR code to login...")
            
            # Wait for main interface to appear
            wait.until(EC.presence_of_element_located((By.ID, "pane-side")))
            logger.info("✅ Login successful!")
            return True
            
        except Exception as e:
            logger.error(f"Login timeout or error: {e}")
            return False
    
    def send_message(self, to_phone, message):
        """
        Send WhatsApp message to a phone number
        
        Args:
            to_phone (str): Recipient phone number (with country code)
            message (str): Message text
            
        Returns:
            dict: Result of message sending
        """
        try:
            # Auto-start session if not already active
            if not PersonalWhatsAppClient._is_logged_in or not PersonalWhatsAppClient._driver:
                logger.info("Starting WhatsApp session for message sending...")
                if not self.start_session():
                    return {
                        "status": "failed",
                        "to": to_phone,
                        "error": "Failed to start WhatsApp session"
                    }
            
            logger.info(f"Sending message to {to_phone}")
            
            # Navigate to chat using phone number
            chat_url = f"https://web.whatsapp.com/send?phone={to_phone}"
            PersonalWhatsAppClient._driver.get(chat_url)
            
            # Wait for chat to load
            wait = WebDriverWait(PersonalWhatsAppClient._driver, 10)
            
            # Wait for message input box
            message_box = wait.until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//div[@contenteditable='true'][@data-tab='10']"
                ))
            )
            
            # Clear and type message
            message_box.clear()
            message_box.send_keys(message)
            
            # Send message
            message_box.send_keys(Keys.ENTER)
            
            logger.info(f"✅ Message sent to {to_phone}")
            return {
                "status": "sent",
                "to": to_phone,
                "message": "Message sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to send message to {to_phone}: {e}")
            return {
                "status": "failed",
                "to": to_phone,
                "error": str(e)
            }
    
    def send_form_link(self, to_phone, form_url):
        """
        Send Google Form link via WhatsApp
        
        Args:
            to_phone (str): Recipient phone number
            form_url (str): Google Form URL
            
        Returns:
            dict: Result of message sending
        """
        message = """🇹🇭 Thailand Visa Consultation - VisaT

Hello! Thank you for reaching out about Thailand visa services.

To provide you with the most accurate consultation, please fill out our quick assessment form:

👉 https://docs.google.com/forms/d/e/1FAIpQLScol3ZjPUuAueFf32s3-dHQiTE3oL1qmkDZGdt-YSqWffecdw/viewform?usp=sharing&ouid=114692513524380498491

This will help us:
✅ Understand your specific situation
✅ Provide personalized visa guidance
✅ Connect you with the right services

The form takes just 2-3 minutes to complete.

Best regards,
Slava - Thailand Visa Specialist"""
        
        return self.send_message(to_phone, message)
    
    def send_follow_up(self, to_phone, name, qualified=True):
        """
        Send follow-up message after form submission
        
        Args:
            to_phone (str): Recipient phone number
            name (str): Prospect name
            qualified (bool): Whether prospect is qualified
            
        Returns:
            dict: Result of message sending
        """
        if qualified:
            message = f"""🎉 Great news, {name}!

You've been pre-qualified for Thailand visa consultation! 

📧 Check your email for detailed next steps and booking information.

Our team is excited to help you with your Thailand journey! 🇹🇭

Best regards,
VisaT Team"""
        else:
            message = f"""Hi {name},

Thank you for your interest in Thailand visa services.

📧 Please check your email for helpful resources and information about visa requirements.

Feel free to reach out when you're ready to explore Thailand visa options in the future.

Best regards,
VisaT Team 🇹🇭"""
        
        return self.send_message(to_phone, message)
    
    def _check_login_status(self):
        """Check if WhatsApp Web is actually logged in by looking for UI elements"""
        try:
            if not PersonalWhatsAppClient._driver:
                return False
                
            # Use the SAME selectors that successfully detected login
            login_selectors = [
                # The EXACT selectors that work in login detection
                "div[class*='app-wrapper-web']",
                "div[data-testid='chat-list']",
                "div[data-testid='app-wrapper-panelheader']",
                "div[data-testid='chatlist-header']",
                "div[id='pane-side']",
                "div[data-testid='side']",
                "div[data-testid='conversation-list']",
                "div[class*='main']",
                "header[data-testid*='header']"
            ]
            
            # Try each selector - if ANY works, we're logged in
            for selector in login_selectors:
                try:
                    element = PersonalWhatsAppClient._driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        PersonalWhatsAppClient._is_logged_in = True
                        logger.info(f"WhatsApp login status verified - logged in (using {selector})")
                        return True
                except:
                    continue
            
            # If no login selectors worked, check for QR code
            try:
                qr_selectors = [
                    "canvas[aria-label*='qr']",
                    "canvas[aria-label*='QR']", 
                    "div[data-testid*='qr']",
                    "div[class*='qr']"
                ]
                
                for qr_selector in qr_selectors:
                    try:
                        qr_element = PersonalWhatsAppClient._driver.find_element(By.CSS_SELECTOR, qr_selector)
                        if qr_element and qr_element.is_displayed():
                            PersonalWhatsAppClient._is_logged_in = False
                            logger.info("WhatsApp login status verified - QR code visible, not logged in")
                            return False
                    except:
                        continue
                        
            except:
                pass
            
            # If we can't find login elements OR QR elements, check URL
            try:
                current_url = PersonalWhatsAppClient._driver.current_url
                if "web.whatsapp.com" in current_url and "qr" not in current_url.lower():
                    PersonalWhatsAppClient._is_logged_in = True
                    logger.info("WhatsApp login status verified via URL - logged in")
                    return True
            except:
                pass
                
            # Default to not logged in
            PersonalWhatsAppClient._is_logged_in = False
            logger.warning("Could not determine login status - assuming not logged in")
            return False
                    
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def start_monitoring(self, force=False):
        """Start monitoring for incoming WhatsApp messages"""
        if self.is_monitoring:
            logger.info("Message monitoring already active")
            return True
            
        # Check if we're actually logged in by looking for WhatsApp Web elements
        login_status = self._check_login_status()
        if not force and not login_status:
            logger.warning("Login check failed, but starting monitoring anyway (will use fallback detection)")
            # Don't return False - continue with monitoring anyway
            
        logger.info("Starting WhatsApp message monitoring...")
        self.is_monitoring = True
        
        def monitor_messages():
            """Enhanced message monitoring with multi-strategy detection"""
            if not self.detection_engine:
                logger.warning("Detection engine not initialized, attempting to initialize now...")
                try:
                    if PersonalWhatsAppClient._driver:
                        from .message_detection_engine import MessageDetectionEngine
                        self.detection_engine = MessageDetectionEngine(PersonalWhatsAppClient._driver)
                        logger.info("✅ Detection engine initialized successfully (fallback)")
                    else:
                        logger.error("❌ Cannot initialize detection engine - no WebDriver available")
                        return
                except Exception as init_error:
                    logger.error(f"❌ Failed to initialize detection engine: {init_error}")
                    logger.info("🔄 Falling back to simplified message detection...")
                    return self._simplified_message_monitoring()
            
            logger.info("Starting enhanced message monitoring with auto-reply templates...")
            
            # Log current state for debugging
            try:
                current_url = PersonalWhatsAppClient._driver.current_url
                page_title = PersonalWhatsAppClient._driver.title
                logger.info(f"🔍 Current URL: {current_url}")
                logger.info(f"🔍 Page Title: {page_title}")
            except Exception as debug_error:
                logger.warning(f"Could not get page info: {debug_error}")
            
            while self.is_monitoring and PersonalWhatsAppClient._driver:
                try:
                    # Detect new messages using advanced detection engine
                    detected_messages = self.detection_engine.detect_new_messages()
                    
                    if detected_messages:
                        logger.info(f"Detected {len(detected_messages)} new messages to process")
                    
                    # Process each detected message
                    for message in detected_messages[:3]:  # Process max 3 at a time
                        try:
                            success = self._process_detected_message(message)
                            if success:
                                # Mark as processed to prevent duplicates
                                self.detection_engine.mark_message_processed(message)
                                logger.info(f"✅ Successfully processed message from: {message.contact_name}")
                            else:
                                logger.warning(f"❌ Failed to process message from: {message.contact_name}")
                            
                            time.sleep(2)  # Wait between responses
                            
                        except Exception as chat_error:
                            logger.error(f"Error processing detected message from {message.contact_name}: {chat_error}")
                            continue
                    
                    # Performance logging
                    if detected_messages:
                        stats = self.detection_engine.get_performance_stats()
                        logger.debug(f"Detection stats: {stats}")
                    
                    time.sleep(self.poll_interval)  # Wait before next detection cycle
                    
                except Exception as monitor_error:
                    logger.error(f"Error in enhanced message monitoring: {monitor_error}")
                    time.sleep(self.poll_interval * 2)  # Wait longer on error
                    
            logger.info("Enhanced message monitoring stopped")
        
        self.monitoring_thread = threading.Thread(target=monitor_messages, daemon=True)
        self.monitoring_thread.start()
        return True
    
    def _simplified_message_monitoring(self):
        """Simplified message monitoring without detection engine"""
        logger.info("🔄 Starting simplified message monitoring...")
        
        # Debug current state
        try:
            current_url = PersonalWhatsAppClient._driver.current_url
            page_title = PersonalWhatsAppClient._driver.title
            logger.info(f"🔍 Simplified monitoring - URL: {current_url}")
            logger.info(f"🔍 Simplified monitoring - Title: {page_title}")
        except Exception as debug_error:
            logger.warning(f"Could not get page info for simplified monitoring: {debug_error}")
        
        while self.is_monitoring and PersonalWhatsAppClient._driver:
            try:
                # Simple approach: look for unread message indicators
                unread_selectors = [
                    'span[aria-label*="unread"]',
                    'div[data-testid="unread-count"]',
                    'span[data-testid="icon-unread-count"]',
                    'div[class*="unread"]'
                ]
                
                found_unread = False
                
                for selector in unread_selectors:
                    try:
                        unread_elements = PersonalWhatsAppClient._driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if unread_elements:
                            logger.info(f"Found {len(unread_elements)} unread message(s) using selector: {selector}")
                            
                            for element in unread_elements[:3]:  # Process max 3 at a time
                                try:
                                    success = self._process_unread_element_simple(element)
                                    if success:
                                        found_unread = True
                                        logger.info("✅ Successfully sent auto-reply using simplified detection")
                                        time.sleep(2)  # Wait between responses
                                except Exception as process_error:
                                    logger.error(f"Error processing unread element: {process_error}")
                                    continue
                            
                            if found_unread:
                                break  # Exit selector loop if we processed messages
                                
                    except Exception as selector_error:
                        logger.debug(f"Selector '{selector}' failed: {selector_error}")
                        continue
                
                if found_unread:
                    logger.debug("Processed unread messages, waiting before next check...")
                
                time.sleep(self.poll_interval)  # Wait before next detection cycle
                
            except Exception as monitor_error:
                logger.error(f"Error in simplified message monitoring: {monitor_error}")
                time.sleep(self.poll_interval * 2)  # Wait longer on error
                
        logger.info("Simplified message monitoring stopped")
    
    def _process_unread_element_simple(self, element) -> bool:
        """Simple processing of unread elements without detection engine"""
        try:
            # Find the chat container
            chat_container = element.find_element(By.XPATH, './ancestor::div[@data-testid="cell-frame-container"]')
            
            # Extract contact name
            contact_name = self._extract_contact_name_simple(chat_container)
            if not contact_name:
                logger.debug("Could not extract contact name, skipping")
                return False
            
            # Check if we should respond (simple cooldown)
            contact_id = f"simple_{contact_name}"
            if hasattr(self, '_simple_response_history'):
                if contact_id in self._simple_response_history:
                    time_since_last = time.time() - self._simple_response_history[contact_id]
                    if time_since_last < 300:  # 5 minute cooldown
                        logger.debug(f"Skipping {contact_name} - cooldown active")
                        return False
            else:
                self._simple_response_history = {}
            
            # Click on the chat to open it
            chat_container.click()
            time.sleep(2)
            
            # Get template message (use default template with emojis - JavaScript handles them properly)
            from ..utils.whatsapp_templates import get_auto_reply_template
            template_message = get_auto_reply_template(
                template_type='default',  # Use default template with emojis - JavaScript can handle them
                form_url=os.getenv('GOOGLE_FORM_URL', 'https://docs.google.com/forms/d/e/1FAIpQLScol3ZjPUuAueFf32s3-dHQiTE3oL1qmkDZGdt-YSqWffecdw/viewform'),
                consultant_name=os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava')
            )
            
            # Find message input and send
            success = self._send_template_message(template_message)
            
            if success:
                # Record response
                self._simple_response_history[contact_id] = time.time()
                logger.info(f"✅ Sent auto-reply to: {contact_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in simple unread processing: {e}")
            return False
    
    def _extract_contact_name_simple(self, chat_container) -> Optional[str]:
        """Simple contact name extraction"""
        name_selectors = [
            'span[data-testid="conversation-info-header-chat-title"]',
            'span[title]',
            'div[data-testid="cell-frame-title"] span',
            'span[class*="title"]',
            'div[class*="title"]'
        ]
        
        for selector in name_selectors:
            try:
                name_element = chat_container.find_element(By.CSS_SELECTOR, selector)
                name = name_element.get_attribute('title') or name_element.text
                if name and name.strip():
                    return name.strip()
            except:
                continue
        
        return None
    
    def _send_template_message(self, message: str) -> bool:
        """Send template message using JavaScript for proper formatting and emoji support"""
        try:
            # Find the message input box with multiple selector strategies
            message_box = None
            input_selectors = [
                'div[data-testid="conversation-compose-box-input"]',
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[data-testid="message-composer"]',
                'div[contenteditable="true"]'
            ]
            
            for selector in input_selectors:
                try:
                    message_box = PersonalWhatsAppClient._driver.find_element(By.CSS_SELECTOR, selector)
                    if message_box and message_box.is_displayed():
                        break
                except:
                    continue
            
            if not message_box:
                logger.error("Could not find message input box")
                return False
            
            # Use JavaScript to set the message content with proper line breaks and emoji support
            js_script = """
            function sendWhatsAppMessage(element, message) {
                try {
                    // Clear any existing content
                    element.innerHTML = '';
                    element.textContent = '';
                    
                    // Focus the element
                    element.focus();
                    
                    // Split message into lines and create proper DOM structure
                    const lines = message.split('\\n');
                    
                    for (let i = 0; i < lines.length; i++) {
                        // Add text content
                        if (lines[i].trim() !== '') {
                            element.appendChild(document.createTextNode(lines[i]));
                        }
                        
                        // Add line break except for the last line
                        if (i < lines.length - 1) {
                            element.appendChild(document.createElement('br'));
                        }
                    }
                    
                    // Trigger comprehensive input events to notify WhatsApp
                    const events = [
                        new Event('input', { bubbles: true, cancelable: true }),
                        new Event('change', { bubbles: true, cancelable: true }),
                        new Event('keyup', { bubbles: true, cancelable: true }),
                        new InputEvent('input', { bubbles: true, cancelable: true, inputType: 'insertText', data: message })
                    ];
                    
                    events.forEach(event => {
                        try {
                            element.dispatchEvent(event);
                        } catch (e) {
                            console.log('Event dispatch error:', e);
                        }
                    });
                    
                    // Wait a moment for WhatsApp to process
                    setTimeout(() => {
                        // Trigger additional events
                        const compositionEvent = new CompositionEvent('compositionend', {
                            bubbles: true,
                            cancelable: true,
                            data: message
                        });
                        element.dispatchEvent(compositionEvent);
                    }, 100);
                    
                    return true;
                } catch (error) {
                    console.error('WhatsApp message injection error:', error);
                    return false;
                }
            }
            
            return sendWhatsAppMessage(arguments[0], arguments[1]);
            """
            
            # Execute JavaScript to set the message content
            success = PersonalWhatsAppClient._driver.execute_script(js_script, message_box, message)
            
            if not success:
                logger.error("JavaScript message setting failed")
                return False
            
            # Wait longer for WhatsApp to process the content and enable send button
            time.sleep(2)
            
            # Enhanced send button detection with comprehensive selectors
            send_button = None
            send_selectors = [
                # Current WhatsApp Web send button selectors (2025)
                'button[data-testid="compose-btn-send"]',
                'span[data-testid="send"]',
                'button[aria-label*="Send"]',
                'button[title*="Send"]',
                'button[data-tab="11"]',
                'span[data-icon="send"]',
                'button[type="submit"]',
                # Parent container approach
                'div[data-testid="conversation-compose-box-send"] button',
                'div[role="button"][data-tab="11"]',
                # SVG-based detection
                'button svg[viewBox*="0 0 24 24"]',
                'span svg[data-icon="send"]',
                # Aria-label variations
                'button[aria-label*="Enviar"]',  # Spanish
                'button[aria-label*="Отправить"]',  # Russian  
                'button[aria-label*="Envoyer"]',  # French
                # Generic fallbacks
                'button:last-child',
                '[role="button"]:last-child'
            ]
            
            logger.info("Searching for send button...")
            for i, selector in enumerate(send_selectors):
                try:
                    send_button = PersonalWhatsAppClient._driver.find_element(By.CSS_SELECTOR, selector)
                    if send_button and send_button.is_displayed() and send_button.is_enabled():
                        logger.info(f"✅ Found send button using selector {i+1}: {selector}")
                        break
                    else:
                        logger.info(f"❌ Found element but not viable for selector {i+1}: {selector} (displayed={send_button.is_displayed() if send_button else None}, enabled={send_button.is_enabled() if send_button else None})")
                        send_button = None
                except Exception as selector_error:
                    logger.debug(f"Selector '{selector}' failed: {selector_error}")
                    continue
            
            if send_button:
                try:
                    # Use JavaScript to click the send button for reliability
                    PersonalWhatsAppClient._driver.execute_script("arguments[0].click();", send_button)
                    logger.debug("Send button clicked successfully")
                    return True
                except Exception as click_error:
                    logger.warning(f"Failed to click send button: {click_error}")
                    # Fall through to Enter key fallback
            
            # Fallback: Use Enter key to send message
            logger.warning("Send button not found, trying Enter key fallback...")
            try:
                # Focus on the message box and press Enter
                message_box.click()
                message_box.send_keys(Keys.RETURN)
                logger.info("✅ Message sent using Enter key fallback")
                return True
            except Exception as enter_error:
                logger.error(f"Enter key fallback failed: {enter_error}")
                
                # Final fallback: JavaScript Enter simulation
                try:
                    logger.warning("Trying JavaScript Enter key simulation...")
                    enter_script = """
                    var element = arguments[0];
                    var enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        cancelable: true
                    });
                    element.dispatchEvent(enterEvent);
                    
                    var enterUpEvent = new KeyboardEvent('keyup', {
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        which: 13,
                        bubbles: true,
                        cancelable: true
                    });
                    element.dispatchEvent(enterUpEvent);
                    return true;
                    """
                    
                    PersonalWhatsAppClient._driver.execute_script(enter_script, message_box)
                    logger.info("✅ Message sent using JavaScript Enter simulation")
                    return True
                    
                except Exception as js_enter_error:
                    logger.error(f"JavaScript Enter simulation failed: {js_enter_error}")
                    logger.error("❌ All send methods failed")
                    return False
            
        except Exception as e:
            logger.error(f"Error sending template message: {e}")
            return False
    
    def _process_detected_message(self, message) -> bool:
        """
        Process a detected message by sending auto-reply template with proper formatting
        
        Args:
            message: DetectedMessage object from detection engine
            
        Returns:
            bool: Success status
        """
        try:
            # Click on the chat to open it
            message.chat_element.click()
            time.sleep(2)
            
            # Get the template message using the default template with emojis (now properly supported)
            template_message = get_auto_reply_template(
                template_type='default',  # Use default template with emojis - JavaScript can handle them
                form_url=os.getenv('GOOGLE_FORM_URL', 'https://docs.google.com/forms/d/e/1FAIpQLScol3ZjPUuAueFf32s3-dHQiTE3oL1qmkDZGdt-YSqWffecdw/viewform'),
                consultant_name=os.getenv('WHATSAPP_TEMPLATE_CONSULTANT_NAME', 'Slava')
            )
            
            # Use the enhanced JavaScript-based message sending
            success = self._send_template_message(template_message)
            
            if success:
                logger.info(f"✅ Sent auto-reply template to: {message.contact_name}")
                return True
            else:
                logger.error(f"❌ Failed to send template to: {message.contact_name}")
                return False
            
        except Exception as e:
            logger.error(f"Error processing detected message: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop monitoring for incoming messages"""
        if self.is_monitoring:
            logger.info("Stopping WhatsApp message monitoring...")
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
        return True
    
    def get_session_status(self):
        """Get current session status"""
        # Check real-time login status
        logged_in = self._check_login_status()
        return {
            "session_active": PersonalWhatsAppClient._driver is not None,
            "logged_in": logged_in,
            "monitoring": self.is_monitoring,
            "session_path": PersonalWhatsAppClient._session_path
        }
    
    def verify_webhook(self, verify_token, challenge):
        """
        Verify webhook (compatibility with business client)
        Personal mode doesn't use webhooks, so this is a no-op
        """
        logger.info("Webhook verification called on personal client (no-op)")
        return challenge if verify_token else None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _download_chromedriver_manually(self):
        """Manual ChromeDriver download as last resort"""
        try:
            import zipfile
            
            # Create a manual download directory
            manual_driver_dir = os.path.expanduser("~/.visat_chromedriver")
            os.makedirs(manual_driver_dir, exist_ok=True)
            
            chromedriver_path = os.path.join(manual_driver_dir, "chromedriver")
            
            if not os.path.exists(chromedriver_path):
                logger.info("Downloading ChromeDriver manually...")
                # Download ChromeDriver for macOS ARM64
                url = "https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.119/mac-arm64/chromedriver-mac-arm64.zip"
                
                response = requests.get(url)
                zip_path = os.path.join(manual_driver_dir, "chromedriver.zip")
                
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(manual_driver_dir)
                
                # Find the chromedriver executable
                for root, dirs, files in os.walk(manual_driver_dir):
                    for file in files:
                        if file == 'chromedriver':
                            src_path = os.path.join(root, file)
                            os.chmod(src_path, 0o755)  # Make executable
                            if src_path != chromedriver_path:
                                import shutil
                                shutil.move(src_path, chromedriver_path)
                            break
                
                # Clean up
                os.remove(zip_path)
                for root, dirs, files in os.walk(manual_driver_dir):
                    for dir in dirs:
                        if dir.startswith('chromedriver-'):
                            import shutil
                            shutil.rmtree(os.path.join(root, dir))
            
            return chromedriver_path if os.path.exists(chromedriver_path) else None
            
        except Exception as e:
            logger.error(f"Manual ChromeDriver download failed: {e}")
            return None 