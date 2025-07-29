import signal
import sys
import threading
import time
import traceback

from Whatsapp import Brain
from Whatsapp import Extra as ex
from Whatsapp import SETTINGS, ___ as _
from Whatsapp import WebLogin as wl
from Whatsapp import pre_dir
from Whatsapp.BrowserManager import CusBrowser

# ----------------------------------------------------------------------------------------------------------------------
RESTART_DELAY = SETTINGS.RESTART_TIME
browser = CusBrowser.getInstance()  # Single Instance
# ----------------------------------------------------------------------------------------------------------------------

def shutdown():
    global browser
    print("🌙 Shutdown initiated… 🌙️")
    print("📦  Saving seen IDs and ban list…")

    ex.dump_ids(_.seen_ids)
    ex.dump_banlist(_.ban_list)
    ex.dump_admin(_.admin_list)

    try:
        if browser and hasattr(browser, "context"):
            try:
                trace_path = pre_dir.TraceStop()
                trace_path.parent.mkdir(parents=True, exist_ok=True)
                browser.context.tracing.stop(path=str(trace_path))
                print(f"🗂️ Trace saved to {trace_path}")
            except Exception as e:
                print(f"⚠️  could not stop tracing (ignored): {e}")

            # ✅ Then try to close the browser
            try:
                browser.close()
            except Exception as e:
                print(f"⚠️ Error closing browser (ignored): {e}")

    except Exception as outer:
        print(f"⚠️ Unexpected shutdown error: {outer}")

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

            print("====== ====== ====== ====== ====== ======")
            print(" == Auto Save thread started == ") # Auto Dump start
            threading.Thread(target=autosave, daemon=True).start()
            print("====== ====== ====== ====== ====== ======")
            print("#----  Fetching Messages ----#")
            Brain.Start_Handling(page) # Starting message handler
            print("====== ====== ====== ====== ====== ======")
            break
        except Exception as e:
            print(f"🔥  Unhandled exception — restarting in {RESTART_DELAY}s. {e}")
            traceback.print_exc()
            shutdown()
            time.sleep(RESTART_DELAY)
