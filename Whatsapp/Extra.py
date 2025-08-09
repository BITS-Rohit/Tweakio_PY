import datetime
import pathlib as pa
import pickle
import random
import re
import shutil
import time

from playwright.sync_api import Page, Locator

from Whatsapp import selectors_config as sc, HumanAction as ha, pre_dir as pwd, ___ as _


def MessageToChat(page: Page) -> None:
    print("Messaging to owner.")
    sbox = sc.searchBox_chatList_panel(page)
    if sbox is None:
        print("sbox is  None")
        return
    else:
        print("search box seen")
    ha.move_mouse_to_locator(page, sbox)
    sbox.click()
    sbox.fill("")
    sbox.fill("7678686855")
    time.sleep(random.uniform(1.0, 2.0))

    firstPick = page.locator("div[role='listitem'] >> div[role='button']").first
    if firstPick is None:
        print("first_pick locator failed in message to owner")
        return

    firstPick.hover()
    firstPick.click()

    mess = sc.message_box(page)
    if mess is None:
        print("messages locator failed in message to owner")
        return

    ha.move_mouse_to_locator(page, mess)
    mess.click()
    mess.fill("")
    mess.fill("Logged in, Success.Tweakio: Hi !")
    mess.press("Enter")
    page.keyboard.press("Escape")
    sc.wa_icon(page).click()

    print("Messaged: Logged in, Success.Tweakio: Hi ! \n Messaging Done.")


def getJID_mess(message: Locator) -> str:
    """Returns the JID of the message  like : 7678xxxxxx@c.us"""
    data_id = sc.get_dataID(message)
    if not data_id or "_" not in data_id:
        return ""
    parts = data_id.split("_")
    return parts[1] if len(parts) > 1 else ""


def getSenderID(message: Locator) -> str:
    """
    Returns the name if it does not have a sender else returns the number of senders
    """
    raw = sc.get_dataID(message)

    def getfromlid() -> str:
        try:
            attr = message.locator("div.copyable-text[data-pre-plain-text]").get_attribute("data-pre-plain-text")
            if not attr or "]" not in attr:
                print("[data-pre-plain-text] Content is not properly formatted.")
                return ""
            parts = attr.split("]", 1)
            return parts[1].strip()[: -1] if len(parts) > 1 else ""
        except Exception as e:
            print(f"Error extracting sender: {e}")
            return ""

    if "@lid" in raw:
        return getfromlid()
    elif "@c.us" in raw and "@g.us" in raw:
        return raw.split("_", 3)[3].replace("@c.us", "")
    elif "@c.us" in raw:
        return raw.split("_", 2)[1].replace("@c.us", "")
    else:
        return ""


def getGroudID(message: Locator) -> str:
    raw = sc.get_dataID(message)
    if "@g.us" in raw:
        return raw.split("_", 2)[1]
    else:
        return ""


def getDirection(message: Locator) -> str:
    """Returns a direction [out: bot | in: other] showcasing the message from the bot number or from another number"""
    return "out" if sc.is_message_out(message) else "in"


def get_mess_type(message: Locator) -> str:
    """Returns the specific type of message : image , video, audio, gif, sticker, quoted, text"""
    if sc.isPic(message).is_visible():
        return "image"
    elif sc.isVideo(message).is_visible():
        return "video"
    elif sc.is_Voice_Message(message).is_visible():
        return "audio"
    elif sc.is_gif(message).is_visible():
        return "gif"
    elif sc.isSticker(message):
        return "sticker"
    elif sc.isQuotedText(message).is_visible():
        return "quoted"
    else:
        return "text"


def get_Timestamp(message: Locator) -> str:
    """Returns TimeStamp of the WhatsApp stored Time of the message"""
    element = message.locator("div[data-pre-plain-text]").first
    if element:
        data = element.get_attribute("data-pre-plain-text")
        if data:
            # WhatsApp format: [4:25 PM, 7/26/2025] Time: Sender
            return data.split("]")[0].strip("[")  # Extract "4:25 PM, 7/26/2025"
    return ""


def trace_message(seen_messages: dict, chat: Locator, message: Locator) -> None:
    try:
        data_id = sc.get_dataID(message)
        if data_id in seen_messages:
            return

        seen_messages[data_id] = {
            "chat": sc.getChatName(chat),
            "community": sc.is_community(chat),
            "preview_url": sc.getChat_lowImg(chat),
            "jid": getJID_mess(message),
            "message": sc.get_message_text(message),
            "sender": getSenderID(message),
            "time": get_Timestamp(message),
            "systime": time.time(),
            "direction": getDirection(message),
            "type": get_mess_type(message)
        }
    except Exception as e:
        print(f"Error in Trace message : {e}")


def get_File_name(message: Locator, chat: Locator) -> str:
    # chat--sender--SYS_TIME
    name = sc.getChatName(chat=chat)
    sender = getSenderID(message=message)
    time = get_datetime()
    return f"{name}--{sender}--{time}"


def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%d %B %Y, %I:%M %p")


# --- ---- Seen IDs ---- ---
def dump_ids(seen: dict) -> None:
    """Dump the seen dict to a pickle file."""
    if not seen:
        print("Empty Seen ids map, Not saving")
        return
    with open(pwd.get_saved_data_ids(), "wb") as f:
        pickle.dump(seen, f)


def pick_ids() -> dict:
    """Load and return the seen dict from a pickle file safely."""
    path = pwd.get_saved_data_ids()
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except (EOFError, pickle.UnpicklingError) as e:
        print(f"[ERROR] Failed to load seen_ids from {path}: {e}")
        path.unlink(missing_ok=True)
        return {}


# --- ---- Ban List ---- ---
def dump_banlist(banlist: list) -> None:
    """Dump the banlist (list) to a pickle file."""
    if not banlist and not _.ban_change:
        print("Empty Banlist with no change , Not saving.")
        return
    with open(pwd.get_ban_list(), "wb") as f:
        pickle.dump(banlist, f)


def pick_banlist() -> list:
    """Load and return the banlist from a pickle file."""
    path = pwd.get_ban_list()
    if not path.exists():
        return []
    with open(path, "rb") as f:
        return pickle.load(f)


def dump_admin(admin_list: list) -> None:
    """Dump the list of admin to a pickle file"""
    if not admin_list and not _.admin_change:
        print("Empty Admin list with no change , Not saving.")
        return
    with open(pwd.get_admin_list(), "wb") as f:
        pickle.dump(admin_list, f)


def pick_adminList() -> list:
    path = pwd.get_admin_list()
    if not path.exists():
        return []
    with open(path, "rb") as f:
        return pickle.load(f)


# --- ---- Unread Handle ---- ---
def is_unread(chat: Locator) -> int:
    """Return 1 if the chat has actual unread messages (with a count),
    else 0 if only marked as unread manually (e.g., no numeric badge)."""
    try:
        unread_badge = chat.locator("[aria-label*='unread']")
        if unread_badge.is_visible():
            # Look for a number
            number_span = unread_badge.locator("span").first
            text = number_span.inner_text().strip()
            return 1 if text.isdigit() else 0
        return 0
    except:
        return 0


def do_unread(page: Page, chat: Locator) -> None:
    """Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'."""
    try:
        ha.move_mouse_to_locator(page, chat)
        chat.click(button="right")
        time.sleep(random.uniform(1.5, 2.5))

        unread_option = page.get_by_role("application").locator("li span").get_by_text(
            re.compile("mark as unread", re.I))

        if unread_option.is_visible():
            ha.move_mouse_to_locator(page, unread_option)
            unread_option.click(timeout=2000)
        else:
            raise Exception("Option 'Mark as unread' not visible or Click error")

    except Exception as e:
        try:
            read_option = page.get_by_role("application").locator("li span").get_by_text(
                re.compile("mark as read", re.I))
            if read_option.is_visible():
                print(f"Chat is already unread — [{sc.getChatName(chat)}]")
            else:
                raise
        except:
            print(f"Error in mark_unread: {e}")

        # Reset state by clicking outside (WA icon)
        ha.move_mouse_to_locator(page, sc.wa_icon(page))
        sc.wa_icon(page).click()


def cleanFolder(folder: pa.Path) -> None:
    if folder.exists():
        for item in folder.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"⚠️ Could not delete {item}: {e}")


