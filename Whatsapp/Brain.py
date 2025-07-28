import random
import time

from playwright.sync_api import Locator, Page

from Whatsapp import SETTINGS, selectors_config as sc, Extra as ex, HumanAction as ha, ___, Methods as helper, \
    Reply as rep, post_process as process
from Whatsapp.BrowserManager import CusBrowser

# -----------------------------------------------------------------------------------------------------------------------
debug = SETTINGS.DEBUG
refreshTime = SETTINGS.REFRESH_TIME
browser = CusBrowser.getInstance()
page = None
processed_ids = ex.pick_ids()
admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", "...help",
              SETTINGS.NLP, SETTINGS.QUANTIFIER, "--ban--", "--unban--"]
user_cmds = [SETTINGS.NLP, SETTINGS.QUANTIFIER, "showq", "...help"]
pause_mode = False
ban_list = ex.pick_banlist()
# -----------------------------------------------------------------------------------------------------------------------

def Start_Handling(p: Page) -> None:
    global page
    page = p

    # - - - - - - Depreciation in future - - - - - - #
    # ex.SeedCache(page, processed_ids)

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
            chats = sc.chat_items(page)
            if chats is None or chats.count() == 0:
                print("Null Chat List or 0 Chats found.")
                break
            total = chats.count()
            _range_ = int(min(total, SETTINGS.MAX_CHAT))

            print(f"Chat count found : {total}")
            print(f"Max chat checking : {_range_}")
            print(f"---- ---- ---- Cycle {cycle} ---- ---- ----")
            cycle += 1

            y = 1
            for i in range(_range_):
                chat = chats.nth(i)
                _check_messages(chat, y)
                y += 1
                time.sleep(random.uniform(0.5, 3.0))

    except Exception as e:
        print(f"Handle chats error:\n{e}")


def _check_messages(chat: Locator, y: int) -> None:
    name = sc.getChatName(chat)
    unread = ex.is_unread(chat)
    if unread == 0:
        print(f"-- --  Skipping Top chat [no - {y}] with name - {name} -- --")
        return

    ha.move_mouse_to_locator(page, chat)
    chat.click()

    if name == "":
        print("Error getting chat name : ")
    print(f"Opening Top chat [no - {y}] with name -  {name} ")

    messages = sc.messages(page)
    print(f"Total messages fetched : {messages.count()}")
    for i in range(messages.count()):
        message = messages.nth(i)
        text = sc.get_message_text(message).strip()
        if not text: continue
        _auth_handle(message=message, text=text, chat=chat)


def _auth_handle(message: Locator, text: str, chat: Locator):
    t = text.split(" ")[0].lower()
    if t not in admin_cmds:
        return

    print("Message : " + text)
    data_id = sc.get_dataID(message)
    if data_id in processed_ids:
        return

    ex.trace_message(processed_ids, chat, message)
    mess_out = sc.is_message_out(message)

    # --- Auth Checks ---
    auth = SETTINGS.GLOBAL_MODE or mess_out
    sender = ex.getSender_mess(message).replace(" ", "").replace("+", "")
    P_AUTH = sender in ___.admin_list

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
            if name in ban_list:
                ban_list.remove(name)
                print(f"✅ Unbanned chat: {name}")
                rep.reply(page=page, locator=message, text=f"✅ Unbanned chat: {name}")
            else:
                print(f"Chat {name} is not in ban list.")
            return

        elif t == "--ban--":
            if name not in ban_list:
                ban_list.append(name)
                print(f"❌ Banned chat: {name}")
                rep.reply(page=page, locator=message, text=f"❌ Banned chat: {name}")
            else:
                rep.reply(page=page, locator=message, text=f"`{name} is already in ban list.`")
            return

    if name in ban_list:
        print("Banned chat. Returning.")
        return

    # ---- Process NLPis a special command for removing the concept ----
    # for [quant + f_name + f_info] type command To direct -> say in natural language
    if t == SETTINGS.NLP:
        helper.nlp(page=page, locator=message, f_info=text.replace(SETTINGS.NLP, ""))
        return

    # --- Command Execution ---
    if auth and t in user_cmds:
        _process_cmd(message, text,chat)

    elif P_AUTH and t in admin_cmds + user_cmds:
        _Admin_Process(message, text,chat)

    else:
        print(f"Unauthorized command '{t}' from {sender}")

    print("------------- Command processed  ---------------")
    ex.mark_unread(page=page, chat=chat)


def _Admin_Process(message: Locator, text: str,chat:Locator):
    global pause_mode

    if text == "pause_on":
        pause_mode = True
        print("Pause Enabled ✅")
        rep.reply(page=page, locator=message, text="Pause Enabled ✅")
        ex.mark_unread(page=page, chat=chat)

    elif text == "pause_off":
        pause_mode = False
        print("Pause Disabled ❌")
        rep.reply(page=page, locator=message, text="Pause Disabled ❌")

    elif text == "pause_show":
        print(f"Pause Status: {'ON' if pause_mode else 'OFF'}")
        rep.reply(page=page, locator=message, text=f"Pause Status: `{'ON' if pause_mode else 'OFF'}`")

    else:
        _process_cmd(message, text)


def _process_cmd(message: Locator, text: str,chat:Locator):
    if text == "...help":
        rep.reply(page=page, locator=message, text=helper.menu.menu())

    elif text == "showq":
        helper.showq(page=page, locator=message)

    elif text == SETTINGS.NLP:
        helper.nlp(page=page, locator=message, f_info=text)

    else:
        # default command handler
        _natural_cmd(message, text)



def _natural_cmd(message: Locator, text: str):
    # format: /quant + f_name + f_info[if needed]
    parts = text.strip().split()

    if len(parts) < 2:
        print("Not Correct Command. Usage: /quant <f_name> [f_info]")
        return

    f_name = parts[1].lower().strip()
    f_info = " ".join(parts[2:]) if len(parts) > 2 else ""

    process.post_process(page=page, message=message, f_name=f_name, f_info=f_info)
