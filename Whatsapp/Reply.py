import random

from playwright.sync_api import Page, Locator

from Whatsapp import selectors_config as sc, HumanAction as ha, Media as med


def double_edge_click(page: Page, locator: Locator, edge: str = "right") -> None:
    """
    double-clicks near the edge of the given message bubble (Locator).
    Args:
        page (Page): The Playwright Page object.
        locator (Locator): The message bubble element.
        edge (str): The edge to double-click near ("left" or "right").
    """
    try:
        ha.move_mouse_to_locator(page=page, locator=locator)
        box = locator.bounding_box()

        if not box or box["width"] == 0 or box["height"] == 0:
            print("Invalid bounding box.")
            return

        x = box["x"] + (box["width"] - 5 if edge == "right" else 5)
        y = box["y"] + box["height"] / 2

        page.mouse.click(x, y, click_count=2, delay=random.randint(301, 399))
    except Exception as e:
        print(f"Error in double edge click : \n {e}")


def reply(page: Page, locator: Locator, text: str) -> None:
    """
    This is a reply function to reply to the message
    :param page:
    :param locator:
    :param text:
    :return:
    """
    if reply_(page=page, locator=locator, text=text): page.keyboard.press("Enter")


def reply_(page: Page, locator: Locator, text: str, retry: int = 0) -> bool:
    """
    This is a reply function to reply to the message with enhanced core logic with retries without Pressing Enter
    :param page:
    :param locator:
    :param text:
    :param retry: 0
    :return:
    """
    try:
        double_edge_click(page=page, locator=locator, edge="left") if sc.is_message_out(
            message=locator) else double_edge_click(page=page, locator=locator, edge="right")

        inBox = sc.message_box(page)
        ha.move_mouse_to_locator(page, inBox)
        inBox.click()

        _typing(page=page, text=text)
        return True
    except Exception as e:
        if retry < 3: reply(page=page, locator=locator, text=text)
        print(f"Error in _reply : \n {e}")
    return False


def _typing(page: Page, text: str) -> None:
    """
    It types with new lines split on \n
    :param page:
    :param text:
    :return:
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        page.keyboard.type(line,delay=random.randint(601, 699))
        if i < len(lines) - 1:
            page.keyboard.press("Shift+Enter")


def reply_media(page: Page, message: Locator, text: str, file: list[str],
                mediatype: str = "doc",sendMedType: str="add") -> None:
    """
    It types first then add image then send .
    :param page:
    :param message:
    :param text:
    :param sendMedType:
    :param file:
    :param mediatype:
    :return:
    """
    success = reply_(page=page, locator=message, text=text)
    if success:
        if sendMedType == "inject":
            med.InjectMedia(page=page, files=file, mediatype=mediatype)
        else:
            med.AddMedia(page=page, file=file[0], mediatype=mediatype)
        # -- Send -- #
        page.wait_for_timeout(random.randint(1023, 1391))
        page.keyboard.press("Enter")
    else:
        page.keyboard.press("Escape", delay=random.randint(701, 893))
        page.keyboard.press("Escape", delay=random.randint(701, 893))


def reply_menu(page: Page, locator: Locator, text: str) -> None:
    """
    Pass the menu string in the text.
    :param page:
    :param locator:
    :param text:
    :return:
    """
    reply_media(page=page, message=locator, text=text, sendMedType="add", mediatype="image")
