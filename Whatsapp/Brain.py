import random
import time

from playwright.sync_api import Locator, Page

from Whatsapp import SETTINGS, selectors_config as sc, Extra as ex, HumanAction as ha, ___ as _, Methods as helper, \
    Reply as rep, post_process as process, pre_dir as pwd
from Whatsapp.BrowserManager import CusBrowser

# -----------------------------------------------------------------------------------------------------------------------
debug = SETTINGS.DEBUG
refreshTime = SETTINGS.REFRESH_TIME
browser = CusBrowser.getInstance()
admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", "...help",
              SETTINGS.NLP, SETTINGS.QUANTIFIER, "--ban--", "--unban--"]
user_cmds = [SETTINGS.NLP, SETTINGS.QUANTIFIER, "showq", "...help"]
pause_mode = False
page = None


# -----------------------------------------------------------------------------------------------------------------------

def Start_Handling(p: Page) -> None:
    global page
    page = p

    def monitor():
        if sc.qr_canvas(page).is_visible():
            print("🧹 QR visible — clearing login data.")
            ex.cleanFolder(pwd.getSavedLoginDir())
            print("Cleaning Done ")
            raise Exception("Session Thread broken, safe clear cookies")

    try:
        try:
            ex.MessageToChat(page)
            print("-- Message to owner done --")
        except Exception as e:
            print(f"Error in message to chat : {e}")
            return
        print("---- Starting monitoring messages ----")

        cycle = 1
        while True:
            monitor()

            chats = sc.chat_items(page)
            if chats is None or chats.count() == 0:
                print("Null Chat List or 0 Chats found.")
                break
            total = chats.count()
            _range_ = int(min(total, SETTINGS.MAX_CHAT))

            print(f"\n---- ---- ---- Cycle {cycle} ---- ---- ----")
            print(f"Chat count found : {total}")
            print(f"Max chat checking : {_range_}")

            cycle += 1

            y = 1
            for i in range(_range_):
                chat = chats.nth(i)
                _check_messages(chat, y)
                y += 1
                time.sleep(random.uniform(0.5, 3.0))

    except Exception as e:
        print(f"Handle chats error: {e}")


def _check_messages(chat: Locator, y: int) -> None:
    try:
        name = sc.getChatName(chat)
        unread = ex.is_unread(chat)
        if unread == 0:
            print(f"-- --  Skipping Top chat [no - {y}] with name - {name} -- --")
            return

        ha.move_mouse_to_locator(page, chat)
        print("--Top chat has new messages--")
        chat.click()

        if name == "":
            print("Error getting chat name : ")
            print(f"Opening Top chat [no - {y}] with name -  {name} ")

        messages = sc.messages(page)
        print(f"Total messages fetched : {messages.count()}")
        for i in range(messages.count()):
            message = messages.nth(i)
            text = sc.get_message_text(message).strip()
            if not text or text.split(" ")[0].lower() not in admin_cmds: continue
            _auth_handle(message=message, text=text, chat=chat)
        ex.mark_unread(page=page, chat=chat)
    except Exception as e:
        print(f"Error in check messages : {e}")


def _auth_handle(message: Locator, text: str, chat: Locator):
    try:
        t = text.split(" ", 1)[0].lower().strip()
        print("Message : " + text)
        if _.ban_list is None : print("None banlist")
        if admin_cmds is None : print("None admin cmds ")
        if user_cmds is None : print("None user cmds")
        data_id = sc.get_dataID(message)

        if not data_id:
            print("Empty data-ID")
            return

        if data_id in _.seen_ids:
            print("[Seen ID containing message]")
            return

        ex.trace_message(_.seen_ids, chat, message)
        mess_out = sc.is_message_out(message)

        # --- Auth Checks ---
        auth = SETTINGS.GLOBAL_MODE or mess_out
        sender = ex.getSender(message).replace(" ", "").replace("+", "")
        print(f"Sender for p_auth: {sender}")
        P_AUTH = sender in _.admin_list

        name = sc.getChatName(chat)
        print(f"Prefix : {t}")

        # --- Pause Handling ---
        if pause_mode:
            if t in ["pause_off", "pause_show"] and P_AUTH:
                _Admin_Process(message, text)
            else:
                print(f"Paused. Ignoring '{t}' from {sender}")
            return

        # --- Ban/Unban Handling ---
        if P_AUTH and t in ["--ban--", "--unban--"]:
            if not name:
                print("Error: Chat name is empty during ban/unban check.")
                return

            if t == "--unban--":
                if name in _.ban_list:
                    _.ban_list.remove(name)
                    print(f"✅ Unbanned chat: {name}")
                    rep.reply(page=page, locator=message, text=f"✅ Unbanned chat: {name}")
                else:
                    print(f"Chat {name} is not in ban list.")
                return

            elif t == "--ban--":
                if name not in _.ban_list:
                    _.ban_list.append(name)
                    print(f"❌ Banned chat: {name}")
                    rep.reply(page=page, locator=message, text=f"❌ Banned chat: {name}")
                else:
                    rep.reply(page=page, locator=message, text=f"`{name} is already in ban list.`")
                return

        if name in _.ban_list:
            print("Banned chat. Returning.")
            return

        # ---- NLP Special Command ----
        if t == SETTINGS.NLP:
            helper.nlp(page=page, locator=message, f_info=text.replace(SETTINGS.NLP, ""))
            return

        # --- Command Execution ---
        text = text.lower()
        if auth and t in user_cmds:
            _process_cmd(message=message, text=text)

        elif P_AUTH and t in admin_cmds + user_cmds:
            _Admin_Process(message=message, text=text)

        else:
            print(f"Unauthorized command '{t}' from {sender}")
            rep.reply(page=page, locator=message, text=f"Unauthorized command '{t}' from {sender}")

        print("------------- Command processed  ---------------")

    except Exception as e:
        print(f"⚠️ Error in _auth_handle(): {e}")
        try:
            rep.reply(page=page, locator=message, text="⚠️ Internal error occurred while processing.")
        except Exception as inner_e:
            print(f"⚠️ Failed to reply to error: {inner_e}")


def _Admin_Process(message: Locator, text: str):
    global pause_mode

    try:
        if text == "pause_on":
            pause_mode = True
            print("Pause Enabled ✅")
            rep.reply(page=page, locator=message, text="Pause Enabled ✅")

        elif text == "pause_off":
            pause_mode = False
            print("Pause Disabled ❌")
            rep.reply(page=page, locator=message, text="Pause Disabled ❌")

        elif text == "pause_show":
            print(f"Pause Status: {'ON' if pause_mode else 'OFF'}")
            rep.reply(page=page, locator=message, text=f"Pause Status: `{'ON' if pause_mode else 'OFF'}`")

        else:
            _process_cmd(message, text)

    except Exception as e:
        print(f"[Admin_Process Error] {e}")
        rep.reply(page=page, locator=message, text=f"❗ Error in admin command:\n`{e}`")


def _process_cmd(message: Locator, text: str):
    try:
        if text == "...help":
            rep.reply(page=page, locator=message, text=helper.menu.menu())

        elif text == "showq":
            helper.showq(page=page, locator=message)

        elif text == SETTINGS.NLP:
            helper.nlp(page=page, locator=message, f_info=text)

        else:
            # default command handler
            _natural_cmd(message=message, text=text)

    except Exception as e:
        print(f"[Process_Cmd Error] {e}")
        rep.reply(page=page, locator=message, text=f"❗ Error in command:\n`{e}`")


def _natural_cmd(message: Locator, text: str):
    try:
        parts = text.strip().split()

        if len(parts) < 2:
            print("Not Correct Command. Usage: /quant <f_name> [f_info]")
            rep.reply(page=page, locator=message, text="❗ Usage: /quant <f_name> [f_info]")
            return

        f_name = parts[1].lower().strip()
        f_info = " ".join(parts[2:]) if len(parts) > 2 else ""

        process.post_process(page=page, message=message, f_name=f_name, f_info=f_info)

    except Exception as e:
        print(f"[Natural_Cmd Error] {e}")
        rep.reply(page=page, locator=message, text=f"❗ Natural command error:\n`{e}`")
