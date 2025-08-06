import base64
import random
import re
import time

from playwright.sync_api import Page, Locator

from Whatsapp import (SETTINGS, Reply as rep, Menu as menu, Manual as guide, ___ as _, Extra as ex,
                      HumanAction as ha, selectors_config as sc)
from Whatsapp.selectors_config import isReacted


def setq(page: Page, locator: Locator, quant: str) -> None:
    """
    set the quantifier to new given q and sends feedback to the user
    :param page:
    :param locator:
    :param quant:
    :return:
    """
    SETTINGS.QUANTIFIER = quant
    text = f"Quant Updated. Success!  Current Now : `{SETTINGS.QUANTIFIER}`"
    rep.reply(page=page, locator=locator, text=text)


def setchat(page: Page, locator: Locator, max_chat_num: str) -> None:
    """
    set the given number to be new max chat to be fetched and send feedback to the user
    :param page:
    :param locator:
    :param max_chat_num:
    :return:
    """
    try:
        SETTINGS.MAX_CHAT = int(max_chat_num)
        text = "Max Chat number updated. Success"
    except Exception as e:
        text = "Failed  to  set new max chat"
        print(f"{text} : \n {e}")
        text += " \n Try  to give correct value number"
    rep.reply(page=page, locator=locator, text=text)


def helper(page: Page, locator: Locator) -> None:
    """
    reply with a menu to the user
    :param page:
    :param locator:
    :return:
    """
    rep.reply(page=page, locator=locator, text=menu.menu())


def setgc(page: Page, locator: Locator, gc_val: str) -> None:
    """
    Set the Global Mode of the bot and give feedback to the user
    :param page:
    :param locator:
    :param gc_val:
    :return:
    """
    starter = ["yes", "on", "active", "start", "open", "true"]
    closer = ["no", "off", "inactive", "stop", "close", "false"]

    lower_text = gc_val.lower().strip()

    if lower_text in starter:
        SETTINGS.GLOBAL_MODE = True
        response_text = "`Turned on Global Mode`"

    elif lower_text in closer:
        SETTINGS.GLOBAL_MODE = False
        response_text = "`Turned off Global Mode`"

    else:
        response_text = (
            "Incorrect command name.\n"
            "Accepted command names:\n"
            f"--start : {starter}\n"
            f"--close : {closer}"
        )

    rep.reply(page=page, locator=locator, text=response_text)


def manual(page: Page, locator: Locator, f_name: str) -> None:
    """
    return the information about bot commands to the user
    :param f_name:
    :param page:
    :param locator:
    :return:
    """
    text = f"Manual-----Guide-----for----{f_name} : \n " + guide.get_Fun_Info(f_name)
    rep.reply(page=page, locator=locator, text=text)


def remove_admin(page: Page, locator: Locator, num: str) -> None:
    """
    Removes the admin number from an admin list
    :param locator:
    :param page:
    :param num: number in str
    :return:
    """
    if num in _.admin_list:
        _.admin_list.remove(num)
        _.admin_change = True # mark for the admin change
        text = "`Removal of admin done.`"
    else:
        text = "`Given number was not in admin list`"
    rep.reply(page=page, locator=locator, text=text)


def add_admin(page: Page, locator: Locator, num: str) -> None:
    """Add the admin"""
    try:
        int(num)
        _.admin_list.append(num)
        rep.reply(page=page, locator=locator, text="`Admin Added.`")
    except Exception as e:
        print(f"Error in num {e}")
        rep.reply(page=page, locator=locator, text="`Failed. Retry with numbers given only.`")


# --- Show commands -----
def showlist(page: Page, locator: Locator) -> None:
    """Prints the Admin list to the user"""
    text = f"`Here is Admin List :` \n -- `{_.admin_list}` --"
    rep.reply(page=page, locator=locator, text=text)


def banlist(page: Page, locator: Locator) -> None:
    text = f"`Here is Ban List :` \n -- `{_.ban_list}` --"
    rep.reply(page=page, locator=locator, text=text)


def showgc(page: Page, locator: Locator) -> None:
    """
    Show the current Global Mode to the user
    :param page:
    :param locator:
    :return:
    """
    text = f"Current Global Mode :`{'On ' if SETTINGS.GLOBAL_MODE else 'Off'}`"
    rep.reply(page=page, locator=locator, text=text)


def showq(page: Page, locator: Locator) -> None:
    text = f"`Active Quant : {SETTINGS.QUANTIFIER}`"
    rep.reply(page=page, locator=locator, text=text)


def showchat(page: Page, locator: Locator) -> None:
    """
    show current amount of max chat currently to the user
    :param page:
    :param locator:
    :return:
    """
    text = f"`Current Max chat : {SETTINGS.MAX_CHAT}`"
    rep.reply(page=page, locator=locator, text=text)


# ---- Media Content--------------

def save_video(page: Page, chat: Locator, message: Locator, filename: str = None) -> None:
    """
    It saves the video of the message with filename, else use internal filename generation
    can extract blob_url, decode, fetch data, write itself
    :param page:
    :param chat:
    :param message:
    :param filename: default -> getfilename
    :return:
    """
    if filename is None: filename = ex.get_File_name(message=message, chat=chat)

    def get_VidBlob() -> str:
        playmedia = message.locator("span[data-icon='media-play']")

        if not playmedia.is_visible() or playmedia.count() == 0:
            print("Can't find play-media button.")
            return ""

        playmedia.hover()
        playmedia.click()

        try:
            page.wait_for_selector("video[src]", timeout=5000)
        except Exception as e:
            print(f"Video tag did not appear in time. {e}")
            return ""
        return page.locator("video[src]").get_attribute("src") or ""

    blob_url = get_VidBlob()
    if not blob_url:
        print("Error getting blob_url $$$$$$$$$$$$$$$$")
        rep.reply(page=page, locator=message, text="Cant save video , Internal Error occurred")
        return

    base64_data = page.evaluate(f"""
            async (blobUrl) => {{
                const res = await fetch(blobUrl);
                const blob = await res.blob();
                const arrayBuffer = await blob.arrayBuffer();
                const uint8Array = new Uint8Array(arrayBuffer);
                let binary = '';
                for (let i = 0; i < uint8Array.length; i++) {{
                    binary += String.fromCharCode(uint8Array[i]);
                }}
                return btoa(binary);
            }}
        """, blob_url)

    # Decode & save the video file
    with open(filename, "wb") as f:
        f.write(base64.b64decode(base64_data))
    print(f"✅ Video saved as {filename}")
    rep.reply(page=page, locator=message, text=f"✅ Video saved as {filename}")


# ------------ Message Prettifiers----------------

def react(message: Locator, page: Page, tries: int = 0) -> None:
    try:
        if isReacted(message):
            print("Already Reacted")
            return None
        message.wait_for(state="visible", timeout=5_000)
        message.hover(timeout=5_000)
        try:
            message.scroll_into_view_if_needed(timeout=2000)
        except:
            pass  # In case hover doesn't bring it into view

        emoji_btn = message.get_by_role("button", name=re.compile("react", re.I)).nth(0)

        try:
            emoji_btn.wait_for(state="visible", timeout=2_000)
        except Exception as e:
            if tries < 2:
                print("Retrying... React button not visible yet.")
                return react(message, page, tries + 1)
            else:
                print("Max tries reached - couldn't find emoji button")
                print(e)

        ha.move_mouse_to_locator(page=page, locator=emoji_btn)
        emoji_btn.click()

        try:
            dialog = page.get_by_role("dialog")
            dialog.wait_for(timeout=2_000)
            first_emoji = dialog.get_by_role("button").first
            first_emoji.wait_for(state="visible", timeout=2000)
            first_emoji.click()
        except Exception as e:
            print(f"Emoji dialog or button click failed: {e}")

        time.sleep(random.uniform(1.0, 2.0))

        if sc.isReacted(message):
            print(f"Reacted to {sc.get_message_text(message)}")
        else:
            print("Reaction failed (possibly clicked but not registered)")

    except Exception as e:
        if tries < 2:
            print("Retrying due to unexpected error...")
            react(message=message, page=page, tries=tries + 1)
        else:
            print(f"Final failure in react(): {e}")

def detect(message:Locator, page: Page) -> None:
    text = f"`Detected Message Type : {ex.get_mess_type(message)}`"
    rep.reply(page=page, locator=message, text=text)


# -------- -------- -------- -------- -------- -------- -------- -------- -------- --------
def nlp(page: Page, locator: Locator, f_info: str) -> None:
    """ natural language-driven assessment command"""

    # Still Under development
    rep.reply(page=page, locator=locator, text=f_info)
    pass
