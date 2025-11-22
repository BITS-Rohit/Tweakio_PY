import random
import re
import time
from datetime import datetime
from typing import Union

from playwright.sync_api import Locator, Page, ElementHandle

from Whatsapp import SETTINGS, selectors_config as sc, Extra as ex, ___ as _, Methods as helper, \
    Reply as rep, Agent_Commands as process, pre_dir as pwd

# ----------------------------------------------------------------------------------------------------------------------
debug = False
refreshTime = SETTINGS.REFRESH_TIME
pause_mode = False
page : Page
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
                chat = chats.nth(i)
                _check_messages(chat, y)  # Pass as Locator to avoid Stale Pointers
                y += 1
                time.sleep(random.uniform(1.23, 2.22))

    except Exception as e:
        print(f"Handle chats error: {e}")


def _check_messages(chat: Union[ElementHandle, Locator], y: int) -> None:
    admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", "...help",
                  SETTINGS.NLP, SETTINGS.QUANTIFIER, "--ban--", "--unban--"]
    try:
        name = sc.getChatName(chat)
        if name == "":
            print("Error getting chat name : ")

        Personal_auth = PersonalChatCheck(chat=chat)
        if not Personal_auth:
            unread = ex.is_unread(chat)
            if unread == 0:
                print(f"-- --  Skipping Top chat [no - {y}] with name - {name} -- -- {Time()}")
                return

        print(f"Opening Top chat [no - {y}] with name -  {name} ")
        print("--Top chat has new messages--")
        chat.click(timeout=3000)
        try:
            print("<><><><><><><><><><><><><><>")

            # fetch initial messages
            messages = sc.messages(page)
            n = messages.count()
            if not n:
                raise Exception("No messages found in opened chat.")

            # get last message ID
            last_ID = sc.get_dataID(messages.nth(n - 1).element_handle(timeout=1000))
            if not last_ID:
                raise Exception("Data ID is not init in last message // Brain // check messages")

            # live loop
            Loop_Idx = 0
            while Loop_Idx< 5:
                print(f"Total messages fetched : {n}")

                for i in range(n):
                    message = messages.nth(i)
                    text = sc.get_message_text(message).strip()

                    if not text or text.split(" ")[0].lower() not in admin_cmds:
                        continue

                    # auth handler
                    _auth_handle(
                        page=page,
                        Locator_message=message,
                        text=text,
                        Locator_chat=chat,
                        p_chat=Personal_auth,
                    )

                # refresh messages
                time.sleep(random.uniform(0.5 , 1.2)) # Refresh Time

                messages = sc.messages(page)
                current_last_id = sc.get_dataID(messages.nth(n - 1).element_handle(timeout=1000))

                if not current_last_id:
                    raise Exception("Data ID is not correct in last message // Brain // check messages")

                if current_last_id == last_ID:
                    break  # No new messages

                # update last_ID + message count for next iteration
                last_ID = current_last_id
                n = messages.count()
                Loop_Idx+=1

            print("<><><><><><><><><><><><><><>")

            if not Personal_auth:
                ex.do_unread(page=page, chat=chat)

        except Exception as e:
            print(f"[ERROR] Live messages loop failed: {e}")



    except Exception as e:
        print(f"Error in check messages : {e}")


def _auth_handle(page: Page, Locator_message: Union[ElementHandle, Locator], text: str,
                 Locator_chat: Union[ElementHandle, Locator],
                 p_chat: bool = False) -> None:

    message: Optional[ElementHandle] = None

    try:
        if isinstance(Locator_message, Locator):
            message = Locator_message.element_handle()
        else:
            message = Locator_message

        if isinstance(Locator_chat, Locator):
            chat = Locator_chat.element_handle()
        else:
            chat = Locator_chat

        t = text.split(" ", 1)[0].lower().strip()
        data_id = sc.get_dataID(message)

        if not data_id:
            print(f"[Empty data-ID]- Message: [{text}]")
            return

        if data_id in _.seen_ids:
            print(f"[Seen ID]- Message: [{text}]")
            return

        name = sc.getChatName(chat)
        ex.trace_message(_.seen_ids, Locator_chat, Locator_message)
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

        print(f"Prefix : {t}  -- Accepted : {SETTINGS.QUANTIFIER} ")

        attempts = 0
        while message.bounding_box() is None and attempts < 20:
            page.mouse.wheel(0, -random.randint(300, 499))
            page.wait_for_timeout(timeout=random.randint(300, 500))
            attempts += 1

        if message.bounding_box() is None:
            message.scroll_into_view_if_needed(timeout=2000)

        pause_handle(p_auth=Admin_AUTH, t=t, sender=sender, text=text, message=message)

        check = False

        def Ban_Handle(message: Union[ElementHandle, Locator]):
            nonlocal check
            GID = ex.getGID_CID(message)
            if p_chat:
                GID = "personal Chat"
            if Admin_AUTH and t in ["--ban--", "--unban--"]:
                if not GID:
                    print("Error: Chat name is empty during ban/unban check.")
                    return

                if p_chat:
                    helper.react(message=message, page=page)
                    rep.reply(page=page, element=message, text="`You can't ban/unban personal chat`")
                    check = True
                    return

                if t == "--unban--":
                    if GID in _.ban_list:
                        helper.react(page=page, message=message)
                        _.ban_list.remove(GID)
                        _.ban_change = True
                        print(f"`✅ Unbanned chat: [{name}]`")
                        rep.reply(page=page, element=message, text=f"`Unbanned chat: [{name}]`")
                        check = True
                    else:
                        rep.reply(page=page, element=message,
                                  text=f"`Chat[{name}] with GID[{GID}] is not in ban list.`")
                    return

                elif t == "--ban--":
                    if GID not in _.ban_list:
                        helper.react(page=page, message=message)
                        _.ban_list.append(GID)
                        rep.reply(page=page, element=message, text=f"`chat is banned now : [{name}]`")
                        check = True
                    else:
                        rep.reply(page=page, element=message, text=f"`[{name}] is already in ban list.`")
                    return

            if GID in _.ban_list:
                print("Banned chat. Returning.")
                check = True
                return

        try:
            Ban_Handle(message=message)
            if check:
                return
        except Exception as e:
            print(f" Error in Ban Handle : {e}")

        text = text.lower()

        def cmd_exec():
            admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", "...help",
                          SETTINGS.NLP, SETTINGS.QUANTIFIER, "--ban--", "--unban--"]

            user_cmds = [SETTINGS.NLP, SETTINGS.QUANTIFIER, "showq", "...help"]

            if Admin_AUTH and t in admin_cmds + user_cmds:
                _Admin_Process(message=message, fun_name=text, chat= Locator_chat)
            elif user_auth and t in user_cmds:
                _process_cmd(message=message, text=text, chat = Locator_chat)
            else:
                rep.reply(page=page, element=message,
                          text=f"Unauthorized command '{t}' from {sender}")

        try:
            cmd_exec()
        except Exception as e:
            print(f"Error in cmd_exec // user_auth handle : {e}")

        print("------------- Command processed  ---------------")

    except Exception as e:
        print(f"⚠️ Error in _auth_handle(): {e}")
        try:
            if message:   # 🔥 FIX: only reply if message exists
                rep.reply(page=page, element=message, text="⚠️ Internal error occurred while processing.")
            else:
                print("⚠️ Could not reply because message was not initialized.")
        except Exception as inner_e:
            print(f"⚠️ Failed to reply to error: {inner_e}")



def _Admin_Process(message: ElementHandle, fun_name: str, chat : Union[ElementHandle,Locator]) -> None:
    global pause_mode
    if fun_name in ["pause_on", "pause_off", "pause_show"]:
        helper.react(message=message, page=page)
    try:
        if fun_name == "pause_on":
            pause_mode = True
            print("Pause Enabled ✅")
            rep.reply(page=page, element=message, text="Pause Enabled ✅")

        elif fun_name == "pause_off":
            pause_mode = False
            print("Pause Disabled ❌")
            rep.reply(page=page, element=message, text="Pause Disabled ❌")

        elif fun_name == "pause_show":
            print(f"Pause Status: {'ON' if pause_mode else 'OFF'}")
            rep.reply(page=page, element=message, text=f"Pause Status: `{'ON' if pause_mode else 'OFF'}`")

        else:
            _process_cmd(message, fun_name, chat)

    except Exception as e:
        print(f"[Admin_Process Error] {e}")
        rep.reply(page=page, element=message, text=f"❗ Error in admin command:\n`{e}`")


def _process_cmd(message: ElementHandle, text: str, chat : Union[ElementHandle,Locator]) -> None:
    if text in ["showq", "...help"]:
        helper.react(message=message, page=page)
    try:
        if text == "...help":
            rep.reply(page=page, element=message, text=helper.menu.menu())

        elif text == "showq":
            helper.showq(page=page, locator=message)

        elif text == SETTINGS.NLP:
            helper.nlp(page=page, message
            =message, f_info=text.replace(SETTINGS.NLP, ""))

        else:
            _natural_cmd(message=message, text=text, chat =chat)

    except Exception as e:
        print(f"[Process_Cmd Error] {e}")
        rep.reply(page=page, element=message, text=f"❗ Error in command:\n`{e}`")


def _natural_cmd(message: ElementHandle, text: str, chat : Union[ElementHandle,Locator]) -> None:
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
            rep.reply(page=page, element=message, text="❗ Usage: /quant <f_name> [f_info]")
            return

        f_name = parts[1].lower().strip()
        f_info = parts[2].strip() if len(parts) > 2 else ""

        process.Bot_Commands(page=page, message=message, f_name=f_name, f_info=f_info, chat=chat)

    except Exception as e:
        print(f"[Natural_Cmd Error] {e}")
        rep.reply(page=page, element=message, text=f"❗ Natural command error:\n`{e}`")


def Time() -> str: return datetime.now().strftime("%-I : %M:%S %p").lower()


def PersonalChatCheck(chat: Locator) -> bool:
    try:
        if debug: print("In personal Chat check")
        you = chat.get_by_role("gridcell").get_by_text("(You)", exact=True)

        if you.is_visible():
            try :
                chat.click(timeout=3000)
            except Exception as e:
                print(f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Personal Chat click failed %%%%%%%%%%%%%%%%%%%%%%%%%%%%%% \n {e}")
            messages = sc.messages(page=page)
            message = messages.nth(0).element_handle(timeout=1000)  # Any message can define the authentication

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
