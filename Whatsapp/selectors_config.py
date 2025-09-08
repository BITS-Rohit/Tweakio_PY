"""
Helper functions to interact with various WhatsApp Web UI components using Playwright.

Conventions:
- `page`: refers to `playwright.sync_api.Page` instance.
- All other elements returned are of the type `Locator`.
- Utility functions are written to extract attributes or recognize content like images, videos, or quoted messages.
"""
import re
from typing import Union

from playwright.sync_api import ElementHandle, Locator, Page


def chat_list(page: Page) -> Locator:
    """Returns the chat list grid locator on the main UI."""
    return page.get_by_role("grid", name=re.compile("chat list", re.I))


def message_chat_panel(page: Page) -> Locator:
    """ Gives the message container panel"""
    return page.locator("div[id='main']").get_by_role("application").first


def new_chat_chat_list_panel(page: Page) -> Locator:
    """ Return the locator for the new chat on the chat list upper panel"""
    return page.get_by_role("button", name=re.compile("new chat", re.I)).first


def searchBox_chatList_panel(page: Page) -> Locator:
    """Returns the search box on the chat list panel"""
    return page.get_by_role("textbox", name=re.compile("search input textbox", re.I)).first


def message_box(page: Page) -> Locator:
    """Message Input box on the message panel"""
    return page.locator("footer").get_by_role("textbox").first


def wa_icon(page: Page) -> Locator:
    """WhatsApp icon locator"""
    return page.get_by_role("heading", name="WhatsApp").first


def chat_list_filters_ALL(page: Page) -> Locator:
    """Return the chat list filter : ALL """
    return page.locator("#all-filter")


def chat_list_filters_Unread(page: Page) -> Locator:
    """Return the chat list filter : Unread"""
    return page.locator("#unread-filter")


def chat_list_filters_favorites(page: Page) -> Locator:
    """Return the chat list filter : Favorites"""
    return page.locator("#favorites-filter")


def chat_list_filters_groups(page: Page) -> Locator:
    """Return the chat list filter : Groups"""
    return page.locator("#group-filter")


def total_chats(page: Page) -> int:
    """Returns the total number of chats visible in the chat list."""
    return int(chat_list(page).get_attribute("aria-rowcount"))


def chat_items(page: Page) -> Locator:
    """Returns a locator for all individual chat items (buttons) in the list."""
    return chat_list(page).get_by_role("listitem")


def getChat_low_Quality_Img(chat: Union[ElementHandle, Locator]) -> str:
    """Extracts the low-quality image (thumbnail) from a chat preview item."""
    if isinstance(chat, Locator): chat = chat.element_handle(timeout=1001)
    img_el = chat.query_selector_all("img[src]")[0]
    if img_el and img_el.is_visible():
        return img_el.get_attribute("src")
    return ""


def getChatName(chat: Union[ElementHandle, Locator]) -> str:
    """Returns the primary chat name (first span[title]) or empty string."""
    if isinstance(chat, Locator): chat = chat.element_handle(timeout=1001)
    if is_community(chat):
        return chat.query_selector_all("span[title]")[1].get_attribute("title") or ""
    span = chat.query_selector("span[title]")
    if span:
        return span.get_attribute("title") or ""
    return ""


def is_community(chat: Union[ElementHandle, Locator]) -> str:
    """
    If this chat item has the 'default-community-refreshed' icon,
    return the community name (the span[title] without a data-icon).
    """
    if isinstance(chat, Locator): chat = chat.element_handle(timeout=1001)

    icon = chat.query_selector("span[data-icon='default-community-refreshed']")
    if icon and icon.is_visible():
        name_span = chat.query_selector_all("span[title]")
        return name_span[0].get_attribute("title") if name_span else ""
    return ""


def Profile_header(page: Page) -> Locator:
    """
    Returns the profile header button locator used to open contact details.
    Used when a chat is opened and the top bar includes profile/name/media access.
    """
    return page.locator("header").get_by_role("button", name=re.compile("profile details", re.I))


def qr_canvas(page: Page) -> Locator:
    """Returns the QR canvas image for login."""
    return page.get_by_role("img", name=re.compile(r"scan.*qr", re.I))


# -------------------- Sidebar Navigation -------------------- #

def _side_Bar_chats(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Chats'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("chats", re.I))


def _side_Bar_status(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Status Updates'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("updates in status", re.I))


def _side_Bar_channels(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Channels'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("channels", re.I))


def _side_Bar_Communities(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Communities'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("communities", re.I))


# -------------------- Messages Section -------------------- #

def messages(page: Page) -> Locator:
    """
    Returns a locator for all messages in the current open chat.
    Each message element has a unique `data-id` and role "row".
    """
    return page.locator('[role="row"] div[data-id]')


def messages_incoming(page: Page) -> Locator:
    """Filter for the personal | group chat incoming messages"""
    return page.locator('[role="row"] div[data-id] .message-in')


def messages_outgoing(page: Page) -> Locator:
    """Filter for the personal | group chat outgoing messages"""
    return page.locator('[role="row"] div[data-id] .message-out')


def get_message_text(message_element: Union[ElementHandle, Locator]) -> str:
    """Returns the text content of a message if visible."""
    if isinstance(message_element, Locator): message_element = message_element.element_handle()
    span = message_element.query_selector("span.selectable-text.copyable-text")
    if span and span.is_visible():
        return span.text_content() or ""
    return ""

# def get_message_text(element: Locator | ElementHandle) -> str:
#     return element.inner_text().strip()


def is_message_out(message: Union[ElementHandle, Locator]) -> bool:
    """Returns True if the message is outgoing (sent by bot)."""
    if isinstance(message, ElementHandle):
        element = message.query_selector(".message-out")
    else:
        element = message.locator(".message-out")
    return element is not None and element.is_visible()


def get_dataID(message: Union[ElementHandle, Locator]) -> str:
    """Returns the unique data-id attribute of a message."""
    return message.get_attribute("data-id") or ""


# -------------------- Media Send  -------------------- #
def plus_rounded_icon(page: Page) -> Locator:
    """
    It is a locator for the plus icon in the message box for opening menu with options like : image , videos ,documents to send
    :param page:
    :return:
    """
    return page.get_by_role("button").locator("span[data-icon]").filter(has_text=re.compile("plus-rounded", re.I)).first


def document(page: Page) -> Locator:
    """Safely locates the 'Document' upload option in the menu"""
    return page.get_by_role("button", name="Document").first


def photos_videos(page: Page) -> Locator:
    """Safely locates the 'Photos & videos' upload option in the menu"""
    return page.get_by_role("button", name="Photos & videos").first


def camera(page: Page) -> Locator:
    """Safely locates the 'Camera' upload option in the menu"""
    return page.get_by_role("button", name="Camera").first


def audio(page: Page) -> Locator:
    """Safely locates the 'Audio' upload option in the menu"""
    return page.get_by_role("button", name="Audio").first


def contact(page: Page) -> Locator:
    """Safely locates the 'Contact' upload option in the menu"""
    return page.get_by_role("button", name="Contact").first


def poll(page: Page) -> Locator:
    """Safely locates the 'Poll' upload option in the menu"""
    return page.get_by_role("button", name="Poll").first


def event(page: Page) -> Locator:
    """Safely locates the 'Event' upload option in the menu"""
    return page.get_by_role("button", name="Event").first


def new_sticker(page: Page) -> Locator:
    """Safely locates the 'New sticker' upload option in the menu"""
    return page.get_by_role("button", name="New sticker")


# -------------------- Message Type Checkers -------------------- #

def get_mess_pic_url(message: ElementHandle) -> str:
    """Extracts the image URL from an incoming picture message if visible."""
    img_el = message.query_selector("img")
    if img_el:
        return img_el.get_attribute("src") or ""
    return ""


def isReacted(message: Union[ElementHandle, Locator]) -> bool:
    """Check if the message is reacted or not"""
    try:
        if isinstance(message, Locator): message = message.element_handle(timeout=1001)
        btn = message.query_selector("button[aria-label*='reaction 👍']")
        return btn.is_visible() if btn else False
    except:
        return False


def pic_handle(message: ElementHandle) -> bool:
    pic = message.query_selector(
        "xpath=.//div[@role='button' and "
        "translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='open picture']//img"
    )
    if pic and pic.is_visible():
        return True
    pic2 = message.query_selector("xpath=.//img[contains(@src,'data:image/')]")
    return pic2.is_visible() if pic2 else False


def isVideo(message: ElementHandle) -> bool:
    video = message.query_selector(
        "xpath=.//span[@data-icon='media-play' or @data-icon='msg-video']"
    )
    return video.is_visible() if video else False


def is_Voice_Message(message: ElementHandle) -> bool:
    voice = message.query_selector(
        "xpath=.//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'voice message')]"
    )
    if voice and voice.is_visible():
        return True
    voice2 = message.query_selector(
        "xpath=.//span[contains(translate(@data-icon,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'audio-play')]"
    )
    return voice2.is_visible() if voice2 else False


def is_gif(message: ElementHandle) -> bool:
    gif_btn = message.query_selector(
        "xpath=.//div[@role='button' and "
        "contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'play gif')]"
    )
    if gif_btn and gif_btn.is_visible():
        return True
    gif2 = message.query_selector(
        "xpath=.//span[contains(translate(@data-icon,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'media-gif')]"
    )
    return gif2.is_visible() if gif2 else False


def is_animated_sticker(message: ElementHandle) -> bool:
    """
    Animated stickers typically have <img alt="Sticker"> with dynamic alt text.
    """
    sticker = message.query_selector(
        "xpath=.//img[contains(translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'animated sticker')]"
    )
    return sticker.is_visible() if sticker else False


def is_plain_sticker(message: ElementHandle) -> bool:
    """
    Plain/static sticker detection via <img alt="Sticker with no label">.
    """
    sticker = message.query_selector(
        "xpath=.//img[contains(translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sticker with no label')]"
    )
    return sticker.is_visible() if sticker else False


def is_lottie_animation_sticker(message: ElementHandle) -> bool:
    """
    Lottie/SVG sticker detection (<svg> or <img src="blob:"> inside sticker button).
    """
    el = message.query_selector(
        "xpath=.//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sticker')]//img[contains(@src,'blob:')]"
    )
    return el.is_visible() if el else False


def isSticker(message: ElementHandle) -> bool:
    """Returns True if any sticker type is detected using XPath."""
    return is_animated_sticker(message) or is_plain_sticker(message) or is_lottie_animation_sticker(message)


# -------------------- Quoted Message Utilities -------------------- #

def isQuotedText(message: ElementHandle) -> ElementHandle:
    """
    Checks if a message is quoting another and returns the quoted‑message button handle.
    Matches any div with a data-pre-plain-text attribute, then its button labeled "Quoted message".
    """
    return message.query_selector("span.quoted-mention")


def get_QuotedText_handle(message: ElementHandle) -> str:
    """Returns the handle for the quoted-mention span inside a quoted message."""
    return isQuotedText(message).is_visible() or ""


# -- System -- #

def startup_popup_locator(page: Page) -> Locator:
    """Returns the startup continue popup button locator."""
    return page.get_by_role("button", name=re.compile("continue", re.I))


def popup2(page: Page):
    """
    2nd Pop up of WhatsApp with message:
    "Your chats and calls are private"
    """
    button = page.query_selector("div[data-animate-model-popup] button:text-is('OK')")
    if button:
        try:
            if button.is_visible():
                button.click()
        except Exception as e:
            print(f"[popup2] Click failed: {e}")


# ---------------------------- Message Other Option ------------------------------ #
"""
Options :
--Group info 
--select messages
--Mute notifications
--Disappearing messages
--Add to favourite
--close chat 
--clear chat 
--Exit group
"""


def group_info(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('group info')") if dialog else None


def select_messages(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('select messages')") if dialog else None


def mute_notifications(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('mute notifications')") if dialog else None


def disappearing_messages(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('disappearing messages')") if dialog else None


def add_to_fav(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('add to favourites')") if dialog else None


def close_chat(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('close chat')") if dialog else None


def clear_chat(page: Page) -> ElementHandle | None:
    dialog = page.query_selector("div[role='dialog']")
    return dialog.query_selector("li:has-text('clear chat')") if dialog else None
