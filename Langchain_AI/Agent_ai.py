import time
import json
import os
from typing import Any

import requests
from datetime import datetime

class AgentAiClient:
    def __init__(self, post_url: str, get_url_base: str, input_key: str = "user_input", output_key: str = "response"):
        self.post_url = post_url
        self.get_url_base = get_url_base.replace("/<run_id>", "")
        self.input_key = input_key
        self.output_key = output_key

        # ----------- History Directory Setup -----------
        self.history_dir = "History"
        os.makedirs(self.history_dir, exist_ok=True)

        self.history_file = os.path.join(self.history_dir, "agent_ai.json")

        # Ensure file exists
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------
    # Load past JSON conversation
    # ---------------------------------------------------------
    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    # ---------------------------------------------------------
    # Save a message to history
    # ---------------------------------------------------------
    def save_history(self, user_text: str, ai_text: str):
        history = self.load_history()
        history.append({
            "user": user_text,
            "ai": ai_text,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------
    # Build memory prompt from JSON history
    # ---------------------------------------------------------
    def build_memory_prompt(self, query : str)->  str :
        history = self.load_history()
        conv = ""
        for h in history:
            conv += f"User: {h['user']}\nAI: {h['ai']}\n"

        conv = ("The following is a conversation between a human and an AI assistant.\n"
        + conv+
        f"User: {query}\nAI:")
        return conv

    # ---------------------------------------------------------
    # MAIN ASK FUNCTION (Sync)
    # ---------------------------------------------------------
    def ask(self, query: str, poll_interval: float = 1.0) -> Any | None:
        final_prompt = self.build_memory_prompt(query)

        # --------- STEP 1: POST query ---------
        resp = requests.post(
            self.post_url,
            headers={"Content-Type": "application/json"},
            json={self.input_key: final_prompt},
        )
        resp.raise_for_status()

        run_id = resp.json().get("run_id")
        if not run_id:
            raise ValueError("No run_id returned!")

        # print(f"[INFO] Started run: {run_id}")

        # --------- STEP 2: Poll until done ---------
        while True:
            url = f"{self.get_url_base}/{run_id}"
            status_resp = requests.get(url)
            status_resp.raise_for_status()

            if status_resp.status_code == 204 or not status_resp.text.strip():
                print("Still Processing Agent AI...")
                time.sleep(poll_interval)
                continue

            try:
                data = status_resp.json()
            except Exception:
                print("JSON error:", status_resp.text)
                time.sleep(poll_interval)
                continue

            if self.output_key in data:
                ai_reply = data[self.output_key]
                # save to JSON
                self.save_history(query, ai_reply)
                return ai_reply

            time.sleep(poll_interval)

# from AgentAiClient import AgentAiClient
# from Whatsapp.SETTINGS import POST_URL, GET_URL

# ai = AgentAiClient(
#     post_url=POST_URL,
#     get_url_base=GET_URL,
# )

# while True:
#     uin = input("ask GPT: ")
#     if uin == "q": break
#     reply = ai.ask(uin)
#     print("AI:", reply)
#
