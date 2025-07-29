import random

from playwright.sync_api import Page, Locator

from Whatsapp import selectors_config as sc, HumanAction as ha


def _double_edge_click(page: Page, locator: Locator, edge: str = "right") -> None:
    """
    double-clicks near the edge of the given message bubble (Locator).
    Args:
        page (Page): The Playwright Page object.
        locator (Locator): The message bubble element.
        edge (str): The edge to double-click near ("left" or "right").
    """
    try:
        ha.move_mouse_to_locator(page=page,locator=locator)
        box = locator.bounding_box()

        if not box or box["width"] == 0 or box["height"] == 0:
            print("Invalid bounding box.")
            return

        x = box["x"] + (box["width"] - 5 if edge == "right" else 5)
        y = box["y"] + box["height"] / 2

        page.mouse.click(x, y, click_count=2, delay=random.randint(301, 399))
    except Exception as e:
        print(f"Error in double edge click : \n {e}")


def reply(page: Page, locator: Locator, text: str, retry: int = 0) -> None:
    """
    This is a reply function to reply to the message with enhanced core logic with retries
    :param page:
    :param locator:
    :param text:
    :param retry: 0
    :return:
    """
    try:
        _double_edge_click(page=page, locator=locator, edge="left") if sc.is_message_out(
            message=locator) else _double_edge_click(page=page, locator=locator, edge="right")

        inBox = sc.message_box(page)
        if inBox is None: return

        ha.move_mouse_to_locator(page=page, locator=inBox)
        inBox.click()

        ha.human_send(page=page,locator=inBox,text=text)
        inBox.press("Enter")
    except Exception as e:
        if retry < 3 : reply(page=page, locator=locator, text=text, retry=retry + 1)
        print(f"Error in reply : \n {e}")

def reply_media():
    pass

def reply_menu() :
    pass
