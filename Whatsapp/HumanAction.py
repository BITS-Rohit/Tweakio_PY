import time
import random
import pyperclip

from playwright.sync_api import Page,Locator

# Persistent mouse position
import random
import time
import math

current_mouse_position = {"x": 0, "y": 0}

def _random_point_in_box(box, margin_ratio=0.3):
    min_x = box["x"] + box["width"] * margin_ratio
    max_x = box["x"] + box["width"] * (1 - margin_ratio)
    min_y = box["y"] + box["height"] * margin_ratio
    max_y = box["y"] + box["height"] * (1 - margin_ratio)
    return {
        "x": random.uniform(min_x, max_x),
        "y": random.uniform(min_y, max_y)
    }

def _ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

def _distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def move_mouse_smooth(page, target_x, target_y, steps=50):
    global current_mouse_position

    start_x, start_y = current_mouse_position["x"], current_mouse_position["y"]
    distance = _distance(start_x, start_y, target_x, target_y)

    # Adjust duration based on distance (between 0.2 to 0.6 sec)
    base_speed = 800  # pixels per second (adjust as needed)
    duration = max(0.4, min(0.9, distance / base_speed))

    for i in range(1, steps + 1):
        t = _ease_in_out_quad(i / steps)
        intermediate_x = start_x + (target_x - start_x) * t
        intermediate_y = start_y + (target_y - start_y) * t

        # Add jitter in the middle of the movement
        if 0.3 < t < 0.7:
            jitter_x = random.uniform(-0.5, 0.5)
            jitter_y = random.uniform(-0.5, 0.5)
        else:
            jitter_x = jitter_y = 0

        page.mouse.move(intermediate_x + jitter_x, intermediate_y + jitter_y)
        time.sleep(duration / steps)

    # Final position exactly
    page.mouse.move(target_x, target_y)
    current_mouse_position = {"x": target_x, "y": target_y}

def move_mouse_to_locator(page, locator):
    box = locator.bounding_box()
    if not box:
        raise Exception("Cannot get bounding box for locator")

    target_point = _random_point_in_box(box)
    move_mouse_smooth(page, target_point["x"], target_point["y"])



def human_send(page: Page, locator: Locator, text: str):
    locator.click()
    time.sleep(0.1)  # small pre-type delay

    try:
        tag = locator.evaluate("el => el.tagName").lower()
        if tag not in ['input', 'textarea']:
            raise ValueError(f"Element is not input/textarea/select: <{tag}>")

        if len(text) <= 20:
            for char in text:
                delay = random.uniform(0.06, 0.15)
                page.keyboard.type(char, delay=delay)
                if random.random() < 0.02:
                    page.keyboard.press("Backspace")
                    time.sleep(delay)

        elif len(text) <= 50:
            chunk_size = max(5, len(text) // 4)
            chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
            for chunk in chunks:
                current_value = locator.input_value()
                locator.fill(current_value + chunk)
                time.sleep(random.uniform(0.05, 0.2))

        else:
            pyperclip.copy(text)
            page.keyboard.press("Control+V")
            time.sleep(0.15)
        page.keyboard.press("Enter")
    except Exception as e:
        try:
            locator.fill(text)
        except Exception as inner:
            print(f"[Fallback Fill Fail] {inner}")
        print(f"[Fallback Fill] Error in human_send: {e}")
        time.sleep(0.2)
        page.keyboard.press("Enter")
