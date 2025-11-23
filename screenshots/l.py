import random
import re
from playwright.sync_api import sync_playwright, Page

def RandomName() -> str:
    s = []
    for i in range(10):
        s.append(chr(random.randint(65, 90)))
    return "".join(s)

def login_loop(page: Page):
    first_n = page.locator("input[id='firstName']")
    first_n.hover(timeout=5000)
    first_n.click(timeout=5000)
    first_n.fill(RandomName())

    last_n = page.locator("input[id='lastName']")
    last_n.hover(timeout=5000)
    last_n.click(timeout=5000)
    last_n.fill(RandomName())

    dateOfBirth = page.get_by_label(re.compile("date*of*birth", re.I))
    dateOfBirth.hover(timeout=5000)
    dateOfBirth.click(timeout=5000)
    for i in "342004":
        page.keyboard.press(i)

    gender = page.locator("select[id='gender']")
    gender.click(timeout=5000)
    gender.locator(re.compile("male")).click(timeout=5000)

    email = page.locator("input[id='email']")
    email.fill("I_am_autonomous@Anonymous.com")

    phone = page.locator("input[id='phone']")
    phone.fill("1234567890")

    photo = page.get_by_label(re.compile("profile*photo", re.I))
    with page.expect_file_chooser() as fc:
        photo.click(timeout=5000)
    photo.set_input_files('r.pdf')

    idp = page.get_by_label(re.compile("id*proof", re.I))
    with page.expect_file_chooser() as fc:
        idp.click(timeout=5000)
    idp.set_input_files('r.pdf')

    button = page.locator("button").filter(has_text=re.compile("next: doter details")).last
    button.click(timeout=5000)

# Use sync_playwright() to launch the browser
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)  # Set headless=False if you want to see the browser
    context = browser.new_context()
    page = context.new_page()

    # Go to the target URL
    page.goto("https://68db55eb8d4d33d47ee3977e--e-janmat.netlify.app/voter-register")

    # Call the login loop function
    login_loop(page)

    # Close the browser after the task is complete
    browser.close()
