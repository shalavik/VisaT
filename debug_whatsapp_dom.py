#!/usr/bin/env python3
"""
WhatsApp DOM Debugger
Inspect WhatsApp Web DOM structure to identify correct selectors
"""

import sys
import os
sys.path.append('src')

from integrations.personal_whatsapp_client import PersonalWhatsAppClient
import time
from selenium.webdriver.common.by import By

def debug_whatsapp_dom():
    """Debug WhatsApp Web DOM structure"""
    try:
        # Get the existing WhatsApp client instance
        client = PersonalWhatsAppClient.get_instance()
        
        if not client._driver:
            print("❌ No active WhatsApp session found")
            return
            
        driver = client._driver
        
        print("🔍 DEBUGGING WHATSAPP WEB DOM STRUCTURE")
        print("=" * 50)
        
        # Check current URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check if we're in a chat
        try:
            chat_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="conversation-compose-box-input"]')
            if chat_elements:
                print("✅ Message input box found - we're in a chat")
            else:
                print("❌ Not in a chat or input box not found")
                return
        except Exception as e:
            print(f"❌ Error checking chat status: {e}")
            return
        
        # Debug send button selectors
        print("\n🔍 TESTING SEND BUTTON SELECTORS:")
        print("-" * 40)
        
        send_selectors = [
            'button[data-testid="compose-btn-send"]',
            'span[data-testid="send"]', 
            'button[aria-label*="Send"]',
            'button[title*="Send"]',
            'button[data-tab="11"]',
            'span[data-icon="send"]',
            'button[type="submit"]',
            'div[data-testid="conversation-compose-box-send"] button',
            'div[role="button"][data-tab="11"]',
            'button svg[viewBox*="0 0 24 24"]',
            'span svg[data-icon="send"]',
            'button[aria-label*="Enviar"]',
            'button[aria-label*="Отправить"]', 
            'button[aria-label*="Envoyer"]',
            'button:last-child',
            '[role="button"]:last-child'
        ]
        
        found_buttons = []
        
        for i, selector in enumerate(send_selectors):
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for j, element in enumerate(elements):
                        try:
                            is_displayed = element.is_displayed()
                            is_enabled = element.is_enabled()
                            text = element.text or element.get_attribute('aria-label') or element.get_attribute('title') or 'No text'
                            
                            print(f"Selector {i+1:2d}: {selector}")
                            print(f"           Element {j+1}: Displayed={is_displayed}, Enabled={is_enabled}")
                            print(f"           Text/Label: '{text}'")
                            
                            if is_displayed and is_enabled:
                                found_buttons.append((selector, element))
                                print(f"           ✅ VIABLE SEND BUTTON")
                            else:
                                print(f"           ❌ Not viable")
                            print()
                        except Exception as elem_error:
                            print(f"           ❌ Error inspecting element: {elem_error}")
                else:
                    print(f"Selector {i+1:2d}: {selector} - ❌ No elements found")
            except Exception as selector_error:
                print(f"Selector {i+1:2d}: {selector} - ❌ Error: {selector_error}")
        
        print(f"\n📊 SUMMARY: Found {len(found_buttons)} viable send buttons")
        
        if found_buttons:
            print("\n✅ VIABLE SEND BUTTONS:")
            for i, (selector, element) in enumerate(found_buttons):
                print(f"  {i+1}. {selector}")
        
        # Debug compose box area
        print("\n🔍 DEBUGGING COMPOSE BOX AREA:")
        print("-" * 40)
        
        try:
            compose_area = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="conversation-compose-box-input"]').find_element(By.XPATH, './..')
            html_content = compose_area.get_attribute('outerHTML')
            
            # Extract relevant parts
            lines = html_content.split('\n')
            relevant_lines = []
            for line in lines[:50]:  # First 50 lines should contain the structure
                if any(keyword in line.lower() for keyword in ['button', 'send', 'data-testid', 'role', 'aria-label']):
                    relevant_lines.append(line.strip())
            
            print("Compose box HTML structure (relevant parts):")
            for line in relevant_lines[:20]:  # Show first 20 relevant lines
                print(f"  {line}")
                
        except Exception as compose_error:
            print(f"❌ Error inspecting compose area: {compose_error}")
        
        print("\n🔍 PAGE SOURCE SNIPPET (looking for send buttons):")
        print("-" * 40)
        
        try:
            page_source = driver.page_source
            send_related_lines = []
            for line in page_source.split('\n'):
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['send', 'compose-btn', 'data-tab="11"']):
                    send_related_lines.append(line.strip())
            
            print("Send-related HTML snippets:")
            for line in send_related_lines[:10]:  # Show first 10 matches
                print(f"  {line}")
                
        except Exception as source_error:
            print(f"❌ Error inspecting page source: {source_error}")
        
        print("\n" + "=" * 50)
        print("🎯 DEBUG COMPLETE")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_whatsapp_dom() 