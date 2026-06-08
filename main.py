import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
from terabox import get_direct_link, is_terabox_url
from keep_alive import keep_alive

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ─────────────────────────────────────────────
# /start command
# ─────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def start(message):
    """Welcome message with usage instructions."""
    text = (
        "👋 <b>Welcome to Terabox Video Player Bot!</b>\n\n"
        "📌 <b>How to use:</b>\n"
        "Just send me any <b>Terabox share link</b> and I will give you "
        "direct playable/downloadable links instantly — no app needed!\n\n"
        "🔗 <b>Example link format:</b>\n"
        "<code>https://terabox.com/s/1ABCxyzExample</code>\n"
        "or\n"
        "<code>https://teraboxapp.com/s/1ABCxyzExample</code>\n\n"
        "⚡ Powered by SaveTube API\n"
        "✅ No downloads • No ads • Instant links"
    )
    bot.send_message(message.chat.id, text)


# ─────────────────────────────────────────────
# /help command
# ─────────────────────────────────────────────

@bot.message_handler(commands=["help"])
def help_cmd(message):
    """Show help message."""
    text = (
        "ℹ️ <b>Help</b>\n\n"
        "1. Copy a Terabox share link\n"
        "2. Paste it here and send\n"
        "3. Click any button to watch or download\n\n"
        "⚠️ Only <b>public</b> Terabox links work.\n"
        "Private/password-protected links are not supported."
    )
    bot.send_message(message.chat.id, text)


# ─────────────────────────────────────────────
# Handle all text messages (Terabox links)
# ─────────────────────────────────────────────

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_message(message):
    """Main handler — processes Terabox links sent by user."""
    url = message.text.strip()

    # Check if it looks like a URL at all
    if not url.startswith("http"):
        bot.send_message(
            message.chat.id,
            "⚠️ Please send a valid Terabox link starting with <code>https://</code>"
        )
        return

    # Validate it's a Terabox link
    if not is_terabox_url(url):
        bot.send_message(
            message.chat.id,
            "❌ This doesn't look like a Terabox link.\n\n"
            "Supported domains:\n"
            "• terabox.com\n"
            "• teraboxapp.com\n"
            "• 1024tera.com\n"
            "• freeterabox.com"
        )
        return

    # Send processing message
    wait_msg = bot.send_message(
        message.chat.id,
        "⏳ <b>Processing your link, please wait...</b>"
    )

    # Extract direct links
    result = get_direct_link(url)

    # Delete the "processing" message
    try:
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
        pass

    # Handle failure
    if not result:
        bot.send_message(
            message.chat.id,
            "❌ <b>Could not process this link.</b>\n\n"
            "Make sure it's a valid <b>public</b> Terabox link.\n"
            "Private or expired links won't work."
        )
        return

    # ── Success: Build response ──
    title = result["title"]
    thumbnail = result["thumbnail"]
    resolutions = result["resolutions"]

    # Build inline keyboard with all available quality buttons
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []

    # Priority order for display
    priority = ["1080p", "720p", "480p", "360p", "HD", "SD", "Fast"]

    for quality in priority:
        if quality in resolutions:
            link = resolutions[quality]
            if quality in ["1080p", "720p", "480p", "360p"]:
                label = f"▶️ Watch {quality}"
            elif quality == "HD":
                label = "⬇️ Download HD"
            elif quality == "SD":
                label = "⬇️ Download SD"
            else:
                label = f"⚡ {quality}"
            buttons.append(InlineKeyboardButton(label, url=link))

    # Add any remaining links not in priority list
    for quality, link in resolutions.items():
        if quality not in priority:
            buttons.append(InlineKeyboardButton(f"🔗 {quality}", url=link))

    markup.add(*buttons)

    # Caption text
    caption = (
        f"🎬 <b>{title}</b>\n\n"
        f"🔗 <a href='{url}'>Original Terabox Link</a>\n\n"
        "👇 <b>Choose quality to watch or download:</b>"
    )

    # Send thumbnail + buttons if thumbnail exists
    if thumbnail and thumbnail.startswith("http"):
        try:
            bot.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=caption,
                reply_markup=markup
            )
        except Exception:
            # Fallback to text if photo fails
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=markup,
                disable_web_page_preview=True
            )
    else:
        bot.send_message(
            message.chat.id,
            caption,
            reply_markup=markup,
            disable_web_page_preview=True
        )


# ─────────────────────────────────────────────
# Start bot
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Start Flask keep-alive server (for Replit)
    keep_alive()

    print("🤖 Terabox Bot is starting...")
    print("✅ Bot is running! Send a Terabox link on Telegram.")

    # Start polling — restarts automatically on connection errors
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
