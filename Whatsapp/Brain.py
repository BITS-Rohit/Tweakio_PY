import random
import re
import time
from datetime import datetime

from playwright.sync_api import Locator, Page, ElementHandle

from Whatsapp import SETTINGS, selectors_config as sc, Extra as ex, ___ as _, Methods as helper, \
    Reply as rep, post_process as process, pre_dir as pwd

# ----------------------------------------------------------------------------------------------------------------------
debug = False
refreshTime = SETTINGS.REFRESH_TIME
pause_mode = False
page = None
detect = True

# ----------------------------------------------------------------------------------------------------------------------

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
            # ex.MessageToChat(page)
            print("-- Message to owner done --")
        except Exception as e:
            print(f"Error in message to chat : {e}")
            page.keyboard.press("Escape", delay=random.randint(701, 893))
            page.keyboard.press("Escape", delay=random.randint(701, 893))
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
            print(f"Chat count found : {total} ")
            print(f"Max chat checking : {_range_}")

            cycle += 1

            y = 1
            for i in range(_range_):
                chat = chats.nth(i).element_handle()
                _check_messages(chat, y, chats.nth(i))  # chat is now ElementHandle
                y += 1
                time.sleep(random.uniform(0.87, 1.98))

    except Exception as e:
        print(f"Handle chats error: {e}")


def _check_messages(chat: ElementHandle, y: int, Locator_chat: Locator) -> None:  # change
    admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", "...help",
                  SETTINGS.NLP, SETTINGS.QUANTIFIER, "--ban--", "--unban--"]
    try:
        name = sc.getChatName(chat)
        if name == "":
            print("Error getting chat name : ")

        Personal_auth = PersonalChatCheck(chat=Locator_chat)  # this will also need ElementHandle
        if not Personal_auth:
            unread = ex.is_unread(chat)
            if unread == 0:
                print(f"-- --  Skipping Top chat [no - {y}] with name - {name} -- -- {Time()}")
                return

        print(f"Opening Top chat [no - {y}] with name -  {name} ")
        # ha.move_mouse_to_locator(page, chat)
        print("--Top chat has new messages--")
        chat.click()
        try:
            print("<><><><><><><><><><><><><><>")
            messages = sc.messages(page)
            if messages.count() == 0:
                raise Exception("No messages found in opened chat.")

            last_ID = sc.get_dataID(messages.nth(messages.count() - 1).element_handle())
            if not last_ID:
                raise Exception("Data ID is not correct in last message // Brain//check messages")

            while True:
                print(f"Total messages fetched : {messages.count()}")

                for i in range(messages.count()):
                    message = messages.nth(i).element_handle()
                    text = sc.get_message_text(message).strip()
                    # if sc.get_dataID(message) in _.seen_ids:
                    #     print(f"[Seen ID]- Message: [{text}]")
                    #     return
                    # if detect:
                    #     m_type = ex.get_mess_type(message)
                    #     if m_type != "text":
                    #         rep.reply(page=page, locator=message, text=f"`Type : {m_type}`")
                    #         ex.trace_message(_.seen_ids, chat, message)
                    #         return
                    # test purpose only.

                    if not text or text.split(" ")[0].lower() not in admin_cmds:
                        continue
                    _auth_handle(message=message, text=text, chat=chat, p_chat=Personal_auth)

                messages = sc.messages(page)
                current_last_id = sc.get_dataID(messages.nth(messages.count() - 1).element_handle())

                if not current_last_id:
                    raise Exception("Data ID is not correct in last message // Brain//check messages")

                if current_last_id == last_ID: break  # No new messages
                last_ID = current_last_id

            print("<><><><><><><><><><><><><><>")

            if not Personal_auth:
                ex.do_unread(page=page, chat=chat)
        except Exception as e:
            print(f"Error in live messages loop // check messages : {e}")

    except Exception as e:
        print(f"Error in check messages : {e}")


def _auth_handle(message: ElementHandle, text: str, chat: ElementHandle, p_chat: bool = False) -> None:  # change
    try:
        t = text.split(" ", 1)[0].lower().strip()

        data_id = sc.get_dataID(message)
        if not data_id:
            print(f"[Empty data-ID]- Message: [{text}]" )
            return

        if data_id in _.seen_ids:
            print(f"[Seen ID]- Message: [{text}]")
            return

        name = sc.getChatName(chat)
        ex.trace_message(_.seen_ids, chat, message)
        mess_out = sc.is_message_out(message)

        user_auth, Admin_AUTH, sender = False, False, ""

        if p_chat:
            user_auth = Admin_AUTH = True
            sender = SETTINGS.BOT_NUMBER
        else:
            try:
                user_auth = SETTINGS.GLOBAL_MODE or mess_out
                sender_raw = ex.getSenderID(message)
                sender = (sender_raw or "").replace(" ", "").replace("+", "")
                Admin_AUTH = sender in _.admin_list or mess_out
            except Exception as e:
                print(f"Error in user_auth checks : {e}")

        print(f"Prefix : {t}")

        pause_handle(p_auth=Admin_AUTH, t=t, sender=sender, text=text, message=message)

        check = False

        def Ban_Handle():
            nonlocal check
            GID = ex.getGID_CID(message)
            if p_chat: GID = "personal Chat"
            if Admin_AUTH and t in ["--ban--", "--unban--"]:
                if not GID:
                    print("Error: Chat name is empty during ban/unban check.")
                    return

                if p_chat:
                    helper.react(message=message, page=page)
                    rep.reply(page=page, locator=message, text="`You can't ban/unban personal chat`")
                    check = True
                    return

                if t == "--unban--":
                    if GID in _.ban_list:
                        helper.react(page=page, message=message)
                        _.ban_list.remove(GID)
                        _.ban_change = True
                        print(f"`✅ Unbanned chat: [{name}]`")
                        rep.reply(page=page, locator=message, text=f"`Unbanned chat: [{name}]`")
                        check = True
                    else:
                        print(f"Chat[{name}] with GID[{GID}] is not in ban list.")
                        rep.reply(page=page, locator=message,
                                  text=f"`Chat[{name}] with GID[{GID}] is not in ban list.`")
                    return

                elif t == "--ban--":
                    if GID not in _.ban_list:
                        helper.react(page=page, message=message)
                        _.ban_list.append(GID)
                        print(f"`chat is banned now : [{name}]`")
                        rep.reply(page=page, locator=message, text=f"`chat is banned now : [{name}]`")
                        check = True
                    else:
                        rep.reply(page=page, locator=message, text=f"`[{name}] is already in ban list.`")
                    return

            if GID in _.ban_list:
                print("Banned chat. Returning.")
                check = True
                return

        try:
            Ban_Handle()
            if check: return
        except Exception as e:
            print(f" Error in Ban Handle : {e}")

        text = text.lower()

        def cmd_exec():
            admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", "...help",
                          SETTINGS.NLP, SETTINGS.QUANTIFIER, "--ban--", "--unban--"]
            user_cmds = [SETTINGS.NLP, SETTINGS.QUANTIFIER, "showq", "...help"]

            if Admin_AUTH and t in admin_cmds + user_cmds:
                _Admin_Process(message=message, fun_name=text)
            elif user_auth and t in user_cmds:
                _process_cmd(message=message, text=text)
            else:
                print(f"Unauthorized command '{t}' from {sender}")
                rep.reply(page=page, locator=message, text=f"Unauthorized command '{t}' from {sender}")

        try:
            cmd_exec()
        except Exception as e:
            print(f"Error in cmd_exec // user_auth handle : {e}")

        print("------------- Command processed  ---------------")

    except Exception as e:
        print(f"⚠️ Error in _auth_handle(): {e}")
        try:
            rep.reply(page=page, locator=message, text="⚠️ Internal error occurred while processing.")
        except Exception as inner_e:
            print(f"⚠️ Failed to reply to error: {inner_e}")


def _Admin_Process(message: ElementHandle, fun_name: str) -> None:
    global pause_mode
    if fun_name in ["pause_on", "pause_off", "pause_show"]:
        helper.react(message=message, page=page)
    try:
        if fun_name == "pause_on":
            pause_mode = True
            print("Pause Enabled ✅")
            rep.reply(page=page, locator=message, text="Pause Enabled ✅")

        elif fun_name == "pause_off":
            pause_mode = False
            print("Pause Disabled ❌")
            rep.reply(page=page, locator=message, text="Pause Disabled ❌")

        elif fun_name == "pause_show":
            print(f"Pause Status: {'ON' if pause_mode else 'OFF'}")
            rep.reply(page=page, locator=message, text=f"Pause Status: `{'ON' if pause_mode else 'OFF'}`")

        else:
            _process_cmd(message, fun_name)

    except Exception as e:
        print(f"[Admin_Process Error] {e}")
        rep.reply(page=page, locator=message, text=f"❗ Error in admin command:\n`{e}`")


def _process_cmd(message: ElementHandle, text: str) -> None:
    if text in ["showq", "...help"]:
        helper.react(message=message, page=page)
    try:
        if text == "...help":
            rep.reply(page=page, locator=message, text=helper.menu.menu())

        elif text == "showq":
            helper.showq(page=page, locator=message)

        elif text == SETTINGS.NLP:
            helper.nlp(page=page, locator=message, f_info=text.replace(SETTINGS.NLP, ""))

        else:
            _natural_cmd(message=message, text=text)

    except Exception as e:
        print(f"[Process_Cmd Error] {e}")
        rep.reply(page=page, locator=message, text=f"❗ Error in command:\n`{e}`")


def _natural_cmd(message: ElementHandle, text: str) -> None:
    """
    Processes a natural command from user text and calls post-processing.

    Args:
        message (ElementHandle): The message element where the command came from.
        text (str): The full text containing the command.
    """
    try:
        parts = text.strip().split(" ", 2)

        if len(parts) < 2:
            print("Not Correct Command. Usage: /quant <f_name> [f_info]")
            rep.reply(page=page, locator=message, text="❗ Usage: /quant <f_name> [f_info]")
            return

        f_name = parts[1].lower().strip()
        f_info = parts[2].strip() if len(parts) > 2 else ""

        process.post_process(page=page, message=message, f_name=f_name, f_info=f_info)

    except Exception as e:
        print(f"[Natural_Cmd Error] {e}")
        rep.reply(page=page, locator=message, text=f"❗ Natural command error:\n`{e}`")


def Time() -> str: return datetime.now().strftime("%-I : %M:%S %p").lower()


def PersonalChatCheck(chat: Locator) -> bool:
    try:
        if debug: print("In personal Chat check")
        you = chat.get_by_role("gridcell").get_by_text("(You)", exact=True)

        if you.is_visible():
            # ha.move_mouse_to_locator(page=page, locator=chat.element_handle())
            chat.click()
            messages = sc.messages(page=page)
            message = messages.nth(0).element_handle()  # Any message can define the authentication

            num = ex.getJID_mess(message).replace("@c.us", "")
            BOT_NUMBER = re.sub(r"\D", "", SETTINGS.BOT_NUMBER)
            print(f"NUMBER : [{num}] - [{BOT_NUMBER in num} - {BOT_NUMBER}]")
            return BOT_NUMBER in num  # Authorisation complete .

        elif debug:
            print("No (You) found.")

    except Exception as e:
        print(f"Error in Personal Chat Check [{e}]")
    return False


def pause_handle(p_auth: bool, t: str, sender: str, text: str, message: ElementHandle) -> None:
    if pause_mode:
        if t in ["pause_off", "pause_show"] and p_auth:
            _Admin_Process(message, text)
        else:
            print(f"Paused. Ignoring '{t}' from {sender}")
        return
