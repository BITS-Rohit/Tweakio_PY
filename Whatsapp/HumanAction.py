import math
import random
import time

import pyperclip
from playwright.sync_api import Page, ElementHandle

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

    # Adjust duration based on distance (between 0.4 to 0.9 sec)
    base_speed = 800  # pixels per second
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

def Move_mouse_to_locator(page, locator):
    """Moves mouse to a random point inside the element handle's bounding box."""
    box = locator.bounding_box()
    if not box:
        raise Exception("Cannot get bounding box for element handle")

    target_point = _random_point_in_box(box)
    move_mouse_smooth(page, target_point["x"], target_point["y"])



def human_send(page: Page, element: ElementHandle, text: str):
    """
    Clicks into the input field and types the message.
    Handles multiline input using Shift+Enter for `\n`.
    Falls back to paste if the message is large.
    Works with ElementHandle instead of Locator.
    """
    element.click()
    time.sleep(0.1)

    try:
        lines = text.split("\n")

        # If short text with no newline, type normally
        if len(text) <= 50 and len(lines) == 1:
            page.keyboard.type(text, delay=random.randint(76, 98))
        else:
            for i, line in enumerate(lines):
                if len(line) > 100:
                    pyperclip.copy(line)
                    page.keyboard.press("Control+V")
                else:
                    page.keyboard.type(line, delay=random.randint(47, 98))

                if i < len(lines) - 1:
                    page.keyboard.press("Shift+Enter")

    except Exception as e:
        print(f"[Fallback Fill] Failed to send: {e}")
        try:
            element.fill(text)
            page.keyboard.press("Enter")
        except:
            page.keyboard.press("Escape", delay=0.5)
            page.keyboard.press("Escape", delay=0.5)
