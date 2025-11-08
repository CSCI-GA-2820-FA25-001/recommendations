"""
Behave environment configuration for BDD tests
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def before_all(context):
    """Setup global test configuration"""
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")
    context.wait_seconds = 10


def before_scenario(context, scenario):
    """Initialize WebDriver for each scenario"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    context.driver = webdriver.Chrome(options=chrome_options)
    context.driver.implicitly_wait(context.wait_seconds)


def after_scenario(context, scenario):
    """Take screenshot on failure and close browser"""
    if scenario.status == "failed":
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(
            screenshot_dir, 
            f"{scenario.name.replace(' ', '_')}.png"
        )
        context.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
    
    context.driver.quit()


def after_all(context):
    """Cleanup global resources"""
    pass
