import os
import random
import time
from pathlib import Path

from dotenv import load_dotenv

print("----------------------------------------------------------")

def env_maker():
    print(f"[!] No ENV file found at: {default_env_file}")
    print("🧾 Please enter environment variables manually:")

    # Ask user for runtime values
    runtime_profile = "dev"
    print(f" using {runtime_profile}.env")

    # Create an ENV folder if it doesn't exist
    env_dir = project_root / "ENV"
    env_dir.mkdir(exist_ok=True)

    # Save a new .env file
    runtime_env_file = env_dir / f"{runtime_profile}.env"
    with open(runtime_env_file, "w") as f:
        f.write(f"PROFILE={runtime_profile}\n")

    print(f"[+] Created runtime ENV file at: {runtime_env_file}")

    # Load the new .env file
    load_dotenv(runtime_env_file, override=True)




#  Locate the default ENV path
project_root = Path(__file__).resolve().parents[1]
runtime_profile = os.getenv("PROFILE", "dev")
default_env_file = project_root / "ENV" / f"{runtime_profile}.env"


# Check if default .env exists
if default_env_file.exists():
    print(f"[✔] ENV file found at: {default_env_file}")
    load_dotenv(default_env_file, override=False)
else:
    env_maker()

#  PROFILE value
PROFILE =  default_env_file.stem or "dev"
print("📌 PROFILE =", PROFILE)

#  Bot Info
BOT_NAME = os.getenv("BOT_NAME", "Tweakio")
BOT_NUMBER = os.getenv("BOT_NUMBER", "")
BOT_NUM_COUNTRY = os.getenv("BOT_NUM_COUNTRY", "")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER", "")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")

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
AGENT_AI_KEY = os.getenv("AGENT_AI_KEY", "")
QUANTIFIER = os.getenv("QUANTIFIER", "//")
NLP = os.getenv("NLP", "/say")
AGENT_ID = os.getenv("AGENT_ID", "")
WEBHOOK_ID = os.getenv("WEBHOOK_ID", "")
BASE_URL = os.getenv("BASE_URL", "")
INTRO_IMG_URL = os.getenv("INTRO_IMG_URL", "")

#  Debug Mode & System configs
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_CHAT = int(os.getenv("MAX_CHAT", "5"))
REFRESH_TIME = int(os.getenv("REFRESH_TIME", "5"))
SLOW_MO = int(os.getenv("SLOW_MO", f"{random.randint(200, 300)}"))
BROWSER_INIT_TIMEOUT = int(os.getenv("10_000", "0"))
LOGIN_WAIT_TIME = int(os.getenv("LOGIN_WAIT_TIME", "180_000"))
LOGIN_METHOD = int(os.getenv("LOGIN_METHOD", "2"))  # 1 for scan, 2 for code
GLOBAL_MODE = os.getenv("GLOBAL_MODE", "False")
RESTART_TIME= int(os.getenv("RESTART_TIME","2"))
