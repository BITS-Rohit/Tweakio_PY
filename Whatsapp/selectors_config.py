"""
Helper functions to interact with various WhatsApp Web UI components using Playwright.

Conventions:
- `page`: refers to `playwright.sync_api.Page` instance.
- All other elements returned are of the type `Locator`.
- Utility functions are written to extract attributes or recognize content like images, videos, or quoted messages.
"""
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page, Locator


def chat_list(page: 'Page') -> 'Locator':
    """Returns the chat list grid locator on the main UI."""
    return page.get_by_role("grid", name=re.compile("chat list", re.I))


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
    return page.get_by_role("listitem").get_by_role("button")


def getChat_lowImg(chat: 'Locator') -> str:
    """Extracts the low-quality image (thumbnail) from a chat preview item."""
    if chat.locator("span[data-icon='default-group-refreshed']").is_visible() : return "Default group icon"
    if chat.locator("img").is_visible():
        return chat.locator("img").first.get_attribute("src")
    return ""


def getChatName(chat: 'Locator') -> str:
    """Returns the primary chat name (first span[title]) or empty string."""
    spans = chat.locator("span[title]")
    if spans.count() > 0:
        return spans.first.get_attribute("title") or ""
    return ""


def is_community(chat: 'Locator') -> str:
    """
    If this chat item has the 'default-community-refreshed' icon,
    return the community name (the span[title] without a data-icon).
    """
    icon = chat.locator("span[data-icon='default-community-refreshed']")
    if icon.is_visible():
        # pick the first title‐span that does NOT have a data-icon
        name_span = chat.locator("span[title]:not([data-icon])").first
        return name_span.get_attribute("title") or ""
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


def get_message_text(message: 'Locator') -> str:
    """Returns the text content of a message if visible."""
    if message.locator("span.selectable-text.copyable-text").first.is_visible():
        return message.locator("span.selectable-text.copyable-text").first.text_content()
    return ""


def is_message_out(message: 'Locator') -> bool:
    """Returns True if the message is outgoing (sent by bot)."""
    return message.locator(".message-out").is_visible()


def get_dataID(message: 'Locator') -> str:
    """Returns the unique data-id attribute of a message."""
    return message.get_attribute("data-id") or ""

# -------------------- Message Type Checkers -------------------- #

def isPic(message: 'Locator') -> 'Locator':
    """Checks if the message contains a picture via the open-picture button."""
    return message.get_by_role("button", name=re.compile("open picture", re.I))


def get_mess_pic_url(message: 'Locator') -> str:
    """Extracts the image URL from an incoming picture message if visible."""
    if message.locator("img").is_visible():
        return message.locator("img").get_attribute("src")
    return ""


def isVideo(message: 'Locator') -> 'Locator':
    """Checks if the message contains a playable video icon."""
    return message.locator("xpath=.//span[contains(@data-icon, 'media-play')]")

def isReacted(message : 'Locator') -> bool:
    """check is the message is reacted or not"""
    return message.get_by_role("button",name=re.compile("reaction.*👍",re.I))

def is_Voice_Message(message: 'Locator') -> 'Locator':
    """Checks if the message is a voice note."""
    return message.locator("xpath=.//span[contains(@aria-label,'voice message')]")


def is_gif(message: 'Locator') -> 'Locator':
    """Checks if the message contains a GIF play button."""
    return message.locator("xpath=.//div[@role='button' and contains(@aria-label, 'Play GIF')]")


def is_animated_sticker(message: 'Locator') -> 'Locator':
    """Returns locator if an animated sticker is present."""
    return message.locator("xpath=.//div[@role='button' and contains(@label, 'Sticker') and img[contains(@src, 'blob:')] and canvas]")


def is_plain_sticker(message: 'Locator') -> 'Locator':
    """Returns locator if a static sticker image is present."""
    return message.locator("xpath=.//div[@role='button' and contains(@label, 'Sticker')]/img[contains(@src, 'blob:')]")


def is_lottie_animation_sticker(message: 'Locator') -> 'Locator':
    """Checks if a lottie/svg sticker animation is present."""
    return message.locator("xpath=.//svg")


def isSticker(message: 'Locator') -> bool:
    """Returns True if any sticker type is detected."""
    return (
        is_animated_sticker(message).is_visible() or
        is_lottie_animation_sticker(message).is_visible() or
        is_plain_sticker(message).is_visible()
    )

# -------------------- Quoted Message Utilities -------------------- #

def isQuotedText(message: 'Locator') -> 'Locator':
    """
    Checks if a message is quoting another and returns the quoted‑message button locator.
    Matches any div with a data-pre-plain-text attribute, then its button labeled "Quoted message".
    """
    quote_container = message.locator("div[data-pre-plain-text]")
    return quote_container.get_by_role("button", name=re.compile("Quoted message", re.I))


def get_QuotedText(message: 'Locator') -> 'Locator':
    """Returns the locator for the quoted-mention span inside a quoted message."""
    return isQuotedText(message).locator("span.quoted-mention")

# -- System -- #

def startup_popup(page: 'Page') -> 'Locator':
    """Returns the startup continue popup button locator."""
    return page.get_by_role("button", name=re.compile("continue", re.I))


# ------ Read Handles ---- #
def unread():
    pass
