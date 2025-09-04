import datetime
import pathlib as pa
import pickle
import random
import shutil
import time
from typing import Union

from playwright.sync_api import Page, Locator, ElementHandle

from Whatsapp import selectors_config as sc, pre_dir as pwd, ___ as _


def MessageToChat(page: Page) -> None:
    print("Messaging to owner.")
    sbox = sc.searchBox_chatList_panel(page)
    if sbox is None:
        print("sbox is  None")
        return
    else:
        print("search box seen")
    # ha.move_mouse_to_locator(page, sbox.element_handle())
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
        print("messages locator is Empty")
        return

    # ha.move_mouse_to_locator(page, mess)
    mess.click()
    mess.fill("")
    mess.fill("Logged in, Success.Tweakio: Hi !")
    mess.press("Enter")
    page.keyboard.press("Escape")
    sc.wa_icon(page).click()

    print("Messaged: Logged in, Success.Tweakio: Hi ! \n Messaging Done.")


def getJID_mess(message: Union[ElementHandle, Locator]) -> str:
    """Returns the JID of the message like: 7678xxxxxx@c.us"""
    if isinstance(message, Locator): message = message.element_handle(timeout=1001)
    data_id = sc.get_dataID(message)
    if not data_id or "_" not in data_id:
        return ""
    parts = data_id.split("_")
    return parts[1] if len(parts) > 1 else ""


def getSenderID(message: Union[ElementHandle, Locator]) -> str:
    """
    Returns the name if it does not have a sender else returns the number of senders.
    """
    if isinstance(message, Locator): message = message.element_handle(timeout=1001)
    raw = sc.get_dataID(message)

    def getfromlid() -> str:
        try:
            div = message.query_selector("div.copyable-text[data-pre-plain-text]")
            if not div:
                return ""
            attr = div.get_attribute("data-pre-plain-text")
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


def getGID_CID(message: Union[ElementHandle, Locator]) -> str:
    """Gives Group ID for groups and Chat ID for single chats"""
    if isinstance(message, Locator): message = message.element_handle(timeout=1001)
    try:
        raw = sc.get_dataID(message)
        print(f"raw : {raw}")
        if "g.cus" not in raw and "@c.us" in raw:
            return raw.split("_")[1]
        elif "@g.us" in raw:
            return raw.split("_", 2)[1]
        else:
            return ""
    except Exception as e:
        print(f"Error in GID_CID : [{e}]")
        return ""


def getDirection(message: ElementHandle) -> str:
    """Returns a direction [out: bot | in: other] showcasing the message from the bot number or from another number."""
    return "out" if sc.is_message_out(message) else "in"


def get_mess_type(message: Union[ElementHandle, Locator]) -> str:
    """Returns the specific type of message: image, video, audio, gif, sticker, quoted, text"""
    if isinstance(message, Locator): message = message.element_handle(timeout=1001)
    try:
        try:
            if sc.isVideo(message):
                return "video Message"
        except Exception as e:
            print(f"Error checking video: {e}")

        try:
            if sc.pic_handle(message):
                return "image Message"
        except Exception as e:
            print(f"Error checking image: {e}")

        try:
            if sc.is_Voice_Message(message):
                return "Voice Message"
        except Exception as e:
            print(f"Error checking audio: {e}")

        try:
            if sc.is_gif(message):
                return "gif Message"
        except Exception as e:
            print(f"Error checking gif: {e}")

        try:
            if sc.isSticker(message):
                return "sticker"
        except Exception as e:
            print(f"Error checking sticker: {e}")

        try:
            q = sc.isQuotedText(message)
            if q and q.is_visible():
                return "quoted"
        except Exception as e:
            print(f"Error checking quoted text: {e}")

        # Default
        return "text"

    except Exception as e:
        print(f"Unexpected error in get_mess_type: {e}")
        return "unknown"


def get_Timestamp(message: Union[ElementHandle, Locator]) -> str:
    """Returns TimeStamp of the WhatsApp stored Time of the message."""
    if isinstance(message, Locator): message = message.element_handle(timeout=1001)
    try:
        element = message.query_selector("div[data-pre-plain-text]")
        if element:
            data = element.get_attribute("data-pre-plain-text")
            if data:
                # WhatsApp format: [4:25 PM, 7/26/2025] Time: Sender
                return data.split("]")[0].strip("[")
        return ""
    except Exception as e:
        print(f"Error in get_Timestamp : [{e}]")
        return ""


def trace_message(seen_messages: dict, chat: Union[ElementHandle, Locator],
                  message: Union[ElementHandle, Locator]) -> None:
    """Tracks a unique message and stores its details if not already seen."""
    # Till now, we are here incoming the Locator.
    try:
        data_id = sc.get_dataID(message)
        if data_id in seen_messages:
            return

        seen_messages[data_id] = {
            "chat": sc.getChatName(chat),
            "community": sc.is_community(chat),
            "preview_url": sc.getChat_low_Quality_Img(chat),
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
def is_unread(chat: Union[ElementHandle, Locator]) -> int:
    """
    Return 1 if the chat has actual unread messages (with a numeric count),
    else 0 if only marked as unread manually (no numeric badge).
    """
    if isinstance(chat, Locator): chat = chat.element_handle(timeout=1001)
    try:
        unread_badge = chat.query_selector("[aria-label*='unread']")
        if unread_badge:
            number_span = unread_badge.query_selector("span")
            if number_span:
                text = number_span.inner_text().strip()
                return 1 if text.isdigit() else 0
        return 0
    except Exception as e:
        print(f"[is_unread] Error: {e}")
        return 0


def do_unread(page: Page, chat: Union[ElementHandle, Locator]) -> None:
    """
    Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'.
    """
    if isinstance(chat, Locator): chat = chat.element_handle(timeout=1001)
    try:
        # ha.move_mouse_to_locator(page, chat)
        chat.click(button="right")
        time.sleep(random.uniform(1.3, 2.5))

        app_menu = page.query_selector("role=application")  # top-level menu
        if not app_menu:
            raise Exception("Application menu not found")

        unread_option = app_menu.query_selector("li span:text-matches('mark as unread', 'i')")
        if unread_option:
            # ha.move_mouse_to_locator(page, unread_option)
            unread_option.click(timeout=random.randint(1701, 2001))
        else:
            raise Exception("'Mark as unread' option not found or not visible")

    except Exception as e:
        try:
            read_option = page.query_selector("role=application").query_selector(
                "li span:text-matches('mark as read', 'i')"
            )
            if read_option:
                print(f"Chat is already unread — [{sc.getChatName(chat)}]")
            else:
                raise
        except:
            print(f"[do_unread] Error marking unread: {e}")

        # Reset state by clicking outside (WA icon)
        wa_icon = sc.wa_icon(page)
        # ha.move_mouse_to_locator(page, wa_icon)
        wa_icon.click()


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


def get_LocatorBack(page: Page, element: ElementHandle) -> Locator:
    """
    Returns a locator with unique css extracted from the element Handle
    :param page:
    :param element:
    :return:
    """
    css = element.evaluate("""
    (el) => {
        function cssPath(el) {
            if (!(el instanceof Element)) return;
            const path = [];
            while (el.nodeType === Node.ELEMENT_NODE) {
                let selector = el.nodeName.toLowerCase();
                if (el.id) {
                    selector += '#' + el.id;
                    path.unshift(selector);
                    break;
                } else {
                    let sib = el, nth = 1;
                    while (sib = sib.previousElementSibling) {
                        if (sib.nodeName.toLowerCase() === selector) nth++;
                    }
                    if (nth != 1) selector += `:nth-of-type(${nth})`;
                }
                path.unshift(selector);
                el = el.parentNode;
            }
            return path.join(" > ");
        }
        return cssPath(el);
    }
    """)
    return page.locator(css)
