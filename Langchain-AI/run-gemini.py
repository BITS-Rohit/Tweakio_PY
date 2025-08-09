import os
import warnings
import asyncio
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from Whatsapp import SETTINGS

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

memory_prompt = """
You are a helpful, humorous, persona-less assistant with Name Alto. You should adapt your tone to the user's context:
- If a user speaks like a teacher, respond helpfully and respectfully (as if the user were a student).
- If a user speaks casually, be friendly and concise.
- You may use light humor, but never claim to be a real person or a specific company.
IMPORTANT: You must refuse or safely redirect requests that are illegal, harmful, or violate safety/ethical norms (including violent wrongdoing, facilitating illegal activity, or sexual content involving minors). Always follow the platform's safety rules and applicable laws.
When possible, give step-by-step actionable instructions for automation tasks (Playwright or shell snippets), but never execute anything outside the user's explicit consent. 
"""

class Gemini:
    def __init__(self):
        self.api = SETTINGS.GEM_API_KEY
        if not self.api:
            raise Exception("GOOGLE_API_KEY environment variable not set")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=self.api,
            temperature=0.7,
            max_retries=2,
            name="Google Personal Pro",
            timeout=5
        )

        self.memory = ConversationSummaryBufferMemory(
            max_token_limit=2000,
            input_key="user_input",
            output_key="user_output",
            llm=self.llm,
            return_messages=True
        )

        self.base = "history"
        os.makedirs(self.base, exist_ok=True)

        self.memory.chat_memory.add_message(SystemMessage(content=memory_prompt))

        def get_history(session_id: str):
            path = os.path.join(self.base, f"{session_id}.json")
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write("[]")
            return FileChatMessageHistory(file_path=path, ensure_ascii=False, encoding="utf-8")

        def load_to_memory(session_id: str):
            for msg in get_history(session_id).messages:
                if isinstance(msg, HumanMessage):
                    self.memory.chat_memory.add_user_message(msg)
                elif isinstance(msg, AIMessage):
                    self.memory.chat_memory.add_ai_message(msg)

        load_to_memory("Google")

        async def chaining(inputs: dict):
            query = inputs.get(self.memory.input_key)
            if isinstance(query, HumanMessage):
                query = query.content
            elif not isinstance(query, str):
                query = str(query)

            self.memory.chat_memory.add_message(HumanMessage(content=query))
            response = await self.llm.ainvoke(self.memory.chat_memory.messages)

            asyncio.create_task(
                self._save_context_async(query, response.content)
            )

            return {self.memory.output_key: response.content}

        self.chain = RunnableLambda(chaining)

        self.convo = RunnableWithMessageHistory(
            self.chain,
            get_session_history=get_history,
            input_messages_key=self.memory.input_key,
            output_messages_key=self.memory.output_key,
        )

    async def _save_context_async(self, query, output):
        await asyncio.to_thread(
            self.memory.save_context,
            {self.memory.input_key: query},
            {self.memory.output_key: output}
        )

    async def chat(self, user_input: str, session_id: str = "Google") -> str:
        out = await self.convo.ainvoke(
            {self.memory.input_key: user_input},
            config={"configurable": {"session_id": session_id}},
        )
        return out.get(self.memory.output_key, "")


async def main():
    gemini = Gemini()
    while True:
        user_input = input("\nEnter your input: ")
        reply = await gemini.chat(user_input)
        print(f"AI: {reply}")


if __name__ == "__main__":
    asyncio.run(main())
