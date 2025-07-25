import random
import re
import shutil
import time
import playwright.sync_api
import pathlib as pa

from Whatsapp import Selectors_Config as sc, SETTINGS
from Whatsapp.BrowserManager import CusBrowser

#-----------------------------------------------------------------------------------------------------------------------
preferred_login_method = SETTINGS.LOGIN_METHOD
browser = CusBrowser.getInstance()
debug = SETTINGS.DEBUG
#-----------------------------------------------------------------------------------------------------------------------


def login() -> None:
    page = browser.new_page()

    if page.url != "https://web.whatsapp.com/":
        page.goto("https://web.whatsapp.com/")

    time.sleep(random.randint(1,2))

    def scanner_login() -> None:
        canvas = sc.qr_canvas(page)
        try:
            # If QR canvas is visible, we haven't logged in yet
            if canvas.is_visible(timeout=random.randint(1000, 2000)):
                if preferred_login_method == 1:
                    # Wait for a chat list after QR scan
                    sc.chat_list(page).wait_for(timeout=SETTINGS.LOGIN_WAIT_TIME / 2, state="visible")
                else:
                    # Click the "Login with phone number" button
                    button = page.get_by_role("button", name=re.compile("log.*in.*phone number", re.I))
                    button.hover(timeout=random.randint(1000, 2000))
                    button.click()

                    # Now we need to define the further steps for the code-based login
                    page.wait_for_load_state(state="networkidle")
                    country = page.locator("xpath=.//button//span[contains(@data-icon='chevron')]")
                    country.hover()
                    country.click(click_count=random.randint(1,2))

                    wa_popover = page.locator("xpath=.//div[contains(@id=''wa.*popovers)]//span[contains(@data-icon='search']")
                    wa_popover.hover()
                    wa_popover.click()
                    wa_popover.type(SETTINGS.BOT_NUM_COUNTRY,delay=random.randint(300,600))

                    time.sleep(random.uniform(0.5, 1.5))
                    wa_popover.press("ArrowDown")
                    time.sleep(random.uniform(0.6, 1.2))
                    wa_popover.press("ArrowDown")
                    time.sleep(random.uniform(0.3, 0.7))
                    wa_popover.press("Enter")

                    input_box = page.get_by_role("textbox", name=re.compile("phone number", re.I))
                    input_box.hover()
                    input_box.type(SETTINGS.BOT_NUMBER,delay=random.randint(500,1000))


            else:
                # Already logged in, wait for the chat list
                sc.chat_list(page).wait_for(timeout=SETTINGS.LOGIN_WAIT_TIME, state="visible")
        except Exception as e:
            print(f"Login error: {e}")

    scanner_login()

def monitorThread(page : playwright.sync_api.Page) -> None :
    while(True) :
        if sc.qr_canvas(page).is_visible() :
            # Destroy the session files
            time.sleep(60)
            pass

def cleanFolder(folder: pa.Path) -> None:
    if folder.exists():
        for item in folder.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)