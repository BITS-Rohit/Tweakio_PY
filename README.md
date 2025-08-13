# Tweakio — WhatsApp Web Automation Bot

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/yourrepo)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Issues](https://img.shields.io/badge/issues-welcome-orange)](https://github.com/yourusername/yourrepo/issues)

> **Tweakio** — a human-like WhatsApp Web automation agent that centralizes actions, simulates real-user behavior, and allows easy AI-driven message processing and integrations.

---

## Table of Contents

* [Why Tweakio?](#why-tweakio)
* [Key Features](#key-features)
* [High-level Flow](#high-level-flow)
* [Requirements](#requirements)
* [Quick Start](#quick-start)
* [.env (configuration)](#env-configuration)
* [Commands / Menu](#commands--menu)
* [Architecture & Modules](#architecture--modules)
* [Contributing](#contributing)
* [Testing & CI](#testing--ci)
* [Security & Privacy](#security--privacy)
* [Roadmap](#roadmap)
* [Support & Contact](#support--contact)
* [License](#license)
* [Final Demo](#final-demo)

---

## Why Tweakio?

Tweakio is built to automate WhatsApp Web **without** relying on the Business API or unsafe reverse-engineered scripts. It focuses on:

* Human-like browser simulation (stealth, mouse movements, delays) to reduce detection risk.
* Easy integration with AI backends (Gemini, GROQ, OpenRouter, etc.) for natural responses and command routing.
* Acting as a hub to signal other connected automation agents (manual integration required).
* A modular, extensible architecture so companies or hobbyists can build custom automations on top.

---

## Key Features

* Natural language + command-based routing using quantifiers (e.g. `//`) and trigger prefixes.
* Robust media handling: send & detect images (preview), docs, audio, video, GIFs, stickers, quoted messages.
* Admin controls: pause/unpause, ban/unban chats, admin list management.
* Modes: per-chat, global mode, and configurable `MAX_CHAT` concurrency.
* Partial AI selectors (Playwright modern selectors + regex) for resilience against UI changes.
* Planned: async uploads/downloads, profile automation (DP/profile), YouTube/Google live search integration.

---

## High-level Flow

```
Incoming message -> Bot scans chats -> if NEW -> open chat -> check for prefix (e.g. //) ->
parse quantifier & command -> forward remaining text to configured LLM -> send response
```

**Command format:**

```
<Quant> <f_name> <f_info (optional)>
```

Example:

```
 //weather Delhi
 //git commit "fix bug"
```

---

## Requirements

* Python 3.10+
* Playwright + playwright-stealth
* LangChain (optional, for advanced AI routing)

Setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

Direct install:

```bash
pip install playwright playwright-stealth
playwright install
pip install requests python-dotenv pyperclip
pip install -U langchain langsmith
```

---

## Quick Start

1. Clone the repo:

```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

2. Copy and edit environment file:

```bash
cp Example.env.example .env
# edit values in .env (never commit secrets)
```

3. Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

4. Start the bot:

```bash
python Whatsapp/Start.py
```

---

## .env (configuration)

Example:

```env
PROFILE=dev
DEBUG=false
MAX_CHAT=5
REFRESH_TIME=5
SLOW_MO=250
GLOBAL_MODE=False
RESTART_TIME=2

BOT_NUMBER="9183XXXXXXXX"
BOT_NAME="Tweakio"
ADMIN_NUMBER="9183XXXXXXXX"
ADMIN_NAME="Admin"

GEM_API_KEY="YOUR_GOOGLE_GENAI_KEY"
GROQ_API_KEY="YOUR_GROQ_OR_OPENROUTER_KEY"
CSE_ID="YOUR_GOOGLE_CSE_ID"
INTRO_IMG_URL="https://imgur.com/xyz.jpg"

BROWSER_INIT_TIMEOUT=10000
LOGIN_WAIT_TIME=180000
LOGIN_METHOD=2

GH_TOKEN="ghp_xxx"
REPO_NAME="yourusername/yourrepo"
BRANCH_NAME=main
```

---

## Commands / Menu

* `setmaxchat <n>` — limit concurrent chats
* `menu` — show menu
* `pause on` / `pause off` — admin-only
* `showq` — display quantifier
* `ban <phone>` / `unban <phone>` — block/unblock
* `media send` — send media
* `detect` — detect incoming media
* `inject` — send as doc
* `add <phone>` / `remove <phone>` — admin management
* `setgc on/off` — toggle global mode
* `banlist` — show banned chats
* `showlist` — show admin list
* `setq` — set quantifier

---

## Architecture & Modules

```
/Whatsapp
  ├─ Start.py
  ├─ core/
  ├─ integrations/
  ├─ utils/
  ├─ tests/
Example.env.example
requirements.txt
README.md
```

---

## Contributing

Checklist:

1. Fork the repo
2. Create a feature branch
3. Install dependencies
4. Test before pushing
5. Open PR with description

Labels: `good first issue`, `help wanted`, `bug`, `enhancement`, `docs`

---

## Testing & CI

Use `pytest` for tests.
Example CI pipeline:

* Checkout
* Setup Python
* Install deps
* Install Playwright
* Run tests

---

## Security & Privacy

* Never commit `.env` or keys
* Rate-limit sensitive actions
* Rotate API keys regularly

---

## Roadmap

* Async upload/download
* Profile automation
* YouTube & Google live search
* Plugin system for agents

---

## Support & Contact

* GitHub issues
* Discussions

---

## License

MIT License

---

## Final Demo

**Mobile view:**  
<img width="360" height="640" alt="Mobile Demo" src="https://github.com/user-attachments/assets/b9608c12-04ef-43d9-ba45-4c5d16149a8a" />

**WhatsApp Web view:**  
<img width="960" height="540" alt="Web Demo" src="https://github.com/user-attachments/assets/cdf54eee-cb08-43cf-b41f-dad5e6afb1c7" />

**Video Demo:**  
Click on it to view.
[![Watch the Demo](https://i.ibb.co/1fMkd8Y0/thumbnail.jpg)](https://drive.google.com/file/d/1pjlD6HDqRPpdDhgKtuEwiEpqBnmUWYtN/view?usp=sharing)

*Also at new login u can face this bitch , so  to remove this is to manually , else if errored then just restart it , TO fix this is like random, comes or not for this addition will only long the time or overhead.*
![img.png](PopUp.png)

