"""Smart AI for Google Form Filler only"""
import os
from pathlib import Path

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

import Whatsapp.SETTINGS as settings

cur_dir = os.path.dirname(os.path.abspath(__file__))
from Whatsapp.GoogleFormFiller.Prompt import prompts


# ===================================================
#   Pydantic Models
# ===================================================

class QAResponse(BaseModel):
    question: str = Field(description="Exact question from source block")
    qtype: str = Field(description="short_answer, paragraph, checkbox, etc.")
    answer: str = Field(description="Answer in required format")
    selector: str = Field(description="xpath= selector")
    reason: str = Field(description="Reason for answer")
    selector_reason: str = Field(description="Reason for selector")


class Context(BaseModel):
    context: str = Field(description="Full structured context block")


# ===================================================
#   Gemini (GOOGLE) LLM ONLY
# ===================================================

def getLLM(streaming: bool = False):
    """Call LLM"""
    if not settings.GEM_API_KEY:
        raise Exception("GEM_API_KEY missing. Gemini required.")

    common_kwargs = dict(
        temperature=0.5,
        max_retries=2,
        timeout=5,
    )

    if streaming:
        return ChatGoogleGenerativeAI(
            api_key=settings.GEM_API_KEY,
            model="gemini-2.5-flash",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            **common_kwargs,
        )

    return ChatGoogleGenerativeAI(
        api_key=settings.GEM_API_KEY,
        model="gemini-2.5-flash",
        **common_kwargs,
    )


# ===================================================
#   AI Assistant Class (SYNC)
# ===================================================

class AI:
    """Smart AI , Tuned for specific purpose"""

    def __init__(self, default_mode: str = "form_formatter") -> None:
        self.llm = None
        self.history = None
        self.path = None
        self.default_mode = default_mode

        self.form_parser = JsonOutputParser(pydantic_object=QAResponse)
        self.context_parser = JsonOutputParser(pydantic_object=Context)

    # ---------------------------------------------------
    #   INIT (SYNC)
    # ---------------------------------------------------
    def init(self, streaming: bool = False):
        """Initialize AI"""
        try:
            # Always use Gemini
            self.llm = getLLM(streaming=streaming)

            name = "GOOGLE"
            self.path = Path(f"{cur_dir}/{'AI_LOGS'}/{name}.json")
            self.path.mkdir(parents=True, exist_ok=True)
            self.path.touch()

            if self.path.stat().st_size == 0:
                self.path.write_text("[]", encoding="utf-8")

            self.history = FileChatMessageHistory(str(self.path))

        except Exception as e:
            print(f"Error in AI.init: {e}")

    # ---------------------------------------------------
    #   Build chain (SYNC)
    # ---------------------------------------------------
    def _build_chain(self, mode: str):
        if mode == "form_formatter":
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompts[mode]),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{user_input}\n\n{format_instructions}")
            ]).partial(
                format_instructions=self.form_parser.get_format_instructions()
            )

        elif mode == "context":
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompts[mode]),
                ("human", "{user_input}\n\n{format_instructions}")
            ]).partial(
                format_instructions=self.context_parser.get_format_instructions()
            )

        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompts[mode]),
                ("human", "{user_input}")
            ])

        chain = prompt | self.llm

        if mode == "form_formatter":
            chain |= self.form_parser | RunnableLambda(lambda x: {"output": str(x)})

        elif mode == "context":
            chain |= self.context_parser | RunnableLambda(lambda x: {"output": str(x)})

        return RunnableWithMessageHistory(
            chain,
            lambda _: self.history,  # always same history
            input_messages_key="user_input",
            history_messages_key="history",
        )

    # ---------------------------------------------------
    #   CHAT (SYNC)
    # ---------------------------------------------------
    def chat(self, user_input: str, session_id: str = "default", mode: str = None):
        """Chat with user"""
        try:
            mode = mode or self.default_mode
            chain_with_memory = self._build_chain(mode)

            # SYNC invoke()
            result = chain_with_memory.invoke(
                {"user_input": user_input},
                config={"configurable": {"session_id": session_id}},
            )

            raw = result.get("output", "")

            import ast
            return ast.literal_eval(raw)

        except Exception as e:
            print(f"Error in AI.chat: {e}")
            return ""
