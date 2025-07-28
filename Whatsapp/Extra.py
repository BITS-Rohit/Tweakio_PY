import datetime
import pickle
import random
import re
import time

from playwright.sync_api import Page, Locator

from Whatsapp import selectors_config as sc, SETTINGS, HumanAction as ha, pre_dir as pwd

"""
console.log("innerWidth:", window.innerWidth);
console.log("innerHeight:", window.innerHeight);
console.log("outerWidth:", window.outerWidth);
console.log("outerHeight:", window.outerHeight);
console.log("screen.width:", screen.width);
console.log("screen.height:", screen.height);

"""


def MessageToChat(page: Page) -> None:
    sbox = sc.searchBox_chatList_panel(page)
    if sbox is None:
        print("sbox is  None")
        return
    else:
        print("search box seen")
    ha.move_mouse_to_locator(page, sbox)
    print("hovered")
    sbox.click()
    print("clicked")
    sbox.fill("")
    sbox.fill("7678686855")
    print("filled number")
    time.sleep(random.uniform(1.0, 2.0))

    firstPick = page.locator("div[role='listitem'] >> div[role='button']").first
    if firstPick is None:
        print("first_pick locator failed in message to owner")
        return
    else:
        print("First pick is seen")
    firstPick.hover()
    firstPick.click()

    mess = sc.message_box(page)
    if mess is None:
        print("messages locator failed in message to owner")
    ha.move_mouse_to_locator(page, mess)
    mess.click()
    mess.fill("")
    mess.fill("Logged in, Success.Tweakio: Hi !")
    mess.press("Enter")
    page.keyboard.press("Escape")
    sc.wa_icon(page).click()


def SeedCache(page: Page, ids: dict) -> None:
    """
    It logs the message which was not seen till now and store them with message data.
    :param page:
    :param ids:
    :return: None
    """
    print("Seeding started \n Info -----")

    chats = sc.chat_items(page)
    print("Total Chats on this account : %s" % (sc.total_chats(page)))
    print("Agent Reachable Chats : %s" % (chats.count()))
    print("Allowed Top Chats [Default 5] : %s" % SETTINGS.MAX_CHAT)

    for i in range(min(chats.count(), SETTINGS.MAX_CHAT)):  # Top chats.
        chat = chats.nth(i)
        name = sc.getChatName(chat)
        print(f"Processing chat no. {i + 1} : {name}")
        ha.move_mouse_to_locator(page, chat)
        chat.click()
        time.sleep(random.randint(1, 2))

        # TODO Banlist logic coming in future updates.
        admin_cmds = ["pause_on", "pause_off", "pause_show", "showq", SETTINGS.NLP, "...help", SETTINGS.QUANTIFIER,
                      "--ban--", "--unban--"]
        messages = sc.messages(page)

        print(f"Message count for this chat : {messages.count()}")

        for y in range(messages.count()):
            message = messages.nth(y)
            m = sc.get_message_text(message).split(" ")[0].lower()
            if m in admin_cmds:
                if sc.get_dataID(message) not in ids:
                    trace_message(seen_messages=ids, chat=chat, message=message)

        # if sc.message_box(page) is None:
        #     print("message Box [Message panel Input Box] is None")
        #     break
        # ha.move_mouse_to_locator(page, sc.message_box(page))
        # sc.message_box(page).click()
        # sc.message_box(page).fill("")

        # TODO  unread marker

    print("Seeding done.")


def getJID_mess(message: Locator) -> str:
    """Returns the JID of the message"""
    data_id = sc.get_dataID(message)
    if not data_id or "_" not in data_id:
        return ""
    parts = data_id.split("_")
    return parts[1] if len(parts) > 1 else ""


def getSender_mess(message: Locator) -> str:
    """Returns the sender from the message"""
    attr = message.locator("div[data-pre-plain-text]").get_attribute("data-pre-plain-text")
    if not attr or "]" not in attr:
        return ""
    parts = attr.split("]")
    return parts[1].strip() if len(parts) > 1 else ""


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
    data_id = sc.get_dataID(message)
    if data_id in seen_messages:
        return

    seen_messages[data_id] = {
        "chat": sc.getChatName(chat),
        "community": sc.is_community(chat),
        "preview_url": sc.getChat_lowImg(chat),
        "jid": getJID_mess(message),
        "message": sc.get_message_text(message),
        "sender": getSender_mess(message),
        "time": get_Timestamp(message),
        "systime": time.time(),
        "direction": getDirection(message),
        "type": get_mess_type(message)
    }


def get_File_name(message: Locator, chat: Locator) -> str:
    # chat--sender--SYS_TIME
    name = sc.getChatName(chat=chat)
    sender = getSender_mess(message=message)
    time = get_datetime()
    return f"{name}--{sender}--{time}"


def get_datetime():
    now = datetime.datetime.now()
    return now.strftime("%d %B %Y, %I:%M %p")


# --- ---- Seen IDs ---- ---
def dump_ids(seen: dict) -> None:
    """Dump the seen dict to a pickle file."""
    with open(pwd.get_saved_data_ids(), "wb") as f:
        pickle.dump(seen, f)

def pick_ids() -> dict:
    """Load and return the seen dict from a pickle file."""
    path = pwd.get_saved_data_ids()
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return pickle.load(f)

# --- ---- Ban List ---- ---
def dump_banlist(banlist: list) -> None:
    """Dump the banlist (list) to a pickle file."""
    with open(pwd.get_ban_list(), "wb") as f:
        pickle.dump(banlist, f)

def pick_banlist() -> list:
    """Load and return the banlist from a pickle file."""
    path = pwd.get_ban_list()
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
            # Look for a number inside the badge
            number_span = unread_badge.locator("span").first
            text = number_span.inner_text().strip()
            return 1 if text.isdigit() else 0
        return 0
    except :
        return 0


def mark_unread(page : Page,chat: Locator) -> None:
    """it marks unread back"""
    try:
        ha.move_mouse_to_locator(page,chat)
        chat.click(button="right")
        page.get_by_role("application").locator("li span").get_by_text(re.compile("mark as unread", re.I)).click()
    except Exception as e :
        if page.get_by_role("application").locator("li span").get_by_text(re.compile("mark as read", re.I)).is_visible() :
            print(f" chat is already unread - [{sc.getChatName(chat)}] ")
        else : print(f"Error in mark unread : \n {e}")
