import random
from typing import Union

from playwright.async_api import Locator
from playwright.sync_api import Page, ElementHandle

from Whatsapp import selectors_config as sc, HumanAction as ha, Media as med, Menu as menu, pre_dir as pwd


def double_edge_click(page: Page, message: Union[ElementHandle, Locator]) -> bool:
    """For Replying , To double-click on the message"""
    # print("In double edge click")
    try:
        if isinstance(message, Locator): message = message.element_handle()  # Make it just before the clicking
        attempts = 0
        while message.bounding_box() is None and attempts < 20:
            page.mouse.wheel(0, -random.randint(150, 250))
            page.wait_for_timeout(timeout=random.randint(768, 1302))
            attempts += 1
            print(f"Done scrolling : attempts : {attempts}")

        condition = sc.is_message_out(message)  # True = outgoing, False = incoming
        # print(f"Condition : {condition}")

        box = message.bounding_box()

        # Convert absolute coords -> element-relative
        rel_x = box["width"] * (0.2 if condition else 0.8)
        rel_y = box["height"] / 2

        page.mouse.move(rel_x, rel_y)
        message.click(
            position={"x": rel_x, "y": rel_y},
            click_count=2,
            delay=random.randint(38, 69),
            timeout=3000
        )

        # small pause to let UI react
        page.wait_for_timeout(timeout=500)
        return True

    except Exception as e:
        print(f"[double_edge_click] Error: {e}")
        print("out of double edge click")
        return False


def reply(page: Page, element: Union[ElementHandle,Locator], text: str, copy_paste : bool = False) -> None:
    """
    This is a reply function to reply to the message.

    Presses Enter after successful reply_.

    Args:
        page (Page): Playwright page object.
        element (ElementHandle): The message element to reply to.
        text (str): The message text to send.
        :param text:
        :param element:
        :param page:
        :param copy_paste:
    """
    success = _reply_(page=page, message=element, text=text, copy_paste=copy_paste)

    if success:
        page.keyboard.press("Enter")
    else:
        print("Reply Returned False, Can't Press Enter")


def _reply_(page: Page, message: Union[ElementHandle,Locator], text: str,copy_paste : bool = False,  retry: int = 0) -> bool:
    """
    Core reply function with retries, without pressing Enter automatically.

    Args:
        page (Page): Playwright page object.
        message (ElementHandle): The message element to reply to.
        text (str): The message text to type.
        retry (int): Number of retry attempts (default 0).

    Returns:
        bool: True if typing was successful, False otherwise.
    """
    try:
        double_edge_click(page=page, message=message)
        inBox = sc.message_box(page)
        inBox.click(timeout=3000)
        if copy_paste : ha.Copy_Paste(page=page, element=inBox.element_handle(timeout=1000), text=text)
        else : ha.human_send(page=page, element=inBox.element_handle(timeout=1000), text=text)
        return True
    except Exception as e:
        if retry < 1:
            return _reply_(page=page, message=message, text=text, retry=retry + 1)
        print(f"Error in _reply : \n {e}")
    return False


def reply_media(page: Page, message: ElementHandle, filePath: list[str],text: str = "",
                mediatype: str = "doc", send_type: str = "add") -> None:
    """
    Sends a reply with optional media attachment.

    First types the message, then attaches the media (image, document, etc.) and presses Enter.

    Args:
        page (Page): Playwright page object.
        message (ElementHandle): The message element to reply to.
        text (str): Text to type before sending media.
        filePath (list[str]): List of file paths to attach.
        mediatype (str): Type of media ('doc', 'image', etc.)
        send_type (str): 'add' to attach normally, 'inject' to use InjectMedia.
    """
    success = _reply_(page=page, message=message, text=text)
    if success:
        if send_type == "inject":
            med.InjectMedia(page=page, files=filePath, mediatype=mediatype)
        else:
            med.AddMedia(page=page, file=filePath[0], mediatype=mediatype)
        page.wait_for_timeout(random.randint(1123, 1491))
        page.keyboard.press("Enter")
    else:
        page.keyboard.press("Escape", delay=random.randint(701, 893))
        page.keyboard.press("Escape", delay=random.randint(701, 893))


def reply_menu(page: Page, message: Union[ElementHandle, Locator], file: str = f"{pwd.rootDir}/files/img.png") -> None:
    """
    Reply the menu with image to the message.

    Args:
        page (Page): Playwright page object.
        message (ElementHandle): The message element to reply to.
        file (str): File path for the menu image (default provided).
    """
    reply_media(page=page, message=message, text=menu.menu(), mediatype="image", filePath=[file])
