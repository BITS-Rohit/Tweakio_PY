import os
import signal
import sys
import threading
import time
import traceback

from playwright.sync_api import Page

from typing import Optional
from Whatsapp import Brain
from Whatsapp  import Extra as ex
from Whatsapp  import SETTINGS, ___ as _
from Whatsapp  import WebLogin as wl
from Whatsapp.BrowserManager import getPage, close_browser

# ----------------------------------------------------------------------------------------------------------------------
RESTART_DELAY = SETTINGS.RESTART_TIME
# ----------------------------------------------------------------------------------------------------------------------

def shutdown():
    """Clean shutdown: save state and close browser/context."""
    print("🌙️ Shutdown initiated…")
    print(" 📦  Saving seen IDs and ban list… 📦  ")

    try:
        ex.dump_ids(_.seen_ids)
        ex.dump_banlist(_.ban_list)
        ex.dump_admin(_.admin_list)
    except Exception as e:
        print(f"⚠️ Error saving data: {e}")

    try:
        close_browser()
    except Exception as outer:
        print(f"⚠️ Unexpected shutdown error: {outer}")

    print("✅  Clean exit.")


def handle_signal(*_):
    """Signal handler for graceful shutdown."""
    shutdown()
    sys.exit(0)


def autosave():
    """Autosave thread for seen IDs and ban list."""
    while True:
        try:
            time.sleep(300)  # Every 5 minutes
            ex.dump_ids(_.seen_ids)
            ex.dump_banlist(_.ban_list)
            print("💾 Autosaved seen IDs and ban list.")
        except Exception as e:
            print(f"⚠️ Autosave error: {e}")


if __name__ == '__main__':

    # --- LangChain setup ---
    if SETTINGS.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = SETTINGS.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = SETTINGS.LANGCHAIN_PROJECT

    # --- Signal handlers ---
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while True:
        try:
            page : Optional[Page]
            # Try getting a page up to 3 times
            for tries in range(3):
                try:
                    page = getPage()
                    break
                except Exception as e:
                    print(f"❗ Retrying getPage: {e}")
                    print("🔄 Cleaning up browser before retry...")
                    shutdown()
                    time.sleep(1)
            else:
                if not page:
                    print("❌ Could not get page after retries. Exiting.")
                    break

            # Login with the context and page
            success = wl.login(page=page )
            if not success:
                print("❌ Login failed — exiting.")
                handle_signal()

            # Load additional modules
            _.load()

            print("====== ====== ====== ====== ====== ======")
            print(" == Auto Save thread started == ")
            threading.Thread(target=autosave, daemon=True).start()
            print("====== ====== ====== ====== ====== ======")
            print("#----  Fetching Messages ----#")
            Brain.Start_Handling(page)  # Start message handling
            print("====== ====== ====== ====== ====== ======")
            break

        except Exception as e:
            print(f"🔥 Unhandled exception — restarting in {RESTART_DELAY}s. {e}")
            traceback.print_exc()
            shutdown()
            time.sleep(RESTART_DELAY)
