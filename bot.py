import os, re, time, asyncio, logging
from pymongo import MongoClient
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

# ================= CONFIG =================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")

BOT_USERNAME = os.getenv("BOT_USERNAME", "Nidhiprobot").lstrip("@")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/annu_support")
UPDATE_URL = os.getenv("UPDATE_URL", "https://t.me/annu_updates")
OWNER_URL = os.getenv("OWNER_URL", "https://t.me/Only_badnam")
LOGGER_ID = int(os.getenv("LOGGER_GROUP_ID", "-1003979103138"))

WARN_LIMIT = int(os.getenv("WARN_LIMIT", "3"))
MUTE_MINUTES = int(os.getenv("MUTE_MINUTES", "60"))

if not API_ID or not API_HASH or not BOT_TOKEN or not MONGO_URI:
    raise RuntimeError(
        "API_ID, API_HASH, BOT_TOKEN and MONGO_URI are required."
    )

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
log = logging.getLogger("BIO-LINK-BOT")

START_TIME = time.time()

# ================= APP =================

app = Client(
    "biolink_cleaner",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=16
)

# ================= DATABASE =================

mongo = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = mongo["bio_link_cleaner"]
auth_users = db["auth_users"]
warnings = db["warnings"]
stats = db["stats"]

# ================= TEXT =================

START_TEXT = """
<b>❖ ʜєʏ ʙᴧʙʏ !!

𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨 ɪs ᴧʟɪᴠє 🥀 ᴧηᴅ
ᴡσʀᴋɪηɢ ꜰɪηє ᴡɪᴛʜ

➥ ᴀ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ ʙᴏᴛ ғᴏʀ ɢʀᴏᴜᴘs.

➥ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ᴡʜᴇɴ ᴜsᴇʀ ʜᴀs ᴀ ʟɪɴᴋ ɪɴ ʙɪᴏ.
➥ sᴜᴘᴘᴏʀᴛ ᴀᴜᴛʜ ᴜsᴇʀ & ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.
➥ ᴡᴀʀɴ & ᴍᴜᴛᴇ ᴜsᴇʀs ᴡɪᴛʜ ᴍᴇɴᴛɪᴏɴ.

➳ ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.

✦ 𝐏σᴡєʀєᴅ вʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

ABOUT_TEXT = """
<b>────────────────────

❖ ᴀ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ ʙᴏᴛ ғᴏʀ ɢʀᴏᴜᴘs.

● ᴡʀɪᴛᴛєη ɪη » ᴘʏᴛʜση
● ᴅᴀᴛᴀʙᴀsᴇ » ᴍᴏɴɢᴏ-ᴅʙ

➥ ᴍᴀɪɴᴛᴀɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.
➥ ᴅᴇʟᴇᴛᴇ ʙɪᴏ ʟɪɴᴋ ᴜsᴇʀ ᴍᴇssᴀɢᴇs.
➥ ᴡᴀʀɴ & ᴍᴜᴛᴇ ᴜsᴇʀs.

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

HELP_TEXT = f"""
<b>❖ ʜᴇʟᴘ

⊚ ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs

/start - sᴛᴀʀᴛ ʙᴏᴛ
/ping - ᴄʜᴇᴄᴋ ʙᴏᴛ
/stats - sʜᴏᴡ sᴛᴀᴛs

⊚ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ

/auth - ᴀᴜᴛʜᴏʀɪᴢᴇ ᴜsᴇʀ
/unauth - ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ
/authusers - ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs
/clearauthusers - ᴄʟᴇᴀʀ ᴀᴜᴛʜ ᴜsᴇʀs
/resetwarn - ʀᴇsᴇᴛ ᴡᴀʀɴ

━━━━━━━━━━━━━━━━━━

➥ 1sᴛ ᴡᴀʀɴɪɴɢ
➥ 2ɴᴅ ᴡᴀʀɴɪɴɢ
➥ {WARN_LIMIT}ʀᴅ ᴡᴀʀɴɪɴɢ ➜ ᴀᴜᴛᴏ ᴍᴜᴛᴇ

✦ ᴍᴜᴛᴇ ᴛɪᴍᴇ : {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs</b>
"""

# ================= BUTTONS =================

def home_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⊞ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⊞",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("≡ ᴏᴡɴᴇʀ ≡", url=OWNER_URL),
            InlineKeyboardButton("≡ ᴀʙᴏᴜᴛ ≡", callback_data="about")
        ],
        [
            InlineKeyboardButton(
                "≡ ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs ≡",
                callback_data="help"
            )
        ]
    ])

def about_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("≡ sᴜᴘᴘᴏʀᴛ ≡", url=SUPPORT_URL),
            InlineKeyboardButton("≡ ᴜᴘᴅᴀᴛᴇ ≡", url=UPDATE_URL)
        ],
        [InlineKeyboardButton("≡ ʙᴀᴄᴋ ≡", callback_data="back")]
    ])

def help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("≡ sᴜᴘᴘᴏʀᴛ ≡", url=SUPPORT_URL),
            InlineKeyboardButton("≡ ʙᴀᴄᴋ ≡", callback_data="back")
        ]
    ])

# ================= DATABASE =================

def increment(name):
    try:
        stats.update_one(
            {"_id": name},
            {"$inc": {"value": 1}},
            upsert=True
        )
    except Exception:
        pass

def get_stat(name):
    try:
        x = stats.find_one({"_id": name})
        return int(x.get("value", 0)) if x else 0
    except Exception:
        return 0

def get_warn(chat_id, user_id):
    try:
        x = warnings.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        })
        return int(x.get("count", 0)) if x else 0
    except Exception:
        return 0

def set_warn(chat_id, user_id, count):
    warnings.update_one(
        {
            "chat_id": chat_id,
            "user_id": user_id
        },
        {"$set": {"count": count}},
        upsert=True
    )

# ================= HELPERS =================

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        )
    except Exception:
        return False

async def get_bio(user_id):
    try:
        chat = await app.get_chat(user_id)
        return (chat.bio or "").strip()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await get_bio(user_id)
    except Exception as e:
        log.warning("BIO ERROR: %s", e)
        return ""

def is_auth(chat_id, user_id):
    try:
        return auth_users.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        }) is not None
    except Exception:
        return False

# ================= LINK DETECTOR =================

LINK_RE = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|"
    r"(?:t\.me|telegram\.me|telegram\.dog)/[^\s]+|"
    r"tg://[^\s]+|"
    r"\b[\w-]+\.(?:com|net|org|me|in|co|io|xyz|"
    r"site|online|live|shop|dev|app|store|pro|"
    r"tech|info|biz|cc|tv)\b)",
    re.IGNORECASE
)

# ================= PRIVATE START =================

@app.on_message(
    filters.private & filters.command("start"),
    group=0
)
async def private_start(client, message):
    try:
        await message.reply_text(
            START_TEXT,
            reply_markup=home_keyboard(),
            disable_web_page_preview=True
        )
        log.info(
            "PRIVATE START OK | user=%s",
            message.from_user.id if message.from_user else "unknown"
        )
    except Exception as e:
        log.exception("PRIVATE START ERROR: %s", e)

# ================= GROUP START =================

@app.on_message(
    filters.group & filters.command("start"),
    group=0
)
async def group_start(client, message):
    try:
        await message.reply_text(
            START_TEXT,
            reply_markup=home_keyboard(),
            disable_web_page_preview=True
        )
    except Exception as e:
        log.exception("GROUP START ERROR: %s", e)

# ================= CALLBACK =================

@app.on_callback_query()
async def callbacks(client, query):
    try:
        if query.data == "about":
            await query.message.edit_text(
                ABOUT_TEXT,
                reply_markup=about_keyboard()
            )

        elif query.data == "help":
            await query.message.edit_text(
                HELP_TEXT,
                reply_markup=help_keyboard()
            )

        elif query.data == "back":
            await query.message.edit_text(
                START_TEXT,
                reply_markup=home_keyboard()
            )

        await query.answer()

    except Exception:
        try:
            await query.answer(
                "Unable to update.",
                show_alert=True
            )
        except Exception:
            pass

# ================= PING =================

@app.on_message(filters.command("ping"))
async def ping(client, message):
    try:
        start = time.perf_counter()

        temp = await message.reply_text(
            "<b>ᴘɪɴɢɪɴɢ... ❤️‍🔥</b>"
        )

        ms = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        uptime = int(time.time() - START_TIME)
        days, rem = divmod(uptime, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

        try:
            await temp.delete()
        except Exception:
            pass

        await message.reply_text(
            f"""<b>ʜєʏ ʙᴧʙʏ !!

𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨 ɪs ᴧʟɪᴠє 🥀

➥ ᴘɪɴɢ : {ms} ms
➥ ᴜᴘᴛɪᴍᴇ : {days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}s

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>"""
        )

    except Exception as e:
        log.warning("PING ERROR: %s", e)

# ================= STATS =================

@app.on_message(filters.command("stats"))
async def bot_stats(client, message):
    await message.reply_text(
        f"""<b>✦ ʙᴏᴛ sᴛᴀᴛs

» ᴍᴇssᴀɢᴇs ᴄʜᴇᴄᴋᴇᴅ : {get_stat("messages")}
» ʙɪᴏ ʟɪɴᴋs ғᴏᴜɴᴅ : {get_stat("bio_links")}
» ᴍᴇssᴀɢᴇs ᴅᴇʟᴇᴛᴇᴅ : {get_stat("deleted")}

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>"""
    )

# ================= AUTH =================

@app.on_message(filters.command("auth") & filters.group)
async def auth_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs.")

    target = (
        message.reply_to_message.from_user
        if message.reply_to_message else None
    )

    if not target:
        return await message.reply_text(
            "↪️ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ."
        )

    auth_users.update_one(
        {
            "chat_id": message.chat.id,
            "user_id": target.id
        },
        {
            "$set": {
                "name": target.first_name or "User"
            }
        },
        upsert=True
    )

    await message.reply_text(
        f"✅ <b>{target.first_name}</b> ᴀᴜᴛʜᴏʀɪᴢᴇᴅ."
    )

@app.on_message(filters.command("unauth") & filters.group)
async def unauth_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    target = (
        message.reply_to_message.from_user
        if message.reply_to_message else None
    )

    if not target:
        return await message.reply_text(
            "↪️ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ."
        )

    auth_users.delete_one({
        "chat_id": message.chat.id,
        "user_id": target.id
    })

    await message.reply_text(
        "✅ ᴜsᴇʀ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ."
    )

@app.on_message(filters.command("authusers") & filters.group)
async def auth_users_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    users = list(auth_users.find({
        "chat_id": message.chat.id
    }))

    if not users:
        return await message.reply_text(
            "❌ ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs."
        )

    text = "<b>✦ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs\n\n"

    for user in users:
        text += (
            f"• {user.get('name', 'User')} "
            f"<code>{user['user_id']}</code>\n"
        )

    await message.reply_text(text + "</b>")

@app.on_message(
    filters.command("clearauthusers") & filters.group
)
async def clear_auth(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    auth_users.delete_many({
        "chat_id": message.chat.id
    })

    await message.reply_text(
        "✅ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴄʟᴇᴀʀᴇᴅ."
    )

# ================= RESET WARN =================

@app.on_message(
    filters.command("resetwarn") & filters.group
)
async def reset_warn(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return

    target = (
        message.reply_to_message.from_user
        if message.reply_to_message else None
    )

    if not target:
        return await message.reply_text(
            "↪️ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ."
        )

    set_warn(message.chat.id, target.id, 0)

    await message.reply_text(
        "✅ ᴡᴀʀɴɪɴɢ ʀᴇsᴇᴛ."
    )

# ================= BIO MODERATION =================

@app.on_message(
    filters.group & ~filters.service,
    group=10
)
async def bio_checker(client, message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Don't moderate admins
    if await is_admin(chat_id, user_id):
        return

    # Don't moderate authorized users
    if is_auth(chat_id, user_id):
        return

    increment("messages")

    bio = await get_bio(user_id)

    if not bio or not LINK_RE.search(bio):
        return

    increment("bio_links")

    # Delete message
    try:
        await message.delete()
        increment("deleted")
    except Exception as e:
        log.warning("DELETE ERROR: %s", e)
        return

    count = get_warn(chat_id, user_id) + 1

    # Mute on limit
    if count >= WARN_LIMIT:
        try:
            await client.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(),
                until_date=int(time.time()) + MUTE_MINUTES * 60
            )

            set_warn(chat_id, user_id, 0)

            await client.send_message(
                chat_id,
                f"""🔇 <b>{message.from_user.first_name}</b>

ʙɪᴏ ᴍᴇ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ.
ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ ᴄᴏᴍᴘʟᴇᴛᴇ.

➥ ᴍᴜᴛᴇ : {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs"""
            )

        except Exception as e:
            log.warning("MUTE ERROR: %s", e)

    else:
        set_warn(chat_id, user_id, count)

        try:
            await client.send_message(
                chat_id,
                f"""⚠️ <b>{message.from_user.first_name}</b>

ʙɪᴏ ᴍᴇ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ.

➥ ᴡᴀʀɴɪɴɢ : {count}/{WARN_LIMIT}"""
            )
        except Exception as e:
            log.warning("WARN MESSAGE ERROR: %s", e)

# ================= LOGGER =================

async def startup_log():
    if not LOGGER_ID:
        return

    try:
        me = await app.get_me()

        await app.send_message(
            LOGGER_ID,
            f"""<b>❖ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ

🟢 ʙᴏᴛ : @{me.username or me.id}

» ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ : 🟢
» ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇʀ : 🟢
» ᴡᴀʀɴɪɴɢ sʏsᴛᴇᴍ : 🟢
» ᴀᴜᴛᴏ ᴍᴜᴛᴇ : 🟢

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>"""
        )

    except Exception as e:
        log.warning("LOGGER ERROR: %s", e)

# ================= RUN =================

async def main():
    await app.start()

    me = await app.get_me()

    log.info(
        "BOT STARTED: @%s",
        me.username or me.id
    )

    await startup_log()

    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
