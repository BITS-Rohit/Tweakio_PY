import os
import random
from pathlib import Path

from dotenv import load_dotenv

env_file = Path("ENV/dev.env")  # or "ENV/me.env"
load_dotenv(dotenv_path=env_file)


# 🔧 Profile Info
PROFILE = os.getenv("PROFILE", "default")

# 🤖 Bot Info
BOT_NAME = os.getenv("BOT_NAME", "Tweakio")
BOT_NUMBER = os.getenv("BOT_NUMBER", "")
BOT_NUM_COUNTRY=os.getenv("BOT_NUM_COUNTRY","")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER", "")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")

# 🔗 GitHub Config
GH_TOKEN = os.getenv("GH_TOKEN", "")
REPO_NAME = os.getenv("REPO_NAME", "")
BRANCH_NAME = os.getenv("BRANCH_NAME", "main")

# 🔑 API Keys
GEM_API_KEY = os.getenv("GEM_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# 🔍 Custom Search
CSE_ID = os.getenv("CSE_ID", "")

# 🤖 Agent.ai Integration
AGENT_AI_KEY = os.getenv("AGENT_AI_KEY", "")
QUANTIFIER = os.getenv("QUANTIFIER", "//")
AGENT_ID = os.getenv("AGENT_ID", "")
WEBHOOK_ID = os.getenv("WEBHOOK_ID", "")
BASE_URL = os.getenv("BASE_URL", "")
INTRO_IMG_URL = os.getenv("INTRO_IMG_URL", "")

# 🐞 Debug Mode & System configs
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_CHAT = int(os.getenv("MAX_CHAT",5))
REFRESH_TIME = int(os.getenv("REFRESH_TIME",5))
SLOW_MO = int(os.getenv("SLOW_MO",random.randint(200,300)))
BROWSER_INIT_TIMEOUT = int(os.getenv(10_000))
LOGIN_WAIT_TIME = int(os.getenv("LOGIN_WAIT_TIME",180_000))
LOGIN_METHOD= int(os.getenv("LOGIN_METHOD",2))   # 1 for scan, 2 for code

