import pickle
from pathlib import Path

from typing import Optional
from browserforge.fingerprints import FingerprintGenerator
from camoufox import launch_options
from camoufox.sync_api import Camoufox, BrowserContext
from playwright.sync_api import Page

from Whatsapp import pre_dir as dirs

# ---------------- Config ----------------
addons = [
    # "/home/radheradhe/Desktop/Camoufox_addons/adblock_for_firefox-6.26.0",
    # "/home/radheradhe/Desktop/Camoufox_addons/privacy_badger17-2025.5.30",
    # "/home/radheradhe/Desktop/Camoufox_addons/search_by_image-8.2.3",
    # "/home/radheradhe/Desktop/Camoufox_addons/sponsorblock-5.14",
    # "/home/radheradhe/Desktop/Camoufox_addons/video_downloadhelper-9.5.0.2",
    # "/home/radheradhe/Desktop/Camoufox_addons/view_pdf-1.1",
    # "/home/radheradhe/Desktop/Camoufox_addons/youtube_high_definition-118.0.9"
]

BrowserContextInstance: Optional[BrowserContext] = None
pageManager = []
fg = None
traces_dir = dirs.getTraceDir()


# ---------------- Helpers ----------------
def getInstance() -> BrowserContext:
    """Get or initialize persistent Camoufox context."""
    global BrowserContextInstance
    if BrowserContextInstance is None:
        BrowserContextInstance = getBrowser()
    return BrowserContextInstance


# noinspection PyTypeChecker
def getBrowser() -> BrowserContext:
    """Initialize Camoufox with persistent context and fingerprint."""
    global BrowserContextInstance, fg

    if fg is None:
        path = Path(f"{dirs.rootDir}/whatsapp_web_fg")
        if path.exists():
            print("Loading existing fingerprint from file...")
            with open(path, 'rb') as f:
                fg = pickle.load(f)
        else:
            print("Generating and saving new fingerprint...")
            fg = FingerprintGenerator().generate()
            with open(path, 'wb') as f:
                pickle.dump(fg, f)

    if BrowserContextInstance is None:
        BrowserContextInstance = Camoufox(
            **launch_options(
                locale="en-US",
                headless=False,
                humanize=True,
                geoip=True,
                fingerprint=fg,
                # enable_cache=True,  # Only True for back and forward page using
                i_know_what_im_doing=True,
                os="linux",
                addons=addons,
                main_world_eval=True),

            persistent_context=True,
            user_data_dir=dirs.getSavedLoginDir(),
            traces_dir=traces_dir
        ).__enter__()
    return BrowserContextInstance


def getPage() -> Page:
    """Get a page from Camoufox context or create a new one."""
    global pageManager
    ctx = getInstance()
    if ctx.pages:
        pg = ctx.pages[0]
    else:
        pg = ctx.new_page()
    pageManager.append(pg)
    return pg


def close_browser() -> None:
    """Close Camoufox instance safely."""
    global BrowserContextInstance
    if BrowserContextInstance:
        BrowserContextInstance.close()

# if __name__ == "__main__":
#     page = getPage()
#     page.goto("https://web.whatsapp.com")
#     time.sleep(2000)
#
