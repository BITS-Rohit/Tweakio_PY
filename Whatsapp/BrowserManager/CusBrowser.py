"""
In this we will create our Browser with CusBrowser [ Custom Browser ]
Also, the single instance of this browser will be used.

Stealth will be patched from the stealing.py [ just another file in the BrowserManager ]
Monkey Patching we will be doing
"""
import threading

from playwright.sync_api import sync_playwright, Page
import ip
import Whatsapp.BrowserManager.stealing as steal
from Whatsapp import SETTINGS, pre_dir

# -----------------------------------------------------------------------------------------------------------------------
traces_dir = pre_dir.TraceStart()
# -----------------------------------------------------------------------------------------------------------------------

class CusBrowser:
    """
    Thread-safe Singleton Browser Manager with stealth and spoofing.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.browser = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)
                    cls._instance._init_browser()
        return cls._instance

    def _init_browser(self):
        ip.main() # IP configs
        print("----------------------------------------------------------")
        print("🚀 Launching persistent stealth Chromium instance...")

        self.playwright = sync_playwright().start()

        user_data_dir = pre_dir.getSavedLoginDir(SETTINGS.PROFILE)
        self.context = self.playwright.chromium.launch_persistent_context(
            slow_mo=0,
            locale="en-US",
            timezone_id="Asia/Kolkata",
            geolocation={"longitude": 77.2090, "latitude": 28.6139},
            permissions=["geolocation", "clipboard-read", "clipboard-write"],
            # color_scheme="no-preference", # or "dark" or light
            is_mobile=False,
            reduced_motion="no-preference",
            forced_colors=None,  # or "active"
            service_workers="allow",  # block
            has_touch=False,
            ignore_https_errors=True,
            user_data_dir=user_data_dir,
            devtools=False,
            device_scale_factor=2.0,
            headless=False,
            ignore_default_args=[
                "--enable-automation",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ],
            timeout=SETTINGS.BROWSER_INIT_TIMEOUT,
            traces_dir=traces_dir,
            args=[
                "--disable-infobars",
                "--window-size=1280,800"
            ],
            viewport={"width": 1280, "height":720 },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            extra_http_headers=steal.headers,
            java_script_enabled=True
        )

        try:
            self.context.tracing.start(
                name=f"{SETTINGS.PROFILE}_trace",
                screenshots=True,
                snapshots=True,
                sources=True
            )
            print("#        -- Browser Tracing Started --        #")
        except Exception as e:
            if "Tracing has been already started" in str(e):
                print("⚠️ Tracing already started — skipping.")
            else:
                raise Exception("Error in Tracing man")

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        print("~~Chromium persistent context initialized with stealth mode~~")


    def new_page(self) -> Page:
        if self.context.pages and self.context.pages[0].url == "about:blank":
            page = self.context.pages[0]
        else:
            page = self.context.new_page()

        steal.stealth(page)
        return page

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
        CusBrowser._instance = None
        print("🧹 Browser closed and resources cleaned.")

# Usage
def getInstance():
    return CusBrowser()
