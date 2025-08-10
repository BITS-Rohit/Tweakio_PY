import random
import time

from playwright.sync_api import Page, Locator

from Whatsapp import selectors_config as sc, HumanAction as ha, Media as med, Menu as menu


def double_edge_click(
        page: Page,
        locator: Locator,
        edge: str = "right",
        wait_timeout: int = 2000,  # ms to wait for element visible/attached
        verify_data_id: bool = True,  # re-check data-id just before click
) -> bool:
    """
    Safely double-clicks near the left/right edge of the given message bubble.
    Returns True on success, False on skip/failure.
    """
    before_id = None
    try:
        # 1) Wait a short time for it to be attached/visible
        try:
            locator.wait_for(state="visible", timeout=wait_timeout)
        except TimeoutError:
            print(f"double_edge_click: locator not visible after {wait_timeout}ms")
            return False

        # 2) Scroll into view so bounding_box is accurate
        try:
            locator.scroll_into_view_if_needed(timeout=wait_timeout)
        except Exception:
            pass  # not fatal

        # 3) Optionally capture data-id before computing box
        if verify_data_id:
            try:
                before_id = locator.get_attribute("data-id")
            except Exception:
                before_id = None

        # 4) Compute bounding box (retry once if None)
        box = locator.bounding_box()
        if not box:
            time.sleep(0.05)
            box = locator.bounding_box()
            if not box:
                print("double_edge_click: bounding_box not available")
                return False

        if box.get("width", 0) == 0 or box.get("height", 0) == 0:
            print("double_edge_click: invalid bounding box size")
            return False

        # 5) Compute coordinates near chosen edge
        x = box["x"] + (box["width"] - 6 if edge == "right" else 6)
        y = box["y"] + box["height"] / 2

        # 6) Re-verify data-id just before click
        if verify_data_id and before_id is not None:
            try:
                now_id = locator.get_attribute("data-id")
            except Exception:
                now_id = None
            if now_id != before_id:
                print(f"double_edge_click: data-id changed ({before_id} -> {now_id}), skipping click")
                return False

        # 7) Perform atomic double-click at computed coords
        page.mouse.click(x, y, click_count=2, delay=random.randint(40, 80))

        # small pause to let UI react
        time.sleep(0.06)
        return True

    except Exception as e:
        print(f"Error in double_edge_click : {e}")
        return False


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
        # double_edge_click(page=page, locator=locator, edge="left") if sc.is_message_out(
        #     message=locator) else double_edge_click(page=page, locator=locator, edge="right")
        locator.scroll_into_view_if_needed(timeout=2500)
        locator.click(click_count=3)

        inBox = sc.message_box(page)
        ha.move_mouse_to_locator(page, inBox)
        inBox.click()

        ha.human_send(page=page, locator=locator, text=text)
        return True
    except Exception as e:
        if retry < 3: reply(page=page, locator=locator, text=text)
        print(f"Error in _reply : \n {e}")
    return False


def reply_media(page: Page, message: Locator, text: str, file: list[str],
                mediatype: str = "doc", send_type: str = "add") -> None:
    """
    It types first then add image then send .
    :param page:
    :param message:
    :param text:
    :param send_type:
    :param file:
    :param mediatype:
    :return:
    """
    success = reply_(page=page, locator=message, text=text)
    if success:
        if send_type == "inject":
            med.InjectMedia(page=page, files=file, mediatype=mediatype)
        else:
            med.AddMedia(page=page, file=file[0], mediatype=mediatype)
        # -- Send -- #
        page.wait_for_timeout(random.randint(1123, 1491))
        page.keyboard.press("Enter")
    else:
        page.keyboard.press("Escape", delay=random.randint(701, 893))
        page.keyboard.press("Escape", delay=random.randint(701, 893))


def reply_menu(page: Page, locator: Locator,file : str ) -> None:
    """
    Reply the menu with image to the message
    :param file:
    :param page:
    :param locator:
    :return:
    """
    reply_media(page=page, message=locator, text=menu.menu()
                , send_type="add", mediatype="image",file=file)
