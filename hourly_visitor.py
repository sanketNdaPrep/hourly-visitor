import os
import time
import random
import logging
from playwright.sync_api import sync_playwright

TARGET_URL = os.getenv("TARGET_URL", "https://earth-sp-nda.vercel.app/")
DWELL_TIME = int(os.getenv("DWELL_TIME", "300"))
HEADLESS = True

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=logging.INFO)

# Diverse Browser Fingerprints for Vercel Telemetry
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1280, "height": 720}
]

LOCALES = ["en-US", "en-GB", "en-IN", "en-CA", "en-AU"]

def visit_and_stay():
    selected_ua = random.choice(USER_AGENTS)
    selected_vp = random.choice(VIEWPORTS)
    selected_locale = random.choice(LOCALES)

    logging.info(f"Launching browser ({selected_vp['width']}x{selected_vp['height']})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=selected_ua,
            viewport=selected_vp,
            locale=selected_locale
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        start_time = time.time()
        try:
            logging.info(f"Navigating to {TARGET_URL}...")
            page.goto(TARGET_URL, timeout=60000, wait_until="domcontentloaded")
            time.sleep(2)
            page.evaluate("window.scrollBy(0, 400)")
            logging.info("Successfully rendered page and triggered scroll interaction.")
        except Exception as e:
            logging.error(f"Navigation warning: {e}")

        # Enforce exact 5-minute dwell time regardless of navigation state
        elapsed = time.time() - start_time
        remaining_sleep = max(0, DWELL_TIME - elapsed)
        logging.info(f"Holding connection open for remaining {int(remaining_sleep)} seconds...")
        time.sleep(remaining_sleep)

        logging.info("5-minute stay complete. Closing browser.")
        context.close()
        browser.close()

if __name__ == "__main__":
    visit_and_stay()
    
