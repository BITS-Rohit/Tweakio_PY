from typing import Union

from playwright.sync_api import Page, Locator, ElementHandle

from Whatsapp import Methods as helper, Reply as rep, pre_dir as pd

pool = [
    "showq",
    "setgc",
    "showgc",
    "setchat",
    "help",
    "manual",
    "showchat",
    "add",
    "remove",
    "setq",
    "showlist",
    "savevid",
    "banlist",
    "detect",
    "send",
    "inject",
    "ai",
    "audio",
    "menu",
    "fill",
    "yt.search",
    "yt.audio",
    "yt.dlp.s"
]


def Bot_Commands(page: Page, message: Union[Locator, ElementHandle], f_name: str, f_info: str,
                 chat: Union[ElementHandle, Locator]):
    """
    Bot Launch Commands
    :param page:
    :param message:
    :param f_name:
    :param f_info:
    :param chat:
    :return:
    """
    text = f"Unknown command: [{f_name}]"
    helper.react(message=message, page=page)

    if f_name not in pool:
        print(text)
        rep.reply(page=page, element=message, text=f"`{text}`" + f"`Re-try with right cmd in the pool.` \n `[{pool}]`")

    # ---- Methods Implementation --- #
    match f_name:
        case "showq":
            helper.showq(page=page, locator=message)
        case "setgc":
            helper.setgc(page=page, locator=message, gc_val=f_info)
        case "showgc":
            helper.showgc(page=page, locator=message)
        case "setchat":
            helper.setchat(page=page, locator=message, max_chat_num=f_info)
        case "help":
            helper.helper(page=page, locator=message)
        case "manual":
            helper.manual(page=page, locator=message, f_name=f_info)
        case "showchat":
            helper.showchat(page=page, locator=message)
        case "add":
            helper.add_admin(page=page, locator=message, num=f_info)
        case "remove":
            helper.remove_admin(page=page, locator=message, num=f_info)
        case 'setq':
            helper.setq(page=page, locator=message, quant=f_info)
        case 'showlist':
            helper.showlist(page=page, locator=message)
        case 'banlist':
            helper.banlist(page=page, locator=message)
        case 'saveVid':
            helper.save_video(page=page, message=message, chat=chat)
        case "detect":
            helper.detect(page=page, message=message)
        case "ai":
            helper.ai(page=page, message=message, ask=f_info)
        case "inject":
            text = "`--[Here is your file]--`"
            rep.reply_media(page=page, message=message, send_type="inject", filePath=[f"{pd.files}/test.mp4"],
                            text=text)  # MediaType : default : doc
        case "send":
            text = "`--[Here is your file]--`"
            rep.reply_media(page=page, mediatype="image", message=message, filePath=[f"{pd.files}/test.jpg"],
                            text=text)  # Send_type : default : add
        case "audio":
            rep.reply_media(page=page, mediatype="audio", message=message,
                            filePath=[f"{pd.files}/test.mp3"])  # Send_type : default : add
        case "menu":
            rep.reply_menu(page=page, message=message)
        case "fill":
            helper.SmartFormFill(message=message)
        case "yt.search":
            helper.YoutubeAPISearch(page=page, message=message)
        case "yt.audio":
            helper.YoutubeAPIAUDIO(page=page, message=message)
        case "yt.dlp.s":
            helper.YT_DLP_Search(page=page, message=message)

        case _:
            print(text)
