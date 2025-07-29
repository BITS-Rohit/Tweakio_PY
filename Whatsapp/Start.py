import signal
import sys
import threading
import time
import traceback

from Whatsapp import Brain
from Whatsapp import Extra as ex
from Whatsapp import SETTINGS, ___ as _
from Whatsapp import WebLogin as wl
from Whatsapp import pre_dir as pwd
from Whatsapp.BrowserManager import CusBrowser

# ----------------------------------------------------------------------------------------------------------------------
RESTART_DELAY = SETTINGS.RESTART_TIME
browser = CusBrowser.getInstance()  # Single Instance


# ----------------------------------------------------------------------------------------------------------------------

def shutdown():
    global browser
    print("⚠️  Shutdown initiated…")
    print("📦  Saving seen IDs and ban list…")
    ex.dump_ids(_.seen_ids)
    ex.dump_banlist(_.ban_list)

    if browser and hasattr(browser, "context"):
        try:
            trace_path = pwd.getTraceFile()
            browser.context.tracing.stop(path=trace_path)
            print(f"🗂️ Trace saved to {trace_path}")
        except Exception as e:
            print(f"⚠️  could not stop tracing (ignored): {e}")
        try:
            browser.close()
        except Exception as e:
            print(f"Error closing browser: {e}")

    print("✅  Clean exit.")


def handle_signal(*_):
    shutdown()
    sys.exit(0)


def autosave():
    while True:
        time.sleep(300)  # Every 5 minutes
        ex.dump_ids(_.seen_ids)
        ex.dump_banlist(_.ban_list)
        print("💾 Autosaved seen IDs and ban list.")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while True:
        try:
            page = None
            for tries in range(3):
                try:
                    page = browser.new_page()
                    break
                except Exception as e:
                    print(f"❗ Retrying new_page: {e}")
                    time.sleep(1)
            else:
                if not page:
                    print("Error in Page getting in start.py")
                    break

            success = wl.login(page=page)  # Login

            if not success:
                print("❌  Login failed — exiting. ")
                break

            # Load modules
            _.load()

            # Auto Dump start
            threading.Thread(target=autosave, daemon=True).start()
            print(" == Auto Save thread started == ")

            print("#----  Fetching Messages ----#")
            Brain.Start_Handling(page)
            break

        except Exception as e:
            print(f"🔥  Unhandled exception — restarting in {RESTART_DELAY}s. {e}")
            traceback.print_exc()
            shutdown()
            time.sleep(RESTART_DELAY)
