"""
In this we will create our Browser with CusBrowser [ Custom Browser ]
Also, the single instance of this browser will be used.

Stealth will be patched from the stealing.py [ just another file in the BrowserManager ]
Monkey Patching we will be doing
"""
import threading
from playwright.sync_api import sync_playwright, Page, Browser

import Whatsapp.BrowserManager.stealing as steal
import Whatsapp.pre_dir as sys_dir
from Whatsapp import SETTINGS

#-----------------------------------------------------------------------------------------------------------------------
traceDir = sys_dir.getTraceDir()
#-----------------------------------------------------------------------------------------------------------------------

class CusBrowser:
    """
    Thread-safe Singleton Browser Manager with stealth and spoofing.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)
                    cls._instance._init_browser()
        return cls._instance

    def _init_browser(self):
        print("🚀 Launching stealth Chromium instance...")
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(
            headless=False,
            ignore_default_args=["--enable-automation"],
            slow_mo=SETTINGS.SLOW_MO,
            timeout=SETTINGS.BROWSER_INIT_TIMEOUT,
            traces_dir=traceDir
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
        )
        print("🧠 Chromium context initialized with stealth mode.")

    def new_page(self) -> Page:
        if self.context.pages and self.context.pages[0].url == "about:blank":
            page = self.context.pages[0]
        else:
            page = self.context.new_page()

        steal.stealth(page)
        return page

    def close(self):
        self.browser.close()
        self.playwright.stop()
        CusBrowser._instance = None
        print("🧹 Browser closed and resources cleaned.")

# Usage
def getInstance():
    return CusBrowser()
