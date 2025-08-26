import random
import re
import time

from playwright.sync_api import Page

from Whatsapp import pre_dir as dirs
from Whatsapp import selectors_config as sc, SETTINGS

# ─── Screenshot setup ──────────────────────────────────────────────────────────
SCREENSHOT_DIR = dirs.rootDir / 'screenshots'
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

preferred_login_method = SETTINGS.LOGIN_METHOD
STATE_FILE = dirs.rootDir / "storage_state.json"


def login(page: Page) -> bool:
    """Main login function for WhatsApp Web."""
    # Navigate & sanity check
    page.goto("https://web.whatsapp.com/", timeout=60_000)
    page.wait_for_load_state("networkidle", timeout=50_000)

    if not page.url.startswith("https://web.whatsapp.com/"):
        print("❌ WhatsApp Web did not load")
        return False
    print("✅ WhatsApp Web reached")

    # Try QR or code login
    if not _scanner_login(page):
        ts = int(time.time())
        out = SCREENSHOT_DIR / f"login_debug_{ts}.png"
        page.screenshot(path=str(out))
        print(f"⚠️ Saved debug screenshot to {out}")
        return False

    # Dismiss any startup popup
    time.sleep(5)
    popup = sc.startup_popup_locator(page)
    if popup.is_visible():
        popup.click()
        print("▶️ Dismissed startup popup")
    else:
        print("— No startup popup")

    return True


def _scanner_login(page: Page) -> bool:
    """Decide whether to use QR scan, code login, or load existing session."""
    try:
        canvas = sc.qr_canvas(page)
        time.sleep(2)

        # ── QR FLOW ─────────────────────────
        if canvas.is_visible():
            if preferred_login_method == 1:
                print("⏳ Waiting for QR scan…")
                t = SETTINGS.LOGIN_WAIT_TIME / 2
                sc.chat_list(page).wait_for(timeout=t, state="visible")
                if canvas.is_visible():
                    print(f"⚠️ QR not scanned within {t}ms")
                    return False
                print("✅ QR scan succeeded")
                page.context.storage_state(path=str(STATE_FILE))
                return True
            else:
                # User requested code login
                return _code_login(page)

        # ── Code login prompt ─────────────────────────
        if page.get_by_text(re.compile("Steps to log in", re.I)).is_visible():
            return _code_login(page)

        # ── Already logged in ─────────────────────────
        print("🟢 Already logged in | Loading chats…")
        sc.chat_list(page).wait_for(timeout=SETTINGS.LOGIN_WAIT_TIME / 3, state="visible")
        print("✅ Chats loaded")
        page.context.storage_state(path=str(STATE_FILE))
        return True

    except Exception as e:
        print("❌ Login error:", e)
        return False


def _code_login(page: Page) -> bool:
    """Automated code-based login (phone number → code)."""
    print("🔑 Starting code-based login…")

    # Click “Login with phone number”
    try:
        btn = page.get_by_role("button", name=re.compile("log.*in.*phone number", re.I))
        btn.click()
        page.wait_for_load_state("networkidle")
    except:
        print("⚠️ ‘Login with phone number’ button not found.")
        return False

    # Select country
    try:
        ctl = page.locator("button:has(span[data-icon='chevron'])")
        ctl.click()
        page.keyboard.type(SETTINGS.BOT_NUM_COUNTRY, delay=random.randint(100, 200))
        time.sleep(0.5)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
    except Exception as e:
        print("⚠️ Country selection failed:", e)
        return False

    # Enter phone number
    try:
        inp = page.locator("form >> input")
        # ha.move_mouse_to_locator(page, inp)
        inp.click()
        inp.type(SETTINGS.BOT_NUMBER, delay=random.randint(100, 200))
        page.keyboard.press("Enter")
    except Exception as e:
        print("⚠️ Phone number input failed:", e)
        return False

    # Retrieve login code
    try:
        code_elem = page.locator("div[data-link-code]")
        code_elem.wait_for(timeout=10_000)
        code = code_elem.get_attribute("data-link-code")
        print(f"🔢 Received login code: {code}")
    except Exception as e:
        print("⚠️ Could not retrieve login code:", e)
        return False

    # Wait for chats to load
    try:
        print("Waiting 3 mins for chat load")
        sc.chat_list(page).wait_for(timeout=180_000, state="visible")
        print("✅ Chats loaded via code login")
        page.context.storage_state(path=str(STATE_FILE))
        return True
    except:
        print("⚠️ Chats did not load after code login")
        return False
