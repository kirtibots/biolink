import os
import re
import time
import logging
from collections import defaultdict

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.errors import RPCError, FloodWait
from pymongo import MongoClient

# ============================================================
# BIO LINK CLEANER BOT
# Group bio-link checker / warning / mute bot
# ============================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "BiolinkCleanerBot").lstrip("@")

SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/")
UPDATE_URL = os.getenv("UPDATE_URL", "https://t.me/")
OWNER_URL = os.getenv("OWNER_URL", "https://t.me/")
PROMO_URL = os.getenv("PROMO_URL", "https://t.me/")

WARN_LIMIT = int(os.getenv("WARN_LIMIT", "3"))
MUTE_MINUTES = int(os.getenv("MUTE_MINUTES", "60"))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("BIO-LINK-CLEANER")

if not all([API_ID, API_HASH, BOT_TOKEN, MONGO_URI]):
    raise RuntimeError("Set API_ID, API_HASH, BOT_TOKEN and MONGO_URI environment variables.")

app = Client(
    "biolink_cleaner",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

mongo = MongoClient(MONGO_URI)
db = mongo["bio_link_cleaner"]
groups = db["groups"]
auth_users = db["auth_users"]
warnings = db["warnings"]
stats = db["stats"]

START_TEXT = """❖ <b>HEY I'M <font color="#2B78A0">BIO LINK CLEANER</font> 🚨 🥳</b>

༺ A BIO LINK CHECKER BOT FOR GROUPS.

» DELETE MESSAGE HAVE LINKS IN BIO.
» SUPPORT AUTH USER & ADMIN COMMAND.
» I CAN MUTE & WARN USERS WITH MENTION.

➳ CLICK 'HELP' TO SEE ALL COMMANDS.

✦ MADE BY :- <a href="https://t.me/">PURVI-BOTS™</a>"""

ABOUT_TEXT = """❖ <b>A BIO LINK CHECKER BOT FOR GROUPS.</b>

━━━━━━━━━━━━━━━━━━

• <b>WRITTEN IN</b> » <code>PYTHON</code>
• <b>DATABASE</b> » <code>MONGO-DB</code>
• <b>HELP WITH</b> » <code>PYROGRAM</code>

━━━━━━━━━━━━━━━━━━

➥ I CAN EASILY MAINTAIN YOUR GROUP.
➥ PROMOTE ME WITH DELETE & BAN RIGHTS.
➥ ADD ME NOW BABY IN YOUR GROUPS.

━━━━━━━━━━━━━━━━━━

❖ <b>UPDATES CHANNEL</b> ➜ <a href="https://t.me/">PURVI-BOTS</a>
❖ <b>SUPPORT CHAT</b> ➜ <a href="https://t.me/">PURVI-UPDATES</a>

━━━━━━━━━━━━━━━━━━

➤ <b>BOT STATUS & MORE BOTS</b> - <a href="https://t.me/">CLICK HERE</a>
➤ <b>PAID PROMOTION</b> :- <a href="https://t.me/">CONTACT HERE</a>"""

HELP_TEXT = """❖ <b>HERE IS HELP MESSAGE BOT.</b>

◎ <b>ALL USERS COMMANDS :</b>

<code>/start</code> - START THE BOT.
<code>/ping</code> - CHECK BOT ALIVE OR DEAD.
<code>/stats</code> - CHECK BOT STATS.

◎ <b>HERE IS MAIN MODULES :</b>

<code>/auth</code> - AUTHORIZE A USER.
<code>/unauth</code> - UNAUTHORIZE A USER.
<code>/authusers</code> - SHOW ALL AUTHORIZED USER.
<code>/clearauthusers</code> - REMOVE ALL AUTHORIZED USERS.
<code>/resetwarn</code> - RESET THE WARNING COUNT.

➳ <b>NOTE :- ONLY WORKS IN GROUPS & ONLY USE GROUP ADMINS.</b>

✦ <b>POWERED BY » ALPHA-BABY</b>"""

def start_keyboard():
    add_url = f"https://t.me/{BOT_USERNAME}?startgroup=true"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⊞ ADD ME IN YOUR GROUP ⊞", url=add_url)],
        [
            InlineKeyboardButton("≡ OWNER ≡", url=OWNER_URL),
            InlineKeyboardButton("≡ ABOUT ≡", callback_data="about")
        ],
        [InlineKeyboardButton("≡ HELP AND COMMANDS ≡", callback_data="help")]
    ])

def about_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("≡ SUPPORT ≡", url=SUPPORT_URL),
            InlineKeyboardButton("≡ UPDATE ≡", url=UPDATE_URL)
        ],
        [InlineKeyboardButton("≡ BACK ≡", callback_data="back")]
    ])

def help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("≡ SUPPORT ≡", url=SUPPORT_URL),
            InlineKeyboardButton("≡ BACK ≡", callback_data="back")
        ]
    ])

def is_group(chat):
    return chat and chat.type in ("group", "supergroup")

def is_link(text: str) -> bool:
    if not text:
        return False
    patterns = [
        r"https?://\S+",
        r"(?:www\.)\S+\.\S+",
        r"(?:t\.me|telegram\.me|telegram\.dog)/\S+",
        r"tg://\S+",
        r"\b[a-z0-9.-]+\.(?:com|net|org|me|in|co|io|xyz|site|online|live|shop|dev|app)\b",
    ]
    return any(re.search(p, text, re.I) for p in patterns)

def has_bio_link(bio: str) -> bool:
    if not bio:
        return False
    return is_link(bio)

def inc_stat(key, amount=1):
    stats.update_one({"_id": key}, {"$inc": {"value": amount}}, upsert=True)

def get_stat(key):
    doc = stats.find_one({"_id": key})
    return int(doc["value"]) if doc else 0

def get_warn(chat_id, user_id):
    doc = warnings.find_one({"chat_id": chat_id, "user_id": user_id})
    return int(doc["count"]) if doc else 0

def set_warn(chat_id, user_id, count):
    warnings.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True
    )

def is_authorized(chat_id, user_id):
    return auth_users.find_one({"chat_id": chat_id, "user_id": user_id}) is not None

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "owner")
    except RPCError:
        return False

async def can_manage(client, message):
    if not message.from_user:
        return False
    return await is_admin(client, message.chat.id, message.from_user.id)

async def get_target(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    if len(message.command) > 1:
        arg = message.command[1]
        try:
            if arg.lstrip("-").isdigit():
                return await app.get_users(int(arg))
            return await app.get_users(arg)
        except RPCError:
            return None
    return None

@app.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    await message.reply_text(
        START_TEXT,
        reply_markup=start_keyboard(),
        disable_web_page_preview=True
    )

@app.on_message(filters.command("start") & filters.group)
async def start_group(_, message):
    await message.reply_text(
        START_TEXT,
        reply_markup=start_keyboard(),
        disable_web_page_preview=True
    )

@app.on_callback_query()
async def callbacks(_, query):
    data = query.data
    try:
        if data == "about":
            await query.message.edit_text(
                ABOUT_TEXT,
                reply_markup=about_keyboard(),
                disable_web_page_preview=True
            )
        elif data == "help":
            await query.message.edit_text(
                HELP_TEXT,
                reply_markup=help_keyboard(),
                disable_web_page_preview=True
            )
        elif data == "back":
            await query.message.edit_text(
                START_TEXT,
                reply_markup=start_keyboard(),
                disable_web_page_preview=True
            )
        await query.answer()
    except RPCError:
        await query.answer("Unable to update message.", show_alert=True)

@app.on_message(filters.command("ping"))
async def ping(_, message):
    started = time.perf_counter()
    msg = await message.reply_text("» <b>ᴘɪɴɢ...</b>")
    ms = round((time.perf_counter() - started) * 1000)
    await msg.edit_text(f"» <b>ᴘᴏɴɢ!</b> ⚡ <code>{ms} ms</code>")

@app.on_message(filters.command("stats"))
async def bot_stats(_, message):
    text = (
        "✦ <b>BOT STATS</b>\n\n"
        f"» Messages checked: <code>{get_stat('messages_checked')}</code>\n"
        f"» Bio links found: <code>{get_stat('bio_links')}</code>\n"
        f"» Messages deleted: <code>{get_stat('messages_deleted')}</code>\n"
        f"» Warnings issued: <code>{get_stat('warnings')}</code>"
    )
    await message.reply_text(text)

@app.on_message(filters.command("auth") & filters.group)
async def auth_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text("❌ <b>Only group admins can use this command.</b>")
    target = await get_target(message)
    if not target:
        return await message.reply_text("» Reply to a user or use <code>/auth user_id</code>.")
    auth_users.update_one(
        {"chat_id": message.chat.id, "user_id": target.id},
        {"$set": {"name": target.first_name or "", "username": target.username or ""}},
        upsert=True
    )
    await message.reply_text(
        f"✅ <b>AUTHORIZED:</b> {target.mention}\n"
        "» This user is now allowed to use bot admin modules."
    )

@app.on_message(filters.command("unauth") & filters.group)
async def unauth_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text("❌ <b>Only group admins can use this command.</b>")
    target = await get_target(message)
    if not target:
        return await message.reply_text("» Reply to a user or use <code>/unauth user_id</code>.")
    result = auth_users.delete_one({"chat_id": message.chat.id, "user_id": target.id})
    if result.deleted_count:
        await message.reply_text(f"✅ <b>UNAUTHORIZED:</b> {target.mention}")
    else:
        await message.reply_text("⚠️ <b>User was not authorized.</b>")

@app.on_message(filters.command("authusers") & filters.group)
async def authusers_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text("❌ <b>Only group admins can use this command.</b>")
    rows = list(auth_users.find({"chat_id": message.chat.id}).limit(50))
    if not rows:
        return await message.reply_text("» <b>No authorized users found.</b>")
    lines = ["◎ <b>AUTHORIZED USERS:</b>", ""]
    for i, row in enumerate(rows, 1):
        username = f"@{row['username']}" if row.get("username") else row.get("name", "User")
        lines.append(f"{i}. {username} <code>{row['user_id']}</code>")
    await message.reply_text("\n".join(lines))

@app.on_message(filters.command("clearauthusers") & filters.group)
async def clearauthusers_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text("❌ <b>Only group admins can use this command.</b>")
    result = auth_users.delete_many({"chat_id": message.chat.id})
    await message.reply_text(f"✅ <b>Removed {result.deleted_count} authorized user(s).</b>")

@app.on_message(filters.command("resetwarn") & filters.group)
async def resetwarn_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text("❌ <b>Only group admins can use this command.</b>")
    target = await get_target(message)
    if not target:
        return await message.reply_text("» Reply to a user or use <code>/resetwarn user_id</code>.")
    set_warn(message.chat.id, target.id, 0)
    await message.reply_text(f"♻️ <b>Warning count reset for</b> {target.mention}")

@app.on_message(filters.group & ~filters.service)
async def bio_checker(_, message):
    if not message.from_user or message.from_user.is_bot:
        return

    # Never moderate group administrators.
    if await is_admin(app, message.chat.id, message.from_user.id):
        return

    inc_stat("messages_checked")

    try:
        user = await app.get_chat(message.from_user.id)
        bio = getattr(user, "bio", None) or ""
    except RPCError:
        return

    if not has_bio_link(bio):
        return

    # Authorized users are exempt.
    if is_authorized(message.chat.id, message.from_user.id):
        return

    inc_stat("bio_links")

    try:
        await message.delete()
        inc_stat("messages_deleted")
    except RPCError:
        pass

    current = get_warn(message.chat.id, message.from_user.id) + 1
    set_warn(message.chat.id, message.from_user.id, current)
    inc_stat("warnings")

    mention = message.from_user.mention
    if current >= WARN_LIMIT:
        try:
            until = int(time.time()) + (MUTE_MINUTES * 60)
            await app.restrict_chat_member(
                message.chat.id,
                message.from_user.id,
                permissions=ChatPermissions(),
                until_date=until
            )
            await message.reply_text(
                f"⚠️ {mention}\n"
                f"» <b>Your bio contains a link.</b>\n"
                f"» Warning: <code>{current}/{WARN_LIMIT}</code>\n"
                f"🔇 <b>You have been muted for {MUTE_MINUTES} minutes.</b>",
                disable_web_page_preview=True
            )
            set_warn(message.chat.id, message.from_user.id, 0)
        except RPCError as e:
            log.warning("Mute failed: %s", e)
    else:
        try:
            await message.reply_text(
                f"⚠️ {mention}\n"
                f"» <b>Remove the link from your Telegram bio.</b>\n"
                f"» Warning: <code>{current}/{WARN_LIMIT}</code>",
                disable_web_page_preview=True
            )
        except RPCError:
            pass

def print_startup_logger():
    try:
        import sys
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    except Exception:
        py_version = "Unknown"

    try:
        import pyrogram
        pyro_version = getattr(pyrogram, "__version__", "2.0.106")
    except Exception:
        pyro_version = "2.0.106"

    # Keep this value configurable so the logger can match the deployed plugin count.
    plugin_count = os.getenv("PLUGIN_COUNT", "15")
    bot_name = os.getenv("LOGGER_BOT_NAME", "Purvi 🐒")
    powered_by = os.getenv("LOGGER_POWERED_BY", "PURVI-BOTS")

    log.info("╔══════════════════════════════════════════════════════╗")
    log.info("║ ❖ BOT STARTED SUCCESSFULLY                           ║")
    log.info("║                                                      ║")
    log.info("║ • BOT      :- %s", bot_name)
    log.info("║ • PLUGINS  :- %s LOADED", plugin_count)
    log.info("║ • PYROGRAM :- %s", pyro_version)
    log.info("║ • PYTHON   :- %s", py_version)
    log.info("║                                                      ║")
    log.info("║ » POWERED BY :- %s", powered_by)
    log.info("╚══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    print_startup_logger()
    app.run()
