import random
import re
import time

from playwright.sync_api import Page

from Whatsapp import selectors_config as sc, SETTINGS, HumanAction as ha


# -----------------------------------------------------------------------------------------------------------------------
preferred_login_method = SETTINGS.LOGIN_METHOD
debug = SETTINGS.DEBUG
Mess_load_time = None  # we will update it dynamically for the login part
# -----------------------------------------------------------------------------------------------------------------------

def login(page: Page,browser) -> bool:
    page.goto("https://web.whatsapp.com/", timeout=60_000)
    page.wait_for_load_state(state="networkidle", timeout=50_000)

    def scanner_login() -> bool:
        try:
            canvas = sc.qr_canvas(page)
            time.sleep(2)

            if canvas.is_visible():
                if preferred_login_method == 1:
                    # Wait for QR scan to complete
                    print("Waiting for QR scan")
                    t = SETTINGS.LOGIN_WAIT_TIME / 2
                    try:
                        sc.chat_list(page).wait_for(timeout=t, state="visible")
                        if canvas.is_visible():
                            print(f"Did not scan QR in given time [{t}]")
                            return False
                    except Exception:
                        print("Chat list not loaded after QR wait.")
                        return False

                else:
                    # Phone number login flow
                    print("Initiating automated code login")
                    try:
                        login_btn = page.get_by_role("button", name=re.compile("log.*in.*phone number", re.I))
                        login_btn.hover(timeout=2000)
                        login_btn.click()
                    except Exception:
                        print("Login with phone number button not found.")
                        return False

                    page.wait_for_load_state("networkidle")

                    try:
                        country = page.locator("button:has(span[data-icon='chevron'])")
                        country.wait_for(timeout=7000, state="visible")
                        country.hover()
                        country.click()
                    except Exception:
                        print("Country selector not clickable.")
                        return False

                    try:
                        page.keyboard.type(SETTINGS.BOT_NUM_COUNTRY, delay=random.randint(100, 200))
                        time.sleep(random.uniform(0.3, 0.7))
                        page.keyboard.press("ArrowDown")
                        page.keyboard.press("ArrowDown")
                        page.keyboard.press("Enter")
                    except Exception as e :
                        print(f"Country search failed. {e}")
                        return False

                    try:
                        input_box = page.locator("form >> input")
                        ha.move_mouse_to_locator(page,input_box)
                        input_box.click()
                        input_box.type(SETTINGS.BOT_NUMBER, delay=random.randint(100, 200))
                        page.keyboard.press("Enter")
                    except Exception as e :
                        print(f"Phone number input failed.{e}")
                        return False

                    try:
                        time.sleep(random.uniform(1.0, 2.0))
                        code_elem = page.locator("div[data-link-code]")
                        code_elem.wait_for(timeout=10000)
                        code = code_elem.get_attribute("data-link-code")
                        print(f"Enter code to confirm login: {code} — Waited 60 sec")
                    except Exception as e:
                        print(f"Login code not found. {e}")
                        return False

                    try:
                        sc.chat_list(page).wait_for(timeout=60000, state="visible")
                        print("Chats loaded successfully.")
                        browser.context.storage_state(path=browser.storage_state)  # Needed for Auto GitHub workflow
                        return True
                    except Exception:
                        print("Login failed — chats not loaded in time.")
                        return False

            else:
                # Already logged in
                print("Already logged in | Chat Loading...")
                sc.chat_list(page).wait_for(timeout=SETTINGS.LOGIN_WAIT_TIME, state="visible")
                print("Chats loaded successfully.")
                browser.context.storage_state(path=browser.storage_state) # Needed for Auto GitHub workflow
                return True

        except Exception as e:
            print("Can't Login...")
            print(f"Login error from scanner_login // login:\n{e}")
            return False

    if not scanner_login():
        return False


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
