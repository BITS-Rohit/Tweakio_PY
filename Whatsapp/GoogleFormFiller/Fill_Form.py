"""Init for starting the google form here. Just call Start Filling"""
import os
import random
import re
from typing import Union

from bs4 import BeautifulSoup
from playwright.sync_api import Page, Locator, ElementHandle
from rich.console import Console
from rich.table import Table

from Whatsapp.GoogleFormFiller.SmartAI import AI
from Whatsapp.HumanAction import human_send

cur_dir = os.path.dirname(os.path.abspath(__file__))


def Start_Filling(url: str, page: Page) -> bool:
    """Start Filling Form """
    try:
        page.goto(url)
        page.wait_for_timeout(2500)
        print(f"Page is ready [{page.url}]")
        try:
            fill(page=page, ai=AI())
        except:
            return False
        return True

    except Exception as e:
        print(f"Error in Start Filling Form [{e}]")
        return False


def fill(page: Page, ai) -> None:
    """FIll"""
    context, feedback = "", []
    try:
        Items = fs.get_FormItems(page)
        if not Items:
            print("Items are None")
            return
        else:
            print("Items found")

        count = Items.count()
        print(f"Count : {count}")
        try:
            html = page.content()
            parser = BeautifulSoup(html, "html.parser")
            print("Got parser")

            body = parser.find("body")

            items = body.find("div", {"role": "list"})
            items.decompose()
            print("Removed items")

            res = ai.chat(user_input=f"Source Code HTML : {body}", mode="context")
            context = res["context"]
            print(f"Context : {context}")
        except Exception as e:
            print(f"Error in Fill Form // context [{e}]")

        email__box = fs.get_EmailCheckbox(page)
        if email__box.is_visible():
            email__box.click(timeout=1999)

        for i in range(0, count):
            print(f"Item no. [ {i} ]")
            item = Items.nth(i)
            getIntoView(element=item, page=page)

            choose = item.get_by_text(re.compile("choose", re.I), exact=True).first
            if choose.is_visible():
                print("Choose Clicked")
                choose.click()
                item = Items.nth(i)

            clear_selection = item.locator("span").filter(has_text=re.compile("clear selection", re.I)).first
            if clear_selection.is_visible():
                clear_selection.click(timeout=random.randint(1002, 1345))
                print("Clear Selection Clicked")

            text = item.inner_text()
            response = ai.chat(user_input=f"Source Code : {text}", mode="form_formatter")

            question = response["question"]
            answer = response["answer"]
            qtype = response["qtype"]
            reason = response["reason"]

            feedback.append({
                "qtype": qtype,
                "question": question,
                "answer": answer,
                "reason": reason
            })

            if qtype.lower() in ["date", "time"]:
                print("[Date | Time] -> will be patched soon")
            else:
                FallBackFill(page=page, response=response, element=item)

            alert = item.get_by_role("alert").last
            if alert.is_visible():
                print("Alert Seen [Re-checking answer]")

    except Exception as e:
        print(f"Error  in Fill [{e}]")

    print("++++++++++ Constructed Feedback ++++++++++")
    print_feedback(context=context, feedback=feedback)


def print_feedback(context, feedback):
    """ Rich FeedBack """
    console = Console()

    console.rule("[bold blue] Google Form Context [/bold blue]")
    console.print(context)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No.", width=5)
    table.add_column("QType", width=15)
    table.add_column("Question", style="bold")
    table.add_column("Answer", style="green")
    table.add_column("Reason", style="dim")

    for idx, entry in enumerate(feedback, start=1):
        table.add_row(
            str(idx),
            entry["qtype"],
            entry["question"],
            entry["answer"],
            entry["reason"],
        )

    console.rule("[bold green] Form Feedback [/bold green]")
    console.print(table)


def _click_(target: Locator, page: Page):
    target.scroll_into_view_if_needed(timeout=random.randint(1502, 1945))
    target.click(timeout=2000)
    page.wait_for_timeout(random.randint(1502, 1945))


def FillItem(page: Page, element: Locator, response: dict):
    """Fill Item in the form"""
    selectors = response["selector"].split("#")
    selectors = ["xpath=" + s.replace("xpath=", "") for s in selectors]

    qtype = response["qtype"].lower()
    answer = response["answer"]
    print(f"TYPE : {qtype}")

    try:
        if qtype in ["short_answer", "paragraph"]:
            target = element.locator(selectors[0]).first
            _click_(target, page)
            human_send(page=page, element=target, text=answer)

        elif qtype in ["multiple_choice", "linear_scale", "rating"]:
            _click_(element.locator(selectors[0]).first, page)

        elif qtype in ["checkbox", "multiple_choice_grid"]:
            for sel in selectors:
                _click_(element.locator(sel).first, page)

        elif qtype == "dropdown":
            ans = element.get_by_text(re.compile(answer, re.I), exact=True).last
            _click_(ans, page)

        elif qtype == "file_upload":
            File_Upload(element=element, page=page)

        else:
            print(f"⚠️ Unknown question type: {qtype}")

    except:
        FallBackFill(page=page, element=element, response=response)


def FallBackFill(page: Page, response: dict, element: Locator):
    """Fallback Filler for the form"""
    print("Fall Back initiated")
    answer = response["answer"]
    qtype = response["qtype"].lower()

    print(f"TYPE : {qtype}")
    print(f"Question : {response['question']}")
    print(f"Answer : {answer}")

    try:
        if qtype in ["short_answer", "paragraph"]:
            locator = element.locator("input[type=text]")
            if not locator or not locator.is_visible():
                locator = element.locator("textarea").first

            locator.click(timeout=2000)
            locator.fill(" ")
            human_send(page=page, element=element, text=answer)

        elif qtype in ["multiple_choice", "dropdown", "linear_scale", "rating"]:
            locator = element.get_by_text(answer, exact=True).last
            locator.click(timeout=2000)

        elif qtype == "multiple_choice_grid":
            for choices in answer.split("--"):
                row, col = choices.split("#")
                locator = element.get_by_role("radio", name=f"{row}, response for {col}").first
                if locator and locator.is_visible():
                    locator.click(timeout=2000)

        elif qtype == "checkbox":
            for x in answer.split("#"):
                locator = element.get_by_text(x, exact=True).last
                if locator.is_visible():
                    locator.click(timeout=2000)

        else:
            print("Default Fall Back reached")

        print("Success \n----------")

    except Exception as e:
        print(f"Error in Fall Back Fill: {e}")


def File_Upload(element: Locator, page: Page):
    """File Upload API function"""
    global cur_dir
    add_file = element.get_by_text(re.compile("add file", re.I), exact=True).last
    if not add_file or not add_file.is_visible():
        print("Add File not visible")
        return

    add_file.click(timeout=2000)

    Frame = page.frame_locator("iframe[src*='https://docs.google.com/picker']")
    if not Frame:
        print("No Frame")
        return

    cur_dir = os.path.join(cur_dir, "resume.pdf")
    Frame.locator("input[type='file']").set_input_files(cur_dir)


def getIntoView(element: Union[Locator, ElementHandle], page: Page, max_attempts: int = 45) -> None:
    """Makes the Element to come into view """
    try:
        print("Getting into view of the element")

        # Convert Locator → ElementHandle
        if isinstance(element, Locator):
            element: ElementHandle = element.element_handle(timeout=1000)

        if element is None:
            print("Error: Element handle could not be retrieved.")
            return

        box = element.bounding_box()
        attempts = 0

        if box is None:
            while attempts < max_attempts:
                box = element.bounding_box()

                if not at_end_of_page(page):
                    page.mouse.wheel(0, random.randint(119, 199))
                else:
                    break

                page.wait_for_timeout(random.randint(899, 1111))
                attempts += 1

        if box is None:
            print("Warning: Element not found after scrolling both directions.")

        element.scroll_into_view_if_needed(timeout=1000)

    except Exception as e:
        print(f"Error in getIntoView: {e}")


def at_end_of_page(page: Page) -> bool:
    """At the End of the Page"""
    return page.evaluate(
        "() => (window.scrollY + window.innerHeight) >= document.documentElement.scrollHeight"
    )
