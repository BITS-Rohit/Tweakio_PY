import random
from dotenv import load_dotenv
from pathlib import Path
import os


print("----------------------------------------------------------")
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[ENV] Loaded .env from: {env_path}")
else:
    print(env_path)
    print("[ENV] Running in CI or production — skipping .env")


#  PROFILE value
PROFILE =  os.getenv("PROFILE","dev")
print("[ENV CHECK] PROFILE =", PROFILE)

#  Bot Info
BOT_NAME = os.getenv("BOT_NAME", "Tweakio")
BOT_NUMBER = os.getenv("BOT_NUMBER", "")
BOT_NUM_COUNTRY = os.getenv("BOT_NUM_COUNTRY", "")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER", "")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")

# Quantifier :
QUANTIFIER = os.getenv("QUANTIFIER", "//")
NLP = os.getenv("NLP", "/say")

#  GitHub Config
GH_TOKEN = os.getenv("GH_TOKEN", "")
REPO_NAME = os.getenv("REPO_NAME", "")
BRANCH_NAME = os.getenv("BRANCH_NAME", "main")

#  API Keys
GEM_API_KEY = os.getenv("GEM_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

#  Custom Search
CSE_ID = os.getenv("CSE_ID", "")

#  Agent.ai Integration
# AI_NAME=os.getenv("AI_NAME", "gpt")
POST_URL = os.getenv("POST_URL", "https://api.agent.ai/v1/agent/mr9zb4vn5xtb166v/webhook/9c538b06/async")
GET_URL = os.getenv("GET_URL", "https://api.agent.ai/v1/agent/mr9zb4vn5xtb166v/webhook/9c538b06/status/<run_id>")
# AGENT_AI_KEY = os.getenv("AGENT_AI_KEY", "")
# AGENT_ID = os.getenv("AGENT_ID", "")
# WEBHOOK_ID = os.getenv("WEBHOOK_ID", "")
# BASE_URL = os.getenv("BASE_URL", "")
# INTRO_IMG_URL = os.getenv("INTRO_IMG_URL", "")

#  Debug Mode & System configs
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_CHAT = int(os.getenv("MAX_CHAT", "5"))
REFRESH_TIME = int(os.getenv("REFRESH_TIME", "5"))
SLOW_MO = int(os.getenv("SLOW_MO", f"{random.randint(200, 300)}"))
BROWSER_INIT_TIMEOUT = int(os.getenv("10_000", "0"))
LOGIN_WAIT_TIME = int(os.getenv("LOGIN_WAIT_TIME", "180_000"))
LOGIN_METHOD = int(os.getenv("LOGIN_METHOD", "1"))  # 1 for scan, 2 for code
GLOBAL_MODE = os.getenv("GLOBAL_MODE", "False")
RESTART_TIME= int(os.getenv("RESTART_TIME","2"))

# -- LangSmith -- #
LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT=os.getenv("LANGCHAIN_PROJECT", "Lang-Bot")
