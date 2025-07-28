from playwright.sync_api import Page, Locator

from Whatsapp import Methods as helper


def post_process(page: Page, message: Locator, f_name: str, f_info: str):
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
            helper.setq(page=page,locator=message,quant=f_info)
        case _:
            print(f"Unknown command: {f_name}")
