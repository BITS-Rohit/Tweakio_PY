"""Media Methods"""
import random
import time
from pathlib import Path

from playwright.sync_api import Page, Locator, FileChooser
from Whatsapp import HumanAction as ha
from Whatsapp import selectors_config as sc

# ----------------------------------------------------------------  #
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".3gp", ".mkv"}


def infer_media_type_from_file(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    return "doc"


def getMediaOptionLocator(page: Page, mediatype: str) -> Locator:
    """
    Returns the visible <li> or <button> you need to click
    to open the Photos & videos / Document / Audio chooser.
    """
    mt = mediatype.lower().strip()
    if mt in ("img", "image", "vid", "video"):
        return sc.photos_videos(page)
    if mt == "audio":
        return sc.audio(page)
    # fallback to document
    return sc.document(page)

def getMediaInputLocator(page: Page, mediatype: str) -> Locator:
    """
    Returns the hidden <input type=file> inside that menu item,
    for direct .set_input_files() injection.
    """
    return getMediaOptionLocator(page, mediatype).locator("input[type=file]")


def menu_icon_click(page: Page):
    try:
        menu_icon = sc.plus_rounded_icon(page=page)

        if not menu_icon:
            print("Menu Icon not found")
            return

        ha.move_mouse_to_locator(page, menu_icon)
        menu_icon.click(timeout=2000)
        time.sleep(random.uniform(1.0, 1.5))
    except Exception as e:
        print(f"Menu Icon not found : {e}")


def InjectMedia(page: Page, files: list[str], mediatype: str = "doc") -> None:
    """
    Add the Media to the message box but don't send. Just adds the Media.
    :param mediatype:  type of the file to add
    :param files: list of type str [give the list of the files path as str]
    :param page:page
    :return:None
    """

    menu_icon_click(page)
    media_input = getMediaInputLocator(page, mediatype)
    if not media_input:
        print(f"❌ Media type button not visible for: {mediatype}")
        return

    if not media_input:
        print(f"Media input for type [ {mediatype} ] not found")
        return

    media_input.set_input_files(files)


def AddMedia(page: Page, file: str, mediatype: str = "doc") -> None:
    """
    this adds an image to the message box , only images
    :param page:
    :param file:
    :param mediatype:
    :return:
    """
    try:
        menu_icon_click(page)

        target = getMediaOptionLocator(page, mediatype)

        if not target.is_visible():
            print(f"❌ Attach option for '{mediatype}' not visible.")
            return

        with page.expect_file_chooser() as fc:
            target.click(timeout=2000)
        chooser: FileChooser = fc.value

        p = Path(file)
        if not p.exists():
            print(f"❌ File not found: {file}")
            return
        chooser.set_files(str(p.resolve()))

        page.wait_for_timeout(600)
        page.keyboard.press("Enter")
        page.wait_for_timeout(300)
        page.keyboard.press("Enter")

        print(f"✅ Sent {mediatype}: {file}")

    except Exception as e:
        print(f"Error in AddMedia: {e}")


def sendMedia(page: Page, files: list[str], mediatype: str = "doc") -> None:
    try:
        InjectMedia(page=page, files=files, mediatype=mediatype)
        page.keyboard.press("Enter")
    except Exception as e:
        print(f"Error in Add Media : {e}")
        page.keyboard.press("Escape", delay=random.uniform(0.2, 0.5))
        page.keyboard.press("Escape", delay=random.uniform(0.1, 0.3))
