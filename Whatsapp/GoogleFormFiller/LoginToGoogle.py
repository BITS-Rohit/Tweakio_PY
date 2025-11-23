"""
Login File for Google
"""
import random
import time
from playwright.sync_api import Page

from Whatsapp.HumanAction import human_send
# from Whatsapp.SETTINGS import GOOGLE_EMAIL, GOOGLE_PASSWORD

GOOGLE_EMAIL ="biz.zila123@gmail.com"
GOOGLE_PASSWORD = "Rohit@321@123"

def Login(page: Page):
    """
    Login to Google
    :param page: Page
    :return: boolean [True on success, False on failure]
    """

    if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
        print(" Email or password is empty - Login Failed")
        return False

    # Navigate to form
    page.goto("https://accounts.google.com/")
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    try:
        # Email field
        email = page.locator("input[type='email']").first
        if email.count() > 0:
            email.click()
            human_send(page=page, text=GOOGLE_EMAIL, element=email)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1500)
            print("Email done")
        else:
            print("Email not found")

        # Password field
        passd = page.locator("input[aria-label*='password']")
        passd.wait_for(state="visible", timeout=3000)

        if passd.count() > 0:
            passd.click()
            human_send(page=page, text=GOOGLE_PASSWORD, element=passd)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1500)
            print("Password done")
        else:
            print("Password not found")

        time.sleep(random.uniform(4, 7))

    except Exception as e:
        print(f"Error: {e}")

    return True
