"""
Helper functions to interact with various WhatsApp Web UI components using Playwright.

Conventions:
- `page`: refers to `playwright.sync_api.Page` instance.
- All other elements returned are of the type `Locator`.
- Utility functions are written to extract attributes or recognize content like images, videos, or quoted messages.
"""
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from playwright.sync_api import Locator, ElementHandle, Page


def chat_list(page: 'Page') -> 'Locator':
    """Returns the chat list grid locator on the main UI."""
    return page.get_by_role("grid", name=re.compile("chat list", re.I))


def message_chat_panel(page: 'Page') -> 'Locator':
    """ Gives the message container panel"""
    return page.locator("div[id='main']").get_by_role("application").first


def new_chat_chat_list_panel(page: 'Page') -> 'Locator':
    """ Return the locator for the new chat on the chat list upper panel"""
    return page.get_by_role("button", name=re.compile("new chat", re.I)).first


def searchBox_chatList_panel(page: 'Page') -> 'Locator':
    """Returns the search box on the chat list panel"""
    return page.get_by_role("textbox", name=re.compile("search input textbox", re.I)).first


def message_box(page: 'Page') -> 'Locator':
    """Message Input box on the message panel"""
    return page.get_by_role("textbox", name=re.compile("type a message", re.I))


def wa_icon(page: 'Page') -> 'Locator':
    """WhatsApp icon locator"""
    return page.get_by_role("heading", name="WhatsApp").first


def chat_list_filters_ALL(page: 'Page') -> 'Locator':
    """Return the chat list filter : ALL """
    return page.locator("#all-filter")


def chat_list_filters_Unread(page: 'Page') -> 'Locator':
    """Return the chat list filter : Unread"""
    return page.locator("#unread-filter")


def chat_list_filters_favorites(page: 'Page') -> 'Locator':
    """Return the chat list filter : Favorites"""
    return page.locator("#favorites-filter")


def chat_list_filters_groups(page: 'Page') -> 'Locator':
    """Return the chat list filter : Groups"""
    return page.locator("#group-filter")


def total_chats(page: 'Page') -> int:
    """Returns the total number of chats visible in the chat list."""
    return int(chat_list(page).get_attribute("aria-rowcount"))


def chat_items(page: 'Page') -> 'Locator':
    """Returns a locator for all individual chat items (buttons) in the list."""
    return chat_list(page).get_by_role("listitem")


def getChat_lowImg(chat: 'ElementHandle') -> str:
    """Extracts the low-quality image (thumbnail) from a chat preview item."""
    group_icon = chat.query_selector("span[data-icon='default-group-refreshed']")
    if group_icon and group_icon.is_visible():
        return "Default group icon"

    img_el = chat.query_selector("img")
    if img_el and img_el.is_visible():
        return img_el.get_attribute("src")

    return ""


def getChatName(chat: 'ElementHandle') -> str:
    """Returns the primary chat name (first span[title]) or empty string."""
    span = chat.query_selector("span[title]")
    if span:
        return span.get_attribute("title") or ""
    return ""


def is_community(chat: 'ElementHandle') -> str:
    """
    If this chat item has the 'default-community-refreshed' icon,
    return the community name (the span[title] without a data-icon).
    """
    icon = chat.query_selector("span[data-icon='default-community-refreshed']")
    if icon and icon.is_visible():
        # pick the first title‐span that does NOT have a data-icon
        name_span = chat.query_selector("span[title]:not([data-icon])")
        return name_span.get_attribute("title") if name_span else ""
    return ""


def Profile_header(page: 'Page') -> 'Locator':
    """
    Returns the profile header button locator used to open contact details.
    Used when a chat is opened and the top bar includes profile/name/media access.
    """
    return page.locator("header").get_by_role("button", name=re.compile("profile details", re.I))


def qr_canvas(page: 'Page') -> 'Locator':
    """Returns the QR canvas image for login."""
    return page.get_by_role("img", name=re.compile(r"scan.*qr", re.I))


# -------------------- Sidebar Navigation -------------------- #

def _side_Bar_chats(page: 'Page') -> 'Locator':
    """Returns the sidebar button locator for 'Chats'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("chats", re.I))


def _side_Bar_status(page: 'Page') -> 'Locator':
    """Returns the sidebar button locator for 'Status Updates'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("updates in status", re.I))


def _side_Bar_channels(page: 'Page') -> 'Locator':
    """Returns the sidebar button locator for 'Channels'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("channels", re.I))


def _side_Bar_Communities(page: 'Page') -> 'Locator':
    """Returns the sidebar button locator for 'Communities'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("communities", re.I))


# -------------------- Messages Section -------------------- #

def messages(page: 'Page') -> 'Locator':
    """
    Returns a locator for all messages in the current open chat.
    Each message element has a unique `data-id` and role "row".
    """
    return page.locator('[role="row"] div[data-id]')


def messages_incoming(page: 'Page') -> 'Locator':
    """Filter for the personal | group chat incoming messages"""
    return page.locator('[role="row"] div[data-id] .message-in')


def messages_outgoing(page: 'Page') -> 'Locator':
    """Filter for the personal | group chat outgoing messages"""
    return page.locator('[role="row"] div[data-id] .message-out')


def get_message_text(message_element: Union['ElementHandle', 'Locator']) -> str:
    """Returns the text content of a message if visible."""
    if isinstance(message_element, Locator): message_element = message_element.element_handle()
    span = message_element.query_selector("span.selectable-text.copyable-text")
    if span and span.is_visible():
        return span.text_content() or ""
    return ""


def is_message_out(message: 'ElementHandle') -> bool:
    """Returns True if the message is outgoing (sent by bot)."""
    element = message.query_selector(".message-out")
    return element is not None and element.is_visible()


def get_dataID(message: 'ElementHandle') -> str:
    """Returns the unique data-id attribute of a message."""
    return message.get_attribute("data-id") or ""


# -------------------- Media Send  -------------------- #
def plus_rounded_icon(page: 'Page') -> 'Locator':
    """
    It is a locator for the plus icon in the message box for opening menu with options like : image , videos ,documents to send
    :param page:
    :return:
    """
    return page.locator("button >> span[data-icon='plus-rounded']")


def document(page: 'Page') -> 'Locator':
    """Safely locates the 'Document' upload option in the menu"""
    return page.get_by_role("button", name="Document").first


def photos_videos(page: 'Page') -> 'Locator':
    """Safely locates the 'Photos & videos' upload option in the menu"""
    return page.get_by_role("button", name="Photos & videos").first


def camera(page: 'Page') -> 'Locator':
    """Safely locates the 'Camera' upload option in the menu"""
    return page.get_by_role("button", name="Camera").first


def audio(page: 'Page') -> 'Locator':
    """Safely locates the 'Audio' upload option in the menu"""
    return page.get_by_role("button", name="Audio").first


def contact(page: 'Page') -> 'Locator':
    """Safely locates the 'Contact' upload option in the menu"""
    return page.get_by_role("button", name="Contact").first


def poll(page: 'Page') -> 'Locator':
    """Safely locates the 'Poll' upload option in the menu"""
    return page.get_by_role("button", name="Poll").first


def event(page: 'Page') -> 'Locator':
    """Safely locates the 'Event' upload option in the menu"""
    return page.get_by_role("button", name="Event").first


def new_sticker(page: 'Page') -> 'Locator':
    """Safely locates the 'New sticker' upload option in the menu"""
    return page.get_by_role("button", name="New sticker")


# -------------------- Message Type Checkers -------------------- #

def get_mess_pic_url(message: 'ElementHandle') -> str:
    """Extracts the image URL from an incoming picture message if visible."""
    img_el = message.query_selector("img")
    if img_el:
        return img_el.get_attribute("src") or ""
    return ""


def isReacted(message: 'ElementHandle') -> bool:
    """Check if the message is reacted or not"""
    try:
        btn = message.query_selector("button[aria-label*='reaction 👍']")
        return btn.is_visible() if btn else False
    except:
        return False


def pic_handle(message: 'ElementHandle') -> bool:
    pic = message.query_selector(
        "xpath=.//div[@role='button' and translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='open picture']//img"
    )
    return pic.is_visible() if pic else False


def isVideo(message: 'ElementHandle') -> bool:
    """
    Check if a WhatsApp message DOM element (ElementHandle) is a video.
    Supports aria-hidden="true" icons.
    """
    return message.query_selector("div[role='button']").query_selector(
        "span[data-icon='media-play'],span[data-icon='msg-video']").is_visible()


def is_Voice_Message(message: 'ElementHandle') -> bool:
    voice = message.query_selector(
        "xpath=.//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'voice message')]"
    )
    return voice.is_visible() if voice else False


import re


def is_gif(message: 'ElementHandle') -> 'ElementHandle':
    """
    Checks if the WhatsApp message ElementHandle is a GIF message.

    :param message: Playwright ElementHandle pointing to the message element
    :return: The button element if it's a GIF, else None
    """
    # This matches a <div> with role="button" and aria-label containing "Play GIF" (the standard WhatsApp GIF UI)
    gif_btn = message.query_selector(
        "xpath=.//div[@role='button' and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'play gif')]"
    )
    if gif_btn and gif_btn.is_visible():
        return gif_btn
    return None


def is_animated_sticker(message: 'ElementHandle') -> 'ElementHandle':
    """
    Returns handle if an animated sticker is present in the message using XPath.

    :param message: Playwright ElementHandle representing a WhatsApp message element
    :return: ElementHandle of the sticker container if animated sticker exists, else None
    """
    xpath = (
        ".//div[@role='button' and contains(translate(@aria-label, "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sticker')]"
        "//img[contains(@src,'blob:')]/following-sibling::canvas"
    )
    animated_canvas = message.query_selector(f"xpath={xpath}")
    if animated_canvas and animated_canvas.is_visible():
        return animated_canvas
    return None


def is_plain_sticker(message: 'ElementHandle') -> 'ElementHandle':
    """
    Returns the handle if a static sticker image is present using XPath.
    Matches sticker buttons containing 'Sticker' in aria-label and a blob: image.
    """
    return message.query_selector(
        "xpath=.//button[img[contains(@src,'blob:')] and (@aria-label='Sticker with no label' or contains(@aria-label,'Sticker'))]"
    )


def is_lottie_animation_sticker(message: 'ElementHandle') -> 'ElementHandle':
    """
    Checks if a Lottie/SVG sticker animation is present in a WhatsApp Web message.
    Returns the <svg> element if found, else None.
    """
    # Limit search to sticker container area to avoid matching other small SVG icons
    xpath = (
        ".//div[@role='button' and "
        "contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'sticker')]"
        "//svg"
    )
    el = message.query_selector(f"xpath={xpath}")
    if el and el.is_visible():
        return el
    return None


def isSticker(message: 'ElementHandle') -> bool:
    """Returns True if any sticker type is detected using XPath."""
    return any([
        (el := is_animated_sticker(message)) and el.is_visible(),
        (el := is_lottie_animation_sticker(message)) and el.is_visible(),
        (el := is_plain_sticker(message)) and el.is_visible()
    ])


# -------------------- Quoted Message Utilities -------------------- #

def isQuotedText(message: 'ElementHandle') -> 'ElementHandle':
    """
    Checks if a message is quoting another and returns the quoted‑message button handle.
    Matches any div with a data-pre-plain-text attribute, then its button labeled "Quoted message".
    """
    return message.query_selector("div[data-pre-plain-text]").query_selector(
        "div[role='button'] >> span.quoted-mention")


def get_QuotedText_handle(message: 'ElementHandle') -> str:
    """Returns the handle for the quoted-mention span inside a quoted message."""
    return isQuotedText(message).is_visible() or ""


# -- System -- #

def startup_popup_locator(page: 'Page') -> 'Locator':
    """Returns the startup continue popup button locator."""
    return page.get_by_role("button", name=re.compile("continue", re.I))


def popup2(page: 'Page'):
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


def group_info(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('group info')")


def select_messages(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('select messages')")


def mute_notifications(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('mute notifications')")


def disappearing_messages(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('disappearing messages')")


def add_to_fav(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('add to favourites')")


def close_chat(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('close chat')")


def clear_chat(page: 'Page') -> 'ElementHandle':
    dialog = page.query_selector("div[role='dialog']")
    if not dialog:
        return None
    return dialog.query_selector("li:has-text('clear chat')")
