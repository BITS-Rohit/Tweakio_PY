import atexit
import signal
import sys
import time
import traceback

from Whatsapp import Extra as ex
from Whatsapp.Brain import Start_Handling
from Whatsapp.BrowserManager import CusBrowser
from Whatsapp.WebLogin import login
from Whatsapp import pre_dir as pwd
from Whatsapp import SETTINGS

RESTART_DELAY = SETTINGS.RESTART_TIME
seen_ids = ex.pick_ids()
ban_list = ex.pick_banlist()
browser = None

def shutdown():
    global browser
    print("⚠️ Shutdown initiated…")
    print("📦 Saving seen IDs and ban list…")
    ex.dump_ids(seen_ids)
    ex.dump_banlist(ban_list)

    if browser and hasattr(browser, "context"):
        try:
            trace_path = pwd.getTraceFile()
            browser.context.tracing.stop(path=trace_path)
            print(f"🗂️ Trace saved to {trace_path}")
        except Exception as e:
            print(f"⚠️ could not stop tracing (ignored): {e}")
        try:
            browser.close()
        except Exception as e:
            print(f"Error closing browser: {e}")

    print("✅ Clean exit.")

def handle_signal(*_):
    shutdown()
    sys.exit(0)

if __name__ == '__main__':
    atexit.register(shutdown)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while True:
        try:
            print("🚀 Launching browser…")
            browser = CusBrowser.getInstance()
            page = login()
            if not page:
                print("❌ Login failed — exiting.")
                break

            print("---- Starting message handler ----")
            Start_Handling(page)
            break

        except Exception as e:
            print(f"🔥 Unhandled exception — restarting in {RESTART_DELAY}s. {e}")
            traceback.print_exc()
            shutdown()
            time.sleep(RESTART_DELAY)
