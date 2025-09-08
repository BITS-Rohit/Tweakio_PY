import time

import requests


# post https://api.agent.ai/v1/agent/fynl6w5du8d7mz1z/webhook/134441ad/async
# get https://api.agent.ai/v1/agent/fynl6w5du8d7mz1z/webhook/134441ad/status/<run_id>

class AgentAiClient:
    def __init__(self, post_url: str, get_url_base: str, input_key: str = "user_input", output_key: str = "response"):
        self.post_url = post_url
        self.get_url_base = get_url_base.replace("/<run_id>", "")
        self.input_key = input_key
        self.output_key = output_key

    async def ask(self, query: str, poll_interval: float = 1.0) -> str:
        resp = requests.post(
            self.post_url,
            headers={"Content-Type": "application/json"},
            json={self.input_key: query},
        )
        resp.raise_for_status()
        run_id = resp.json().get("run_id")

        while True:
            status_resp = requests.get(f"{self.get_url_base}/{run_id}")
            status_resp.raise_for_status()
            print("Status:", status_resp.status_code)
            print("Raw:", status_resp.text)

            data = status_resp.json()
            if self.output_key in data:
                return data[self.output_key]
            time.sleep(poll_interval)


async def main():
    ai = AgentAiClient(
        post_url="https://api.agent.ai/v1/agent/fynl6w5du8d7mz1z/webhook/134441ad/async",
        get_url_base="https://api.agent.ai/v1/agent/fynl6w5du8d7mz1z/webhook/134441ad/status/<run_id>",
        input_key="user_input",
        output_key="response"
    )
    resp = await ai.ask("Hello, how are you?")
    print(resp)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
