"""
Helper functions to interact with various WhatsApp Web UI components using Playwright.

Conventions:
- `page`: refers to `playwright.sync_api.Page` instance.
- All other elements returned are of the type `Locator`.
- Utility functions are written to extract attributes or recognize content like images, videos, or quoted messages.
"""

import re

from playwright.sync_api import Page, Locator


def chat_list(page: Page) -> Locator:
    """Returns the chat list grid locator on the main UI."""
    return page.get_by_role("grid", name=re.compile("chat list", re.I))


def total_chats(page: Page) -> int:
    """Returns the total number of chats visible in the chat list."""
    return int(chat_list(page).get_attribute("aria-rowcount"))


def chat_items(page: Page) -> Locator:
    """Returns a locator for all individual chat items (buttons) in the list."""
    return page.get_by_role("listitem").get_by_role("button")


def getChat_lowImg(chat: Locator) -> str:
    """Extracts the low-quality image (thumbnail) from a chat preview item."""
    return chat.locator("img").get_attribute("src")


def Profile_header(page: Page) -> Locator:
    """
    Returns the profile header button locator used to open contact details.

    Used when a chat is opened and the top bar includes profile/name/media access.
    """
    return page.locator("header").get_by_role("button", name=re.compile("profile details", re.I))

def qr_canvas(page : Page) -> Locator:
    return page.get_by_role("img", name=re.compile(r"scan.*qr", re.I))


# -------------------- Sidebar Navigation (Protected selectors) -------------------- #

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
    return page.locator('[role="row"][data-id]')


def get_dataID(message: Locator) -> str:
    """Returns the unique data-id attribute of a message."""
    return message.get_attribute("data-id")


# -------------------- Message Type Checkers -------------------- #

def isPic(message: Locator) -> Locator:
    """Checks if the message contains a picture. Returns the button that opens the image."""
    return message.get_by_role("button", name=re.compile("open picture", re.I))


def get_mess_pic(message: Locator) -> str:
    """
    Extracts the image URL from an incoming picture message.

    Note: This assumes that the picture message contains a visible <img> tag.
    """
    return message.locator("img").get_attribute("src")


def isVideo(message: Locator) -> Locator:
    """
    Checks if the message contains a video.

    Returns the button element that represents the video (playable media).
    """
    return message.locator("xpath=.//span[contains(@data-icon, 'media-play')]")


def is_Voice_Message(message: Locator) -> Locator:
    """"""
    return message.locator("xpath=.//span[contains(@aria-label,'voice message'")


def is_gif(message: Locator) -> Locator:
    """"""
    return message.locator("xpath=.//div[@role='button' and contains(@aria-label, 'Play GIF')]")


def is_animated_sticker(message: Locator) -> Locator:
    """
    expected to return if is animated sticker?
    """
    return message.locator("xpath=.//div[@role='button' and contains(@label, 'Sticker')and img[contains(@src, 'blob:')]and canvas]")


def is_plain_sticker(message : Locator) -> Locator :
    """expected to return is plain sticker?"""
    return message.locator("xpath=.//div[@role='button' and contains(@label, 'Sticker')]/img[contains(@src, 'blob:')]")

def is_lottie_animation_sticker(message : Locator) ->Locator:
    """ expected to return the lottie animation """
    return message.locator("xpath=.//svg")

def isSticker(message : Locator) -> Locator :
    return is_animated_sticker(message) or is_lottie_animation_sticker(message) or is_plain_sticker(message)

# -------------------- Quoted Message Utilities -------------------- #


def isQuotedText(message: Locator) -> Locator:
    """
    Checks if the message is quoting another message.
    Returns the quoted message button element if found.
    """
    return message.locator("xpath=.//div[contains(@data-pre-plain-text)]").get_by_role("button",name=re.compile("Quoted message",re.I))


def get_QuotedText(message: Locator) -> Locator:
    """
    Extracts the span text element inside the quoted message section.

    Useful when replying to a message, and you want to access the original referenced content.
    """
    return isQuotedText(message).locator("span.quoted-mention")
