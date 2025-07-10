#!/usr/bin/env python3
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# ── Configuration ──────────────────────────────────────────────────────────────
# Directory to persist Chrome profile (session) so you don't re-scan QR every run:
USER_DATA_DIR = os.path.abspath("chrome-session")  
# How often (in seconds) to poll for new messages:
POLL_INTERVAL = 5                                              
# ────────────────────────────────────────────────────────────────────────────────

def main():
    # Set up Chrome with persistent session
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")  # reuse session folder :contentReference[oaicite:0]{index=0}
    # Launch Chrome (visible) so you can scan QR if needed
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    # Open WhatsApp Web
    driver.get("https://web.whatsapp.com")
    print("Opening WhatsApp Web…")

    # Wait until the chats pane is present (i.e. login complete)
    while True:
        try:
            driver.find_element(By.ID, "pane-side")
            print("✅ Logged in to WhatsApp Web!")
            break
        except:
            print("⌛ Waiting for QR scan…")
            time.sleep(2)
    # ────────────────────────────────────────────────────────────────────────────────

    # Main loop: look for unread chats, reply, then sleep
    print("Entering message-watch loop…")
    while True:
        try:
            # Unread badges: span[data-testid="icon-unread-count"]
            badges = driver.find_elements(By.CSS_SELECTOR, "span[data-testid='icon-unread-count']")
            for badge in badges:
                # Click the chat container that contains this badge
                chat = badge.find_element(By.XPATH, "./ancestor::div[contains(@aria-label,'unread')]")
                chat.click()
                time.sleep(1)  # let chat open

                # Locate the message input box
                inp = driver.find_element(
                    By.XPATH,
                    "//div[@contenteditable and @data-tab='10']"
                )
                # Send reply
                inp.send_keys("Ахуително!!!!!")
                inp.send_keys(Keys.ENTER)
                print(f"→ Replied to chat at {time.strftime('%H:%M:%S')}")
                time.sleep(1)
            # Pause before checking again
            time.sleep(POLL_INTERVAL)
        except Exception as err:
            # If something goes wrong, log and retry
            print("⚠️ Loop error:", err)
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
