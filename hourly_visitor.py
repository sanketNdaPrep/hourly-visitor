import os
import time
import random
import logging
from playwright.sync_api import sync_playwright

TARGET_URL = os.getenv("TARGET_URL", "https://earth-sp-nda.vercel.app/")
DWELL_TIME = int(os.getenv("DWELL_TIME", "300"))
HEADLESS = True

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

# Diverse User-Agents to prevent Vercel deduplication
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900}
]

def visit_and_stay():
    # Randomly select a signature for each run
    selected_ua = random.choice(USER_AGENTS)
    selected_vp = random.choice(VIEWPORTS)
    
    logging.info(f"Launching stealth browser ({selected_vp['width']}x{selected_vp['height']})...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = browser.new_context(
            user_agent=selected_ua,
            viewport=selected_vp,
            locale="en-US",
            timezone_id="Asia/Kolkata"
        )
        
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            # Navigate and wait for network to idle
            page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")
            
            # Simulate real user interaction so Vercel fires telemetry immediately
            time.sleep(3)
            page.evaluate("window.scrollBy(0, 400)")
            time.sleep(2)

            logging.info(f"Loaded {TARGET_URL}. Staying active for {DWELL_TIME // 60} minutes...")
            time.sleep(max(0, DWELL_TIME - 5))
            logging.info("Stay complete. Closing context.")
        except Exception as e:
            logging.error(f"Error during visit: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    visit_and_stay()
    
