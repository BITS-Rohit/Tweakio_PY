import random
import re
import time

from playwright.sync_api import Page

from Whatsapp import selectors_config as sc, SETTINGS

# -----------------------------------------------------------------------------------------------------------------------
# preferred_login_method = SETTINGS.LOGIN_METHOD
preferred_login_method = 1
# browser = CusBrowser.getInstance()
debug = SETTINGS.DEBUG
Mess_load_time = None  # we will update it dynamically for the login part


# -----------------------------------------------------------------------------------------------------------------------


def login(page: Page) -> bool:
    page.goto("https://web.whatsapp.com/", timeout=60_000)
    page.wait_for_load_state(state="networkidle", timeout=50_000)

    def scanner_login() -> None:
        canvas = sc.qr_canvas(page)
        try:
            time.sleep(2)  # Time for canvas to be visible
            if canvas.is_visible():
                if preferred_login_method == 1:
                    # Wait for a chat list after QR scan
                    print("Waiting for QR scan")
                    t = SETTINGS.LOGIN_WAIT_TIME / 2
                    sc.chat_list(page).wait_for(timeout=t, state="visible")
                    if canvas.is_visible():
                        print(f"Did not scanned qr in Given Time [{t}]")
                        return False
                else:
                    # Click the "Login with phone number" button
                    print("Initiating automated code login")
                    button = page.get_by_role("button", name=re.compile("log.*in.*phone number", re.I))
                    button.hover(timeout=random.randint(1000, 2000))
                    button.click()

                    # Now we need to define the further steps for the code-based login
                    page.wait_for_load_state(state="networkidle")
                    country = page.locator("xpath=.//button//span[contains(@data-icon='chevron')]")
                    country.hover()
                    country.click(click_count=random.randint(1, 2))

                    wa_popover = page.locator(
                        "xpath=.//div[contains(@id=''wa.*popovers)]//span[contains(@data-icon='search']")
                    wa_popover.hover()
                    wa_popover.click()
                    wa_popover.type(SETTINGS.BOT_NUM_COUNTRY, delay=random.randint(300, 600))

                    time.sleep(random.uniform(0.5, 1.5))
                    wa_popover.press("ArrowDown")
                    time.sleep(random.uniform(0.6, 1.2))
                    wa_popover.press("ArrowDown")
                    time.sleep(random.uniform(0.3, 0.7))
                    wa_popover.press("Enter")

                    input_box = page.get_by_role("textbox", name=re.compile("phone number", re.I))
                    input_box.hover()
                    input_box.type(SETTINGS.BOT_NUMBER, delay=random.randint(500, 1000))
                    page.keyboard.press("Enter")

                    time.sleep(random.uniform(1.0, 2.0))
                    code = page.locator("div[aria-details][data-link-code]").get_attribute("data-link-code")
                    print(f"Enter code to confirm login : {code} & Waited Time for login is  60 sec")

                    i = 1
                    check = False
                    while i <= 60:
                        if sc.chat_list(page).is_visible():
                            check = True
                            break
                        else:
                            print(f"Waiting ... Secs : {i}")
                            time.sleep(1)

                    if check:
                        print("Chats loaded success.")
                    else:
                        print("Failed login , out of Time , Re-try")
                        return False

            else:
                # Already logged in, wait for the chat list
                print("Already Login | waiting for the chats to load.")
                sc.chat_list(page).wait_for(timeout=SETTINGS.LOGIN_WAIT_TIME, state="visible")
                print("Chats loaded success.")
            # print("Full Boot Success.")
            return True
        except Exception as e:
            print("Can't Login...")
            print(f"Login error from scanner_login // login \n : {e}")
            return False

    scanner_login()

    # Todo , we will reduce it as this only comes at the start like 1-2 times ,
    #  after 5 successful logins we can remove this pop-up check then reducing 5 sec more in Boot Time
    time.sleep(5)  # pop up rendering time
    if sc.startup_popup(page).is_visible():
        sc.startup_popup(page).hover()
        sc.startup_popup(page).click()
        print("Popup seen\nClicked Continue")
    else:
        print("No Popup seen")
    return True
