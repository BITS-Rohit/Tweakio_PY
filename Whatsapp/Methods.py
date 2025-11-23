""" Custom Methods"""
import base64
import random
import re
import time
from typing import Union

from playwright.sync_api import Page, ElementHandle, Locator

from EXTRA_UTILS.youtube import YoutubeAPI
from Whatsapp.GoogleFormFiller.Fill_Form import Start_Filling
from Langchain_AI import run_AI, Agent_ai
from Whatsapp import (SETTINGS, Reply as rep, Menu as menu, Manual as guide, ___ as _, Extra as ex,
                      selectors_config as sc)
from Whatsapp.SETTINGS import POST_URL, GET_URL
from Whatsapp.selectors_config import isReacted

# ----------------
gemini = run_AI.Gemini()
gpt = Agent_ai.AgentAiClient(
    post_url=POST_URL,
    get_url_base=GET_URL,
)
yt = YoutubeAPI(API_KEY=SETTINGS.YOUTUBE_API_KEY)


# ----------------
def setq(page: Page, locator: ElementHandle, quant: str) -> None:
    """
    Updates the bot's quantifier setting to the given value.

    Args:
        page (Page): The Playwright page object.
        locator (ElementHandle): The element handle of the chat to reply to.
        quant (str): The new quantifier value to set.

    Behavior:
        Sets SETTINGS.QUANTIFIER to the new value and sends a confirmation message
        back to the user.
    """
    SETTINGS.QUANTIFIER = quant
    text = f"Quant Updated. Success!  Current Now : `{SETTINGS.QUANTIFIER}`"
    rep.reply(page=page, element=locator, text=text)


def setchat(page: Page, locator: ElementHandle, max_chat_num: str) -> None:
    """
    Updates the maximum number of chats the bot should fetch.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): The chat element to send confirmation to.
        max_chat_num (str): The new maximum chat number as string.

    Behavior:
        Converts the input to int and updates SETTINGS.MAX_CHAT. Sends
        success or failure feedback to the user.
    """
    try:
        SETTINGS.MAX_CHAT = int(max_chat_num)
        text = "Max Chat number updated. Success"
    except Exception as e:
        text = "Failed to set new max chat"
        print(f"{text} : \n {e}")
        text += " \n Try to give correct value number"
    rep.reply(page=page, element=locator, text=text)


def helper(page: Page, locator: ElementHandle) -> None:
    """
    Sends a menu/help message to the user listing available commands.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): The chat element to reply to.

    Behavior:
        Fetches the menu from `menu.menu()` and sends it to the chat.
    """
    rep.reply(page=page, element=locator, text=menu.menu())


def setgc(page: Page, locator: ElementHandle, gc_val: str) -> None:
    """
    Enables or disables the bot's global mode based on user input.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.
        gc_val (str): Value indicating on/off like "yes", "no", "on", "off".

    Behavior:
        Updates SETTINGS.GLOBAL_MODE to True/False based on input and
        sends feedback to the user. Accepts multiple synonymous commands.
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

    rep.reply(page=page, element=locator, text=response_text)


def manual(page: Page, locator: ElementHandle, f_name: str) -> None:
    """
    Sends the user a manual/guide for a specific bot command.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.
        f_name (str): Name of the function/command to show the guide for.

    Behavior:
        Fetches the guide information using `guide.get_Fun_Info` and sends
        it back to the chat.
    """
    text = f"Manual-----Guide-----for----{f_name} : \n " + guide.get_Fun_Info(f_name)
    rep.reply(page=page, element=locator, text=text)


def remove_admin(page: Page, locator: ElementHandle, num: str) -> None:
    """
    Removes a number from the admin list if present.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.
        num (str): Admin number to remove.

    Behavior:
        Checks if the number exists in _.admin_list, removes it, marks
        _.admin_change = True, and sends feedback to the user.
    """
    if num in _.admin_list:
        _.admin_list.remove(num)
        _.admin_change = True
        text = "`Removal of admin done.`"
    else:
        text = "`Given number was not in admin list`"
    rep.reply(page=page, element=locator, text=text)


def add_admin(page: Page, locator: ElementHandle, num: str) -> None:
    """
    Adds a new admin number to the admin list.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.
        num (str): Admin number to add.

    Behavior:
        Tries to convert the number to int, appends to _.admin_list, and
        sends confirmation or error message.
    """
    try:
        int(num)
        _.admin_list.append(num)
        rep.reply(page=page, element=locator, text="`Admin Added.`")
    except Exception as e:
        print(f"Error in num {e}")
        rep.reply(page=page, element=locator, text="`Failed. Retry with numbers given only.`")


def showlist(page: Page, locator: ElementHandle) -> None:
    """
    Displays the current admin list to the user.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.

    Behavior:
        Sends a formatted list of all admin numbers.
    """
    text = f"`Here is Admin List :` \n -- `{_.admin_list}` --"
    rep.reply(page=page, element=locator, text=text)


def banlist(page: Page, locator: ElementHandle) -> None:
    """
    Displays the current banned numbers list to the user.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.

    Behavior:
        Sends a formatted list of all banned numbers.
    """
    text = f"`Here is Ban List :` \n -- `{_.ban_list}` --"
    rep.reply(page=page, element=locator, text=text)


def showgc(page: Page, locator: ElementHandle) -> None:
    """
    Shows the current state of the global mode.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.

    Behavior:
        Sends either "On" or "Off" depending on SETTINGS.GLOBAL_MODE.
    """
    text = f"`Current Global Mode =>[ {'On' if SETTINGS.GLOBAL_MODE else 'Off'} ]`"
    rep.reply(page=page, element=locator, text=text)


def showq(page: Page, locator: ElementHandle) -> None:
    """
    Shows the currently active quantifier.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.

    Behavior:
        Sends the value of SETTINGS.QUANTIFIER to the chat.
    """
    text = f"`Active Quant => {SETTINGS.QUANTIFIER}`"
    rep.reply(page=page, element=locator, text=text)


def showchat(page: Page, locator: ElementHandle) -> None:
    """
    Shows the maximum number of chats currently configured.

    Args:
        page (Page): Playwright page object.
        locator (ElementHandle): Chat element to reply to.

    Behavior:
        Sends the value of SETTINGS.MAX_CHAT to the chat.
    """
    text = f"`Current Max chat : {SETTINGS.MAX_CHAT}`"
    rep.reply(page=page, element=locator, text=text)


# ---- Media Content--------------

def save_video(page: Page, chat: Union[ElementHandle, Locator], message: Union[ElementHandle, Locator],
               filename: str = None) -> None:
    """
    Saves a video from a WhatsApp message using ElementHandle.
    """
    if isinstance(chat, Locator): chat = chat.element_handle(timeout=1000)
    if isinstance(message, Locator): message = message.element_handle(timeout=1000)

    if filename is None:
        filename = ex.get_File_name(message=message, chat=chat)

    def get_vid_blob() -> str:
        """Helper function for save vide"""
        playmedia = message.query_selector("span[data-icon='media-play']")
        if not playmedia:
            print("Can't find play-media button.")
            return ""

        playmedia.hover()
        playmedia.click(timeout=random.randint(1801, 2001))

        try:
            page.wait_for_selector("video[src]", timeout=5000)
        except Exception as e:
            print(f"Video tag did not appear in time. {e}")
            return ""

        video_el = page.query_selector("video[src]")
        return video_el.get_attribute("src") if video_el else ""

    blob_url = get_vid_blob()
    if not blob_url:
        print("Error getting blob_url")
        rep.reply(page=page, element=message, text="❌ Cannot save video, internal error occurred")
        return

    # Fetch, decode, and save the video
    base64_data = page.evaluate("""
                                async (blobUrl) => {
                                    const res = await fetch(blobUrl);
                                    const blob = await res.blob();
                                    const arrayBuffer = await blob.arrayBuffer();
                                    const dataBytes = new Uint8Array(arrayBuffer);  // renamed
                                    let binary = '';
                                    for (let i = 0; i < dataBytes.length; i++) {
                                        binary += String.fromCharCode(dataBytes[i]);
                                    }
                                    return btoa(binary);
                                }
                                """, blob_url)

    with open(filename, "wb") as f:
        f.write(base64.b64decode(base64_data))

    print(f"✅ Video saved as {filename}")
    rep.reply(page=page, element=message, text=f"✅ Video saved as {filename}")


# ------------ Message Prettifiers----------------

def react(message: Union[ElementHandle, Locator], page: Page, tries: int = 0) -> None:
    """React on message"""
    if isinstance(message, Locator): message = message.element_handle(timeout=1001)
    try:
        attempts = 0
        while message.bounding_box() is None and attempts < 10:
            page.mouse.wheel(0, -random.randint(150, 250))
            page.wait_for_timeout(timeout=random.randint(991, 1001))
            attempts += 1

        if message.bounding_box() is None:
            return print("DOM is not attached to the page , Bounding box none // react") or None

        if not message:
            print("Message is None in react")
            return None

        if not message.is_visible():
            print("Message not visible in react")
            if tries < 1:
                time.sleep(0.5)
                return react(message, page, tries + 1)
            return None

        if isReacted(message):
            print("Already Reacted")
            return None

        message.hover(timeout=2000, force=True)
        emoji_picker_button = page.get_by_role("button", name=re.compile("react", re.I)).last

        try:
            if not emoji_picker_button:
                if tries < 1:
                    print("Retrying... React button not visible yet.")
                    time.sleep(0.5)
                    return react(message, page, tries + 1)
                else:
                    print("Max tries reached - couldn't find emoji button")
                    return None
            emoji_picker_button.click(timeout=2000)
        except Exception as e:
            print(f"emoji button not found [{e}]")

        page.wait_for_timeout(500)

        # ----- Click the designated emoji -----
        try:
            dialog = page.get_by_role("dialog")
            dialog.wait_for(timeout=3000)

            # Emoji locator (more stable than .last)
            emoji = dialog.locator("img[alt='👍']").nth(-1)

            # Wait until visible
            emoji.wait_for(state="visible", timeout=2000)

            # Scroll into view manually
            page.evaluate(
                "(el) => el.scrollIntoView({behavior: 'instant', block: 'center'})",
                emoji
            )

            # Try clicking twice (UI sometimes animates)
            for _ in range(2):
                try:
                    emoji.click(timeout=2000)
                except:
                    page.wait_for_timeout(200)  # small delay retry

            print("⚠️ Emoji visible but could not click.")

        except Exception as e:
            print(f"pass emoji %%%% {e}")

        time.sleep(random.uniform(1.0, 2.0))
        if sc.isReacted(message):
            print(f"Reacted to {sc.get_message_text(message)}")

    except Exception as e:
        if tries < 1:
            print(f"Retrying due to unexpected error: {e}")
            time.sleep(0.5)
            react(message=message, page=page, tries=tries + 1)
        else:
            print(f"Final failure in react(): {e}")


def detect(page: Page, message: ElementHandle) -> None:  # change to ElementHandle
    """Detect Incoming message type : [text , Image , Video]"""
    text = f"`Detected Message Type : {ex.get_mess_type(message)}`"
    rep.reply(page=page, element=message,
              text=text)  # rep.reply still accepts Locator; may need wrapping if fully ElementHandle


# ------------  ----------- AI ------------ ------------ #
def ai(page: Page, message: ElementHandle, ask: str) -> None:  # change to ElementHandle
    """Gets AI answer for the given ask string and replies via the page"""
    response = gpt.ask(ask)  # Agent AI
    rep.reply(page=page, element=message, text=response)  # rep.reply still accepts Locator


# -------- -------- -------- -------- -------- -------- -------- -------- -------- --------
def nlp(page: Page, message: ElementHandle, f_info: str) -> None:  # change to ElementHandle
    """ natural language-driven assessment command"""
    rep.reply(page=page, element=message, text=f_info)  # same note: rep.reply may need locator conversion
    pass


def SmartFormFill(message: ElementHandle) -> None:
    """ fills form for given message """
    from BrowserManager import getPage
    page = getPage()
    url = sc.get_message_text(message)
    Start_Filling(page=page, url=url)


def YoutubeAPISearch(message: ElementHandle, page: Page) -> None:
    """Sends Searched queries according to YouTube API & query. It has Limits"""
    searched = yt.search(sc.get_message_text(message))
    rep.reply(page=page, element=message, text=searched, copy_paste=True)


def YoutubeAPIAUDIO(message: ElementHandle, page: Page) -> None:
    """Sends Audio to the Designated Message"""
    link = sc.get_message_text(message)
    ytd = yt.download_audio(link=link)
    rep.reply_media(page=page, mediatype="audio", message=message, filePath=ytd)


def YT_DLP_Search(message: ElementHandle, page: Page) -> None:
    """Uses YT DLP to search for query, No Limit"""
    rep.reply(page=page, element=message, text=yt.ytdlp_search(query=sc.get_message_text(message)), copy_paste=True)
