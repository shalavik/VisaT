#!/usr/bin/env python3
"""
WhatsApp Message Detection Engine
Advanced multi-strategy message detection with duplicate prevention
"""

import time
import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logger = logging.getLogger(__name__)

@dataclass
class DetectedMessage:
    """Data class for detected WhatsApp messages"""
    contact_name: str
    contact_id: str
    unread_count: int
    chat_element: any
    timestamp: float
    confidence_score: float
    detection_method: str

class MessageDetector(ABC):
    """Abstract base class for message detection strategies"""
    
    @abstractmethod
    def detect(self, driver: WebDriver) -> List[DetectedMessage]:
        """Detect new messages using this strategy"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this detection strategy"""
        pass

class CSSBasedDetector(MessageDetector):
    """Primary CSS selector-based message detection"""
    
    def __init__(self):
        # Multiple CSS selectors for different WhatsApp Web versions
        self.selectors = [
            # Primary selectors (most common)
            'div[data-testid="cell-frame-container"] span[aria-label*="unread"]',
            # Alternative selectors for different layouts
            'div[data-testid="cell-frame-container"] span[data-testid="icon-unread-count"]',
            'div[data-testid="cell-frame-container"] div[data-testid="unread-count"]',
            # Fallback selectors
            '[data-testid="cell-frame-container"] span[class*="unread"]',
            'div[data-testid="chat"] span[aria-label*="unread"]'
        ]
    
    def detect(self, driver: WebDriver) -> List[DetectedMessage]:
        """Detect messages using CSS selectors"""
        detected_messages = []
        
        for selector in self.selectors:
            try:
                unread_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in unread_elements:
                    try:
                        message = self._process_unread_element(element, driver)
                        if message:
                            detected_messages.append(message)
                    except Exception as e:
                        logger.debug(f"Error processing unread element: {e}")
                        continue
                
                # If we found messages with this selector, break
                if detected_messages:
                    break
                    
            except Exception as e:
                logger.debug(f"CSS selector '{selector}' failed: {e}")
                continue
        
        return detected_messages
    
    def _process_unread_element(self, element, driver: WebDriver) -> Optional[DetectedMessage]:
        """Process a single unread element to extract message info"""
        try:
            # Get the chat container
            chat_container = element.find_element(By.XPATH, './ancestor::div[@data-testid="cell-frame-container"]')
            
            # Extract contact name
            contact_name = self._extract_contact_name(chat_container, driver)
            if not contact_name:
                return None
            
            # Extract unread count
            unread_count = self._extract_unread_count(element)
            
            # Generate contact ID
            contact_id = self._generate_contact_id(contact_name, chat_container)
            
            return DetectedMessage(
                contact_name=contact_name,
                contact_id=contact_id,
                unread_count=unread_count,
                chat_element=chat_container,
                timestamp=time.time(),
                confidence_score=0.9,  # High confidence for CSS detection
                detection_method="css_selector"
            )
            
        except Exception as e:
            logger.debug(f"Error processing unread element: {e}")
            return None
    
    def _extract_contact_name(self, chat_container, driver: WebDriver) -> Optional[str]:
        """Extract contact name from chat container"""
        name_selectors = [
            'span[data-testid="conversation-info-header-chat-title"]',
            'span[title]',
            'div[data-testid="cell-frame-title"] span',
            'span[class*="title"]'
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
    
    def _extract_unread_count(self, element) -> int:
        """Extract unread message count"""
        try:
            aria_label = element.get_attribute('aria-label') or ''
            text = element.text or ''
            
            # Try to extract number from aria-label
            if 'unread' in aria_label.lower():
                import re
                numbers = re.findall(r'\d+', aria_label)
                if numbers:
                    return int(numbers[0])
            
            # Try to extract from text
            if text.isdigit():
                return int(text)
            
            return 1  # Default to 1 if can't determine count
            
        except:
            return 1
    
    def _generate_contact_id(self, contact_name: str, chat_container) -> str:
        """Generate unique contact ID"""
        try:
            # Try to get a more unique identifier
            chat_id = chat_container.get_attribute('data-id') or chat_container.get_attribute('id')
            if chat_id:
                return f"{contact_name}_{chat_id}"
            else:
                return f"{contact_name}_{hash(contact_name) % 10000}"
        except:
            return f"{contact_name}_{hash(contact_name) % 10000}"
    
    def get_strategy_name(self) -> str:
        return "css_based_detector"

class UnreadCountDetector(MessageDetector):
    """Fallback detector based on unread count indicators"""
    
    def detect(self, driver: WebDriver) -> List[DetectedMessage]:
        """Detect using unread count indicators"""
        detected_messages = []
        
        try:
            # Look for any elements with unread indicators
            unread_indicators = driver.find_elements(
                By.XPATH, 
                "//*[contains(@aria-label, 'unread') or contains(text(), 'unread') or @data-testid='icon-unread-count']"
            )
            
            for indicator in unread_indicators:
                try:
                    message = self._process_unread_indicator(indicator, driver)
                    if message:
                        detected_messages.append(message)
                except Exception as e:
                    logger.debug(f"Error processing unread indicator: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"UnreadCountDetector failed: {e}")
        
        return detected_messages
    
    def _process_unread_indicator(self, indicator, driver: WebDriver) -> Optional[DetectedMessage]:
        """Process unread indicator to extract message info"""
        try:
            # Find nearest chat container
            chat_container = self._find_chat_container(indicator)
            if not chat_container:
                return None
            
            # Extract contact name using multiple strategies
            contact_name = self._extract_contact_name_fallback(chat_container)
            if not contact_name:
                return None
            
            return DetectedMessage(
                contact_name=contact_name,
                contact_id=f"{contact_name}_{hash(contact_name) % 10000}",
                unread_count=1,
                chat_element=chat_container,
                timestamp=time.time(),
                confidence_score=0.7,  # Medium confidence
                detection_method="unread_count"
            )
            
        except Exception as e:
            logger.debug(f"Error processing unread indicator: {e}")
            return None
    
    def _find_chat_container(self, element):
        """Find the nearest chat container element"""
        try:
            # Try multiple parent traversal strategies
            parent_selectors = [
                './ancestor::div[@data-testid="cell-frame-container"]',
                './ancestor::div[contains(@class, "chat")]',
                './ancestor::div[@role="listitem"]',
                './parent::div/parent::div'
            ]
            
            for selector in parent_selectors:
                try:
                    container = element.find_element(By.XPATH, selector)
                    return container
                except:
                    continue
            
            return None
            
        except:
            return None
    
    def _extract_contact_name_fallback(self, container) -> Optional[str]:
        """Extract contact name using fallback methods"""
        try:
            # Multiple text extraction strategies
            text_elements = container.find_elements(By.XPATH, ".//span | .//div")
            
            for elem in text_elements:
                text = elem.text
                if text and len(text) > 2 and len(text) < 50:
                    # Filter out common non-name text
                    excluded_text = ['unread', 'online', 'typing', 'last seen', ':', '+']
                    if not any(exc in text.lower() for exc in excluded_text):
                        return text.strip()
            
            return None
            
        except:
            return None
    
    def get_strategy_name(self) -> str:
        return "unread_count_detector"

class TimestampBasedDetector(MessageDetector):
    """Detector based on message timestamps for recent messages"""
    
    def detect(self, driver: WebDriver) -> List[DetectedMessage]:
        """Detect recent messages based on timestamps"""
        detected_messages = []
        
        try:
            # Look for chat elements with recent timestamps
            chat_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="cell-frame-container"]')
            
            for chat_elem in chat_elements:
                try:
                    message = self._analyze_chat_timestamp(chat_elem)
                    if message:
                        detected_messages.append(message)
                except Exception as e:
                    logger.debug(f"Error analyzing chat timestamp: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"TimestampBasedDetector failed: {e}")
        
        return detected_messages
    
    def _analyze_chat_timestamp(self, chat_element) -> Optional[DetectedMessage]:
        """Analyze chat element for recent activity"""
        try:
            # Look for timestamp indicators of recent activity
            timestamp_indicators = ['now', 'just now', '1 min', '2 min', '3 min']
            
            text_elements = chat_element.find_elements(By.XPATH, ".//span | .//div")
            
            for elem in text_elements:
                text = elem.text.lower()
                if any(indicator in text for indicator in timestamp_indicators):
                    # Found recent activity, extract contact name
                    contact_name = self._extract_contact_name_from_chat(chat_element)
                    if contact_name:
                        return DetectedMessage(
                            contact_name=contact_name,
                            contact_id=f"{contact_name}_{hash(contact_name) % 10000}",
                            unread_count=1,
                            chat_element=chat_element,
                            timestamp=time.time(),
                            confidence_score=0.6,  # Lower confidence
                            detection_method="timestamp_based"
                        )
            
            return None
            
        except Exception as e:
            logger.debug(f"Error analyzing timestamp: {e}")
            return None
    
    def _extract_contact_name_from_chat(self, chat_element) -> Optional[str]:
        """Extract contact name from chat element"""
        name_selectors = [
            'span[title]',
            'div[title]',
            'span[data-testid*="title"]'
        ]
        
        for selector in name_selectors:
            try:
                name_element = chat_element.find_element(By.CSS_SELECTOR, selector)
                name = name_element.get_attribute('title') or name_element.text
                if name and name.strip():
                    return name.strip()
            except:
                continue
        
        return None
    
    def get_strategy_name(self) -> str:
        return "timestamp_based_detector"

class DuplicatePreventionManager:
    """Manages duplicate message prevention with cooldown periods"""
    
    def __init__(self):
        self.response_history: Dict[str, float] = {}
        self.processed_messages: Set[str] = set()
        self.cooldown_periods = {
            'default': 300,      # 5 minutes default
            'first_time': 0,     # No cooldown for first contact
            'repeat': 3600,      # 1 hour for repeat contacts
            'recent': 180        # 3 minutes for very recent contacts
        }
        self.max_history_size = 1000
    
    def can_respond_to(self, contact_id: str) -> Tuple[bool, str]:
        """
        Check if we can respond to this contact
        
        Returns:
            tuple: (can_respond, reason)
        """
        current_time = time.time()
        
        # Check if this is a first-time contact
        if contact_id not in self.response_history:
            return True, "first_time_contact"
        
        # Check cooldown period
        last_response_time = self.response_history[contact_id]
        time_since_last = current_time - last_response_time
        
        # Determine appropriate cooldown
        if time_since_last < self.cooldown_periods['recent']:
            cooldown = self.cooldown_periods['recent']
        elif contact_id in self.response_history:
            cooldown = self.cooldown_periods['repeat']
        else:
            cooldown = self.cooldown_periods['default']
        
        if time_since_last >= cooldown:
            return True, f"cooldown_expired_{int(time_since_last)}s"
        else:
            remaining = cooldown - time_since_last
            return False, f"cooldown_active_{int(remaining)}s_remaining"
    
    def mark_response_sent(self, contact_id: str):
        """Mark that we've sent a response to this contact"""
        self.response_history[contact_id] = time.time()
        self.processed_messages.add(f"{contact_id}_{int(time.time())}")
        
        # Cleanup old history
        self._cleanup_old_history()
    
    def is_message_processed(self, message: DetectedMessage) -> bool:
        """Check if this specific message has been processed"""
        message_key = f"{message.contact_id}_{int(message.timestamp)}"
        return message_key in self.processed_messages
    
    def _cleanup_old_history(self):
        """Clean up old history to prevent memory leaks"""
        current_time = time.time()
        
        # Remove entries older than 24 hours
        old_threshold = current_time - 86400  # 24 hours
        
        # Clean response history
        old_contacts = [
            contact_id for contact_id, timestamp in self.response_history.items()
            if timestamp < old_threshold
        ]
        for contact_id in old_contacts:
            del self.response_history[contact_id]
        
        # Clean processed messages
        if len(self.processed_messages) > self.max_history_size:
            # Keep only the most recent entries
            sorted_messages = sorted(self.processed_messages)
            self.processed_messages = set(sorted_messages[-self.max_history_size//2:])
    
    def get_statistics(self) -> Dict:
        """Get duplicate prevention statistics"""
        current_time = time.time()
        
        return {
            'total_contacts_tracked': len(self.response_history),
            'messages_processed': len(self.processed_messages),
            'recent_responses_1h': sum(
                1 for timestamp in self.response_history.values()
                if current_time - timestamp < 3600
            ),
            'cooldown_periods': self.cooldown_periods
        }

class MessageDetectionEngine:
    """Main message detection engine coordinating multiple strategies"""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.detectors = [
            CSSBasedDetector(),
            UnreadCountDetector(),
            TimestampBasedDetector()
        ]
        self.duplicate_manager = DuplicatePreventionManager()
        self.performance_stats = {
            'total_detections': 0,
            'successful_responses': 0,
            'duplicate_preventions': 0,
            'detection_errors': 0
        }
    
    def detect_new_messages(self) -> List[DetectedMessage]:
        """
        Detect new messages using multiple strategies
        
        Returns:
            list: Filtered list of messages ready for response
        """
        all_detected = []
        
        # Run all detection strategies
        for detector in self.detectors:
            try:
                messages = detector.detect(self.driver)
                all_detected.extend(messages)
                logger.debug(f"{detector.get_strategy_name()} detected {len(messages)} messages")
            except Exception as e:
                logger.error(f"Error in {detector.get_strategy_name()}: {e}")
                self.performance_stats['detection_errors'] += 1
        
        # Consolidate and filter results
        consolidated = self._consolidate_messages(all_detected)
        filtered = self._filter_messages(consolidated)
        
        self.performance_stats['total_detections'] += len(filtered)
        
        return filtered
    
    def _consolidate_messages(self, messages: List[DetectedMessage]) -> List[DetectedMessage]:
        """Consolidate duplicate messages from different detectors"""
        if not messages:
            return []
        
        # Group by contact name
        contact_groups = {}
        for msg in messages:
            if msg.contact_name not in contact_groups:
                contact_groups[msg.contact_name] = []
            contact_groups[msg.contact_name].append(msg)
        
        # Select best message for each contact
        consolidated = []
        for contact_name, contact_messages in contact_groups.items():
            # Sort by confidence score, then by detection method preference
            best_message = max(contact_messages, key=lambda m: (
                m.confidence_score,
                1 if m.detection_method == "css_selector" else 0
            ))
            consolidated.append(best_message)
        
        return consolidated
    
    def _filter_messages(self, messages: List[DetectedMessage]) -> List[DetectedMessage]:
        """Filter messages based on duplicate prevention and validation"""
        filtered = []
        
        for message in messages:
            # Check if already processed
            if self.duplicate_manager.is_message_processed(message):
                logger.debug(f"Message already processed: {message.contact_name}")
                self.performance_stats['duplicate_preventions'] += 1
                continue
            
            # Check cooldown
            can_respond, reason = self.duplicate_manager.can_respond_to(message.contact_id)
            if not can_respond:
                logger.debug(f"Cannot respond to {message.contact_name}: {reason}")
                self.performance_stats['duplicate_preventions'] += 1
                continue
            
            # Validate message
            if self._validate_message(message):
                filtered.append(message)
            else:
                logger.debug(f"Message validation failed: {message.contact_name}")
        
        return filtered
    
    def _validate_message(self, message: DetectedMessage) -> bool:
        """Validate message before processing"""
        # Basic validation
        if not message.contact_name or len(message.contact_name.strip()) < 2:
            return False
        
        # Filter out system messages or invalid contacts
        invalid_names = ['whatsapp', 'system', 'broadcast', 'announcement']
        if any(invalid in message.contact_name.lower() for invalid in invalid_names):
            return False
        
        return True
    
    def mark_message_processed(self, message: DetectedMessage):
        """Mark message as processed to prevent duplicates"""
        self.duplicate_manager.mark_response_sent(message.contact_id)
        self.performance_stats['successful_responses'] += 1
    
    def get_performance_stats(self) -> Dict:
        """Get detection engine performance statistics"""
        stats = self.performance_stats.copy()
        stats.update(self.duplicate_manager.get_statistics())
        return stats 