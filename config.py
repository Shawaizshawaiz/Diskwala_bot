import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Required - Telegram Bot Token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Optional - Channel ID to dump videos (e.g. -1001234567890)
DUMP_CHAT_ID = os.getenv("DUMP_CHAT_ID", "")

# Validate required config
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing! Add it to your .env file.")
