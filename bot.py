# ============================================================
# BIO LINK CLEANER BOT
# ============================================================

import os
import re
import sys
import time
import asyncio
import logging

from pymongo import MongoClient

# ============================================================
# PYROGRAM PEER-ID FIX
# Fixes: ValueError: Peer id invalid: -100xxxxxxxxxx
# ============================================================

import pyrogram.utils as pyrogram_utils


def fixed_get_peer_type(peer_id):
    peer_id = str(peer_id)

    if peer_id.startswith("-100"):
        return "channel"

    if peer_id.startswith("-"):
        return "chat"

    return "user"


pyrogram_utils.get_peer_type = fixed_get_peer_type


from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError, FloodWait
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
)


# ============================================================
# CONFIG
# ============================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")

BOT_USERNAME = os.getenv(
    "BOT_USERNAME",
    "Radhaprobot"
).lstrip("@")

SUPPORT_URL = os.getenv(
    "SUPPORT_URL",
    "https://t.me/annu_support"
)

UPDATE_URL = os.getenv(
    "UPDATE_URL",
    "https://t.me/annu_updates"
)

OWNER_URL = os.getenv(
    "OWNER_URL",
    "https://t.me/"
)

PROMO_URL = os.getenv(
    "PROMO_URL",
    "https://t.me/annu_updates"
)

START_IMAGE_PATH = os.getenv(
    "START_IMAGE_PATH",
    "https://h.uguu.se/FekWWcsz.jpg"
)

PING_IMAGE_PATH = os.getenv(
    "PING_IMAGE_PATH",
    "https://h.uguu.se/FekWWcsz.jpg"
)

WARN_LIMIT = int(
    os.getenv("WARN_LIMIT", "3")
)

MUTE_MINUTES = int(
    os.getenv("MUTE_MINUTES", "60")
)

LOGGER_GROUP_ID_RAW = os.getenv(
    "LOGGER_GROUP_ID",
    "-1003979103138"
).strip()

try:
    LOGGER_GROUP_ID = int(LOGGER_GROUP_ID_RAW)
except (ValueError, TypeError):
    LOGGER_GROUP_ID = 0

PLUGIN_COUNT = int(
    os.getenv("PLUGIN_COUNT", "15")
)

LOGGER_BOT_NAME = os.getenv(
    "LOGGER_BOT_NAME",
    "kirti 🐒"
)

LOGGER_POWERED_BY = os.getenv(
    "LOGGER_POWERED_BY",
    "kirti-BOTS"
)

BOT_START_TIME = time.time()


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)

log = logging.getLogger(
    "BIO-LINK-CLEANER"
)


# ============================================================
# ENV CHECK
# ============================================================

if not API_ID:
    raise RuntimeError("API_ID is missing.")

if not API_HASH:
    raise RuntimeError("API_HASH is missing.")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing.")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is missing.")

if WARN_LIMIT < 1:
    raise RuntimeError("WARN_LIMIT must be at least 1.")

if MUTE_MINUTES < 1:
    raise RuntimeError("MUTE_MINUTES must be at least 1.")


# ============================================================
# APP
# ============================================================

app = Client(
    "biolink_cleaner",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ============================================================
# MONGO
# ============================================================

mongo = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000
)

db = mongo["bio_link_cleaner"]

groups = db["groups"]
auth_users = db["auth_users"]
warnings = db["warnings"]
stats = db["stats"]


# ============================================================
# START TEXT
# ============================================================

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


# ============================================================
# ABOUT
# ============================================================

ABOUT_TEXT = """
<b>─────────────────────────

❖ ᴀ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ ʙᴏᴛ ғᴏʀ ɢʀᴏᴜᴘs.

─────────────────────────

● ᴡʀɪᴛᴛєη ɪη » ᴩʏᴛʜση
● ᴅᴧᴛᴧʙᴧsє » ϻᴏηɢᴏ-ᴅʙ
● ʜєʟᴘ ᴡɪᴛʜ » ᴘʏʀσɢʀᴧϻ

─────────────────────────

➥ ɪ ᴄᴀɴ ᴇᴀsɪʟʏ ᴍᴀɪɴᴛᴀɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.
➥ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴡɪᴛʜ ᴅᴇʟᴇᴛᴇ & ʙᴀɴ ʀɪɢʜᴛs.
➥ ᴧᴅᴅ ϻє ηᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs.

─────────────────────────

❖ υᴘᴅᴧᴛєs ᴄʜᴧηηєʟ ➥ ᴘᴜʀᴠɪ-ʙᴏᴛꜱ
❖ sυᴘᴘσʀᴛ ᴄʜᴧᴛ ➥ ᴘᴜʀᴠɪ-ᴜᴘᴅᴀᴛᴇs

─────────────────────────

➤ ʙσᴛ sᴛᴧᴛυs & ϻσʀє ʙσᴛs - ᴄʟɪᴄᴋ ʜєʀє
➤ ᴘᴧɪᴅ ᴘʀσϻσᴛɪση :- ᴄσηᴛᴧᴄᴛ ʜєʀє

─────────────────────────</b>
"""


# ============================================================
# HELP
# ============================================================

HELP_TEXT = """
<b>❖ ʜᴇʀᴇ ɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ ʙᴏᴛ.

⊚ ᴀʟʟ ᴜsᴇʀs ᴄᴏᴍᴍᴀɴᴅs :

/start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.
/ping - ᴄʜᴇᴄᴋ ʙᴏᴛ ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ.
/stats - sʜᴏᴡ ʙᴏᴛ sᴛᴀᴛs.

⊚ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ :

/auth - ᴀᴜᴛʜᴏʀɪᴢᴇ ᴀ ᴜsᴇʀ.
/unauth - ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ ᴀ ᴜsᴇʀ.
/authusers - sʜᴏᴡ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs.
/clearauthusers - ᴄʟᴇᴀʀ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs.
/resetwarn - ʀᴇsᴇᴛ ᴡᴀʀɴɪɴɢ.

━━━━━━━━━━━━━━━━━━

⊚ ᴡᴀʀɴɪɴɢ sʏsᴛᴇᴍ :

1st ᴡᴀʀɴɪɴɢ
2nd ᴡᴀʀɴɪɴɢ
3rd ᴡᴀʀɴɪɴɢ ➜ ᴀᴜᴛᴏ ᴍᴜᴛᴇ

━━━━━━━━━━━━━━━━━━

➻ ɴᴏᴛᴇ :

ʙᴏᴛ ᴇᴠᴇʀʏ ᴛɪᴍᴇ
ʙɪᴏ ʟɪɴᴋ ᴡᴀʟᴇ ᴜsᴇʀ ᴋᴀ
ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇ ᴋᴀʀᴇɢᴀ.

✦ 𝐏ᴏᴡᴇʀᴇᴅ вʏ » ᴘᴜʀᴠɪ-ʙᴏᴛꜱ</b>
"""


# ============================================================
# KEYBOARDS
# ============================================================

def start_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⊞ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⊞",
                url=(
                    f"https://t.me/{BOT_USERNAME}"
                    f"?startgroup=true"
                )
            )
        ],
        [
            InlineKeyboardButton(
                "≡ ᴏᴡɴᴇʀ ≡",
                url=OWNER_URL
            ),
            InlineKeyboardButton(
                "≡ ᴀʙᴏᴜᴛ ≡",
                callback_data="about"
            )
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
            InlineKeyboardButton(
                "≡ sᴜᴘᴘᴏʀᴛ ≡",
                url=SUPPORT_URL
            ),
            InlineKeyboardButton(
                "≡ ᴜᴘᴅᴀᴛᴇ ≡",
                url=UPDATE_URL
            )
        ],
        [
            InlineKeyboardButton(
                "≡ ʙᴀᴄᴋ ≡",
                callback_data="back"
            )
        ]
    ])


def help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "≡ sᴜᴘᴘᴏʀᴛ ≡",
                url=SUPPORT_URL
            ),
            InlineKeyboardButton(
                "≡ ʙᴀᴄᴋ ≡",
                callback_data="back"
            )
        ]
    ])


def warning_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✚ ᴀᴅᴅ ᴍᴇ",
                url=(
                    f"https://t.me/{BOT_USERNAME}"
                    f"?startgroup=true"
                )
            ),
            InlineKeyboardButton(
                "👥 sᴜᴘᴘᴏʀᴛ",
                url=SUPPORT_URL
            )
        ]
    ])


# ============================================================
# LINK DETECTOR
# ============================================================

LINK_PATTERNS = [
    r"https?://[^\s]+",
    r"www\.[^\s]+\.[a-z]{2,}",
    r"(?:t\.me|telegram\.me|telegram\.dog)/[^\s]+",
    r"tg://[^\s]+",
    (
        r"\b[a-z0-9-]+\."
        r"(?:com|net|org|me|in|co|io|xyz|site|online|"
        r"live|shop|dev|app|store|pro|tech|info|biz|cc|tv)\b"
    ),
]


def has_bio_link(bio):
    if not bio:
        return False

    return any(
        re.search(
            pattern,
            str(bio),
            re.IGNORECASE
        )
        for pattern in LINK_PATTERNS
    )


# ============================================================
# BIO FETCH
# ============================================================

async def get_user_bio(client, user_id):
    try:
        chat = await client.get_chat(user_id)

        bio = getattr(chat, "bio", None)
        bio = str(bio).strip() if bio else ""

        log.info(
            "BIO FETCH | user=%s | bio=%r",
            user_id,
            bio
        )

        return bio

    except FloodWait as e:
        log.warning(
            "BIO FLOODWAIT | user=%s | wait=%s",
            user_id,
            e.value
        )
        await asyncio.sleep(e.value)
        return await get_user_bio(client, user_id)

    except RPCError as e:
        log.warning(
            "BIO RPC ERROR | user=%s | %s",
            user_id,
            e
        )

    except Exception as e:
        log.warning(
            "BIO FETCH ERROR | user=%s | %s",
            user_id,
            e
        )

    return ""


# ============================================================
# ADMIN / OWNER
# ============================================================

async def is_admin_or_owner(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(
            chat_id,
            user_id
        )

        status = member.status

        if status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        ):
            return True

        value = str(
            getattr(status, "value", status)
        ).lower()

        return value in (
            "owner",
            "administrator",
            "creator"
        )

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await is_admin_or_owner(
            client,
            chat_id,
            user_id
        )

    except Exception as e:
        log.warning(
            "ADMIN CHECK ERROR | %s",
            e
        )
        return False


async def can_manage(client, message):
    if not message.from_user:
        return False

    return await is_admin_or_owner(
        client,
        message.chat.id,
        message.from_user.id
    )


# ============================================================
# DATABASE
# ============================================================

def inc_stat(key, amount=1):
    try:
        stats.update_one(
            {"_id": key},
            {"$inc": {"value": amount}},
            upsert=True
        )
    except Exception as e:
        log.warning(
            "STATS ERROR | %s",
            e
        )


def get_stat(key):
    try:
        data = stats.find_one({"_id": key})

        if not data:
            return 0

        return int(data.get("value", 0))

    except Exception:
        return 0


def get_warn(chat_id, user_id):
    try:
        data = warnings.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        })

        return int(
            data.get("count", 0)
        ) if data else 0

    except Exception:
        return 0


def set_warn(chat_id, user_id, count):
    try:
        warnings.update_one(
            {
                "chat_id": chat_id,
                "user_id": user_id
            },
            {
                "$set": {
                    "count": count
                }
            },
            upsert=True
        )
    except Exception as e:
        log.warning(
            "WARNING DB ERROR | %s",
            e
        )


def is_authorized(chat_id, user_id):
    try:
        return (
            auth_users.find_one({
                "chat_id": chat_id,
                "user_id": user_id
            }) is not None
        )
    except Exception:
        return False


# ============================================================
# TARGET USER
# ============================================================

async def get_target(message):
    try:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user
        ):
            return message.reply_to_message.from_user

        if len(message.command) > 1:
            target = message.command[1].strip()

            if target.lstrip("-").isdigit():
                return await app.get_users(
                    int(target)
                )

            return await app.get_users(target)

    except Exception as e:
        log.warning(
            "TARGET ERROR | %s",
            e
        )

    return None


# ============================================================
# TELEGRAM LOGGER
# ============================================================

async def send_log(text):
    try:
        clean_text = re.sub(
            r"<[^>]+>",
            "",
            text
        )

        log.info(
            "TELEGRAM LOG | %s",
            clean_text
        )
    except Exception:
        pass

    if not LOGGER_GROUP_ID:
        return

    try:
        await app.send_message(
            LOGGER_GROUP_ID,
            text,
            disable_web_page_preview=True
        )

    except FloodWait as e:
        log.warning(
            "LOGGER FLOODWAIT | %s seconds",
            e.value
        )

    except Exception as e:
        log.warning(
            "TELEGRAM LOGGER ERROR | %s",
            e
        )


# ============================================================
# STARTUP LOGGER
# ============================================================

async def send_startup_log():
    if not LOGGER_GROUP_ID:
        log.warning(
            "LOGGER_GROUP_ID is not configured."
        )
        return

    try:
        # Resolve/check logger peer before sending.
        logger_chat = await app.get_chat(
            LOGGER_GROUP_ID
        )

        me = await app.get_me()

        bot_display_name = (
            LOGGER_BOT_NAME
            or (
                f"@{me.username}"
                if me.username
                else me.first_name or "Bot"
            )
        )

        try:
            import pyrogram
            pyrogram_version = pyrogram.__version__
        except Exception:
            pyrogram_version = "Unknown"

        python_version = (
            f"{sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )

        startup_text = f"""
<b>❖ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ

🟢 {bot_display_name}

• ʙᴏᴛ : @{me.username or me.id} 🐒
• ᴘʟᴜɢɪɴs : {PLUGIN_COUNT} ʟᴏᴀᴅᴇᴅ
• ᴘʏʀᴏɢʀᴀᴍ : {pyrogram_version}
• ᴘʏᴛʜᴏɴ : {python_version}

━━━━━━━━━━━━━━━━━━

» ᴡᴀʀɴ ʟɪᴍɪᴛ : {WARN_LIMIT}
» ᴍᴜᴛᴇ : {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs

» ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ : 🟢
» ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇʀ : 🟢
» ᴡᴀʀɴɪɴɢ sʏsᴛᴇᴍ : 🟢
» ᴀᴜᴛᴏ ᴍᴜᴛᴇ : 🟢
» ʟᴏɢɢᴇʀ : 🟢

━━━━━━━━━━━━━━━━━━

» ᴘᴏᴡᴇʀᴇᴅ ʙʏ : {LOGGER_POWERED_BY}</b>
"""

        await app.send_photo(
            chat_id=logger_chat.id,
            photo=START_IMAGE_PATH,
            caption=startup_text
        )

        log.info(
            "STARTUP LOGGER SENT | chat=%s",
            logger_chat.id
        )

    except FloodWait as e:
        log.warning(
            "STARTUP LOGGER FLOODWAIT | %s",
            e.value
        )
        await asyncio.sleep(e.value)

        # Retry once after FloodWait.
        try:
            await send_startup_log()
        except Exception as retry_error:
            log.warning(
                "STARTUP LOGGER RETRY FAILED | %s",
                retry_error
            )

    except Exception as e:
        # Logger failure must NOT crash the bot.
        log.exception(
            "STARTUP LOGGER FAILED | %s",
            e
        )


# ============================================================
# START COMMAND
# ============================================================

@app.on_message(
    filters.command("start") & filters.private
)
async def start_private(_, message):
    try:
        await message.reply_photo(
            photo=START_IMAGE_PATH,
            caption=START_TEXT,
            reply_markup=start_keyboard()
        )
    except Exception as e:
        log.warning(
            "START IMAGE FAILED | %s",
            e
        )

        await message.reply_text(
            START_TEXT,
            reply_markup=start_keyboard(),
            disable_web_page_preview=True
        )


@app.on_message(
    filters.command("start") & filters.group
)
async def start_group(_, message):
    try:
        await message.reply_photo(
            photo=START_IMAGE_PATH,
            caption=START_TEXT,
            reply_markup=start_keyboard()
        )
    except Exception as e:
        log.warning(
            "GROUP START IMAGE FAILED | %s",
            e
        )

        await message.reply_text(
            START_TEXT,
            reply_markup=start_keyboard(),
            disable_web_page_preview=True
        )


# ============================================================
# CALLBACKS
# ============================================================

@app.on_callback_query()
async def callbacks(_, query):
    try:
        if query.data == "about":
            await query.message.edit_text(
                ABOUT_TEXT,
                reply_markup=about_keyboard(),
                disable_web_page_preview=True
            )

        elif query.data == "help":
            await query.message.edit_text(
                HELP_TEXT,
                reply_markup=help_keyboard(),
                disable_web_page_preview=True
            )

        elif query.data == "back":
            await query.message.edit_text(
                START_TEXT,
                reply_markup=start_keyboard(),
                disable_web_page_preview=True
            )

        await query.answer()

    except Exception:
        try:
            await query.answer(
                "Unable to update message.",
                show_alert=True
            )
        except Exception:
            pass


# ============================================================
# PING
# ============================================================

@app.on_message(filters.command("ping"))
async def ping(_, message):
    try:
        started = time.perf_counter()

        temp = await message.reply_text(
            "<b>ᴘɪɴɢɪɴɢ... ❤️‍🔥</b>"
        )

        ping_ms = round(
            (
                time.perf_counter() - started
            ) * 1000,
            2
        )

        uptime = int(
            time.time() - BOT_START_TIME
        )

        days, remainder = divmod(
            uptime,
            86400
        )
        hours, remainder = divmod(
            remainder,
            3600
        )
        minutes, seconds = divmod(
            remainder,
            60
        )

        uptime_text = (
            f"{days}ᴅ:{hours}ʜ:{minutes}ᴍ:{seconds}s"
            if days
            else
            f"{hours}ʜ:{minutes}ᴍ:{seconds}s"
        )

        text = f"""
<b>ʜєʏ ʙᴧʙʏ !!

𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨 ɪꜱ ᴧʟɪᴠє 🥀 ᴧηᴅ
ᴡσʀᴋɪηɢ ꜰɪηє ᴡɪᴛʜ

➥ ᴘσηɢ : {ping_ms} ms
➥ ᴜᴘᴛɪϻє : {uptime_text}

✦ 𝐏σᴡєʀєᴅ вʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

        try:
            await temp.delete()
        except Exception:
            pass

        await message.reply_photo(
            photo=PING_IMAGE_PATH,
            caption=text
        )

    except Exception as e:
        log.warning(
            "PING ERROR | %s",
            e
        )


# ============================================================
# STATS
# ============================================================

@app.on_message(filters.command("stats"))
async def bot_stats(_, message):
    text = f"""
<b>✦ ʙᴏᴛ sᴛᴀᴛs

» ᴍᴇssᴀɢᴇs ᴄʜᴇᴄᴋᴇᴅ :
{get_stat("messages_checked")}

» ʙɪᴏ ʟɪɴᴋs ғᴏᴜɴᴅ :
{get_stat("bio_links")}

» ᴍᴇssᴀɢᴇs ᴅᴇʟᴇᴛᴇᴅ :
{get_stat("messages_deleted")}

» ᴡᴀʀɴɪɴɢs :
{get_stat("warnings")}

» ᴍᴜᴛᴇs :
{get_stat("mutes")}</b>
"""

    await message.reply_text(text)


# ============================================================
# AUTH
# ============================================================

@app.on_message(
    filters.command("auth") & filters.group
)
async def auth_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    target = await get_target(message)

    if not target:
        return await message.reply_text(
            "<b>» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴜsᴇ "
            "/auth user_id</b>"
        )

    auth_users.update_one(
        {
            "chat_id": message.chat.id,
            "user_id": target.id
        },
        {
            "$set": {
                "name": target.first_name or "",
                "username": target.username or ""
            }
        },
        upsert=True
    )

    await message.reply_text(
        f"<b>✅ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ : "
        f"{target.mention}</b>"
    )

    await send_log(
        f"""
<b>🔐 ᴀᴜᴛʜ ʟᴏɢ

👥 ɢʀᴏᴜᴘ : {message.chat.title or "Unknown"}
🆔 ɢʀᴏᴜᴘ ɪᴅ : <code>{message.chat.id}</code>

👤 ᴜsᴇʀ : {target.mention}
🆔 ᴜsᴇʀ ɪᴅ : <code>{target.id}</code>

ᴀᴄᴛɪᴏɴ : ᴜsᴇʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ</b>
"""
    )


# ============================================================
# UNAUTH
# ============================================================

@app.on_message(
    filters.command("unauth") & filters.group
)
async def unauth_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    target = await get_target(message)

    if not target:
        return await message.reply_text(
            "<b>» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴜsᴇ "
            "/unauth user_id</b>"
        )

    result = auth_users.delete_one({
        "chat_id": message.chat.id,
        "user_id": target.id
    })

    if result.deleted_count:
        text = (
            f"<b>✅ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ : "
            f"{target.mention}</b>"
        )
    else:
        text = (
            "<b>⚠️ ᴜsᴇʀ ᴡᴀs ɴᴏᴛ "
            "ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.</b>"
        )

    await message.reply_text(text)


# ============================================================
# AUTH USERS
# ============================================================

@app.on_message(
    filters.command("authusers") & filters.group
)
async def authusers_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    rows = list(
        auth_users.find({
            "chat_id": message.chat.id
        }).limit(50)
    )

    if not rows:
        return await message.reply_text(
            "<b>» ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ "
            "ᴜsᴇʀs ғᴏᴜɴᴅ.</b>"
        )

    lines = [
        "<b>◎ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs :</b>",
        ""
    ]

    for i, row in enumerate(rows, 1):
        username = row.get("username")

        name = (
            f"@{username}"
            if username
            else row.get("name", "User")
        )

        lines.append(
            f"<b>{i}. {name} "
            f"<code>{row.get('user_id')}</code></b>"
        )

    await message.reply_text(
        "\n".join(lines)
    )


# ============================================================
# CLEAR AUTH USERS
# ============================================================

@app.on_message(
    filters.command("clearauthusers") & filters.group
)
async def clearauthusers_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    result = auth_users.delete_many({
        "chat_id": message.chat.id
    })

    await message.reply_text(
        f"<b>✅ ʀᴇᴍᴏᴠᴇᴅ "
        f"{result.deleted_count} "
        f"ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ(s).</b>"
    )


# ============================================================
# MUTE
# ============================================================

async def mute_user(
    chat_id,
    user_id,
    minutes
):
    try:
        until_date = (
            int(time.time())
            + minutes * 60
        )

        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False
            ),
            until_date=until_date
        )

        return True

    except FloodWait as e:
        log.warning(
            "MUTE FLOODWAIT | %s seconds",
            e.value
        )
        await asyncio.sleep(e.value)

        return await mute_user(
            chat_id,
            user_id,
            minutes
        )

    except RPCError as e:
        log.warning(
            "MUTE RPC ERROR | %s",
            e
        )

    except Exception as e:
        log.warning(
            "MUTE ERROR | %s",
            e
        )

    return False


# ============================================================
# BIO LINK CHECKER
# Every offending message is deleted.
# 3 warnings => mute.
# ============================================================

@app.on_message(
    filters.group
    & (
        filters.text
        | filters.caption
    )
)
async def bio_link_checker(_, message):
    try:
        if not message.from_user:
            return

        user = message.from_user

        if user.is_bot:
            return

        chat_id = message.chat.id
        user_id = user.id

        inc_stat("messages_checked")

        log.info(
            "CHECK | group=%s | user=%s | msg=%s",
            chat_id,
            user_id,
            message.id
        )

        # Admin / owner bypass
        if await is_admin_or_owner(
            app,
            chat_id,
            user_id
        ):
            log.info(
                "ADMIN BYPASS | user=%s",
                user_id
            )
            return

        # Authorized user bypass
        if is_authorized(
            chat_id,
            user_id
        ):
            log.info(
                "AUTH BYPASS | user=%s",
                user_id
            )
            return

        # Fetch bio
        bio = await get_user_bio(
            app,
            user_id
        )

        if not has_bio_link(bio):
            return

        inc_stat("bio_links")

        log.warning(
            "BIO LINK FOUND | group=%s | user=%s | msg=%s",
            chat_id,
            user_id,
            message.id
        )

        # ----------------------------------------------------
        # DELETE THIS MESSAGE EVERY TIME
        # ----------------------------------------------------

        deleted = False

        try:
            await message.delete()
            deleted = True

            inc_stat("messages_deleted")

            log.info(
                "MESSAGE DELETED | group=%s | user=%s | msg=%s",
                chat_id,
                user_id,
                message.id
            )

        except FloodWait as e:
            log.warning(
                "DELETE FLOODWAIT | %s seconds",
                e.value
            )

            await asyncio.sleep(e.value)

            try:
                await message.delete()
                deleted = True

                inc_stat("messages_deleted")

            except Exception as retry_error:
                log.warning(
                    "DELETE RETRY FAILED | %s",
                    retry_error
                )

        except Exception as e:
            log.warning(
                "MESSAGE DELETE ERROR | %s",
                e
            )

        # ----------------------------------------------------
        # WARNING COUNT
        # ----------------------------------------------------

        current_warn = get_warn(
            chat_id,
            user_id
        )

        new_warn = current_warn + 1

        # ----------------------------------------------------
        # 3 WARNINGS => MUTE
        # ----------------------------------------------------

        if new_warn >= WARN_LIMIT:

            muted = await mute_user(
                chat_id,
                user_id,
                MUTE_MINUTES
            )

            if muted:
                inc_stat("warnings")
                inc_stat("mutes")

                # Reset only after successful mute.
                set_warn(
                    chat_id,
                    user_id,
                    0
                )

                log.warning(
                    "USER MUTED | group=%s | user=%s | %s min",
                    chat_id,
                    user_id,
                    MUTE_MINUTES
                )

                await send_log(
                    f"""
<b>🔇 ᴍᴜᴛᴇ ʟᴏɢ

👥 ɢʀᴏᴜᴘ : {message.chat.title or "Unknown"}
🆔 ɢʀᴏᴜᴘ ɪᴅ : <code>{chat_id}</code>

👤 ᴜsᴇʀ : {user.mention}
🆔 ᴜsᴇʀ ɪᴅ : <code>{user_id}</code>

⚠️ ᴡᴀʀɴɪɴɢ : {WARN_LIMIT}/{WARN_LIMIT}
🔇 ᴀᴄᴛɪᴏɴ : ᴍᴜᴛᴇᴅ
⏱ ᴅᴜʀᴀᴛɪᴏɴ : {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs

🔗 ʙɪᴏ :
<code>{bio}</code></b>
"""
                )

                try:
                    await app.send_message(
                        chat_id,
                        f"""
<b>🚨 ʙɪᴏ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ !!

👤 ᴜsᴇʀ : {user.mention}

⚠️ ᴡᴀʀɴɪɴɢ : {WARN_LIMIT}/{WARN_LIMIT}

🔇 ᴜsᴇʀ ᴍᴜᴛᴇᴅ !!

⏱ ᴍᴜᴛᴇ : {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs

❌ ʟɪɴᴋ ᴡᴀʟᴇ ʙɪᴏ ᴀʟʟᴏᴡᴇᴅ ɴᴀʜɪ ʜᴀɪ.</b>
""",
                        reply_markup=warning_keyboard()
                    )
                except Exception as e:
                    log.warning(
                        "MUTE MESSAGE ERROR | %s",
                        e
                    )

            else:
                # If mute failed, keep the warning at limit
                # so next offending message retries mute.
                set_warn(
                    chat_id,
                    user_id,
                    new_warn
                )

                inc_stat("warnings")

                log.error(
                    "MUTE FAILED | group=%s | user=%s",
                    chat_id,
                    user_id
                )

                await send_log(
                    f"""
<b>❌ ᴍᴜᴛᴇ ғᴀɪʟᴇᴅ

👥 ɢʀᴏᴜᴘ : {message.chat.title or "Unknown"}
🆔 ɢʀᴏᴜᴘ ɪᴅ : <code>{chat_id}</code>

👤 ᴜsᴇʀ : {user.mention}
🆔 ᴜsᴇʀ ɪᴅ : <code>{user_id}</code>

⚠️ ᴡᴀʀɴɪɴɢ : {new_warn}/{WARN_LIMIT}

❗ ʙᴏᴛ ᴋᴏ ᴍᴜᴛᴇ
ᴘᴇʀᴍɪssɪᴏɴ ᴅᴇɴ.</b>
"""
                )

            return

        # ----------------------------------------------------
        # NORMAL WARNING
        # ----------------------------------------------------

        set_warn(
            chat_id,
            user_id,
            new_warn
        )

        inc_stat("warnings")

        log.warning(
            "WARNING | group=%s | user=%s | %s/%s",
            chat_id,
            user_id,
            new_warn,
            WARN_LIMIT
        )

        await send_log(
            f"""
<b>⚠️ ᴡᴀʀɴɪɴɢ ʟᴏɢ

👥 ɢʀᴏᴜᴘ : {message.chat.title or "Unknown"}
🆔 ɢʀᴏᴜᴘ ɪᴅ : <code>{chat_id}</code>

👤 ᴜsᴇʀ : {user.mention}
🆔 ᴜsᴇʀ ɪᴅ : <code>{user_id}</code>

🚨 ᴡᴀʀɴɪɴɢ : {new_warn}/{WARN_LIMIT}

🗑 ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ :
{"ʏᴇs" if deleted else "ɴᴏ"}</b>
"""
        )

        try:
            await app.send_message(
                chat_id,
                f"""
<b>⚠️ ʙɪᴏ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ !!

👤 ᴜsᴇʀ : {user.mention}

🚨 ᴡᴀʀɴɪɴɢ : {new_warn}/{WARN_LIMIT}

❌ ʟɪɴᴋs ɪɴ ʙɪᴏ ᴀʟʟᴏᴡᴇᴅ ɴᴀʜɪ ʜᴀɪ.

⚠️ {WARN_LIMIT} ᴡᴀʀɴɪɴɢs ᴋᴇ ʙᴀᴅ
ᴜsᴇʀ ᴋᴏ ᴀᴜᴛᴏ ᴍᴜᴛᴇ ᴋɪʏᴀ ᴊᴀʏᴇɢᴀ.</b>
""",
                reply_markup=warning_keyboard()
            )
        except Exception as e:
            log.warning(
                "WARNING MESSAGE ERROR | %s",
                e
            )

    except FloodWait as e:
        log.warning(
            "CHECKER FLOODWAIT | %s seconds",
            e.value
        )
        await asyncio.sleep(e.value)

    except Exception as e:
        log.exception(
            "BIO CHECKER ERROR | %s",
            e
        )


# ============================================================
# RESET WARNING
# ============================================================

@app.on_message(
    filters.command("resetwarn") & filters.group
)
async def reset_warn_cmd(_, message):
    if not await can_manage(app, message):
        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    target = await get_target(message)

    if not target:
        return await message.reply_text(
            "<b>» ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴜsᴇ "
            "/resetwarn user_id</b>"
        )

    set_warn(
        message.chat.id,
        target.id,
        0
    )

    await message.reply_text(
        f"<b>✅ ᴡᴀʀɴɪɴɢ ʀᴇsᴇᴛᴇᴅ ғᴏʀ "
        f"{target.mention}</b>"
    )

    await send_log(
        f"""
<b>♻️ ᴡᴀʀɴɪɴɢ ʀᴇsᴇᴛ

👥 ɢʀᴏᴜᴘ : {message.chat.title or "Unknown"}
🆔 ɢʀᴏᴜᴘ ɪᴅ : <code>{message.chat.id}</code>

👤 ᴜsᴇʀ : {target.mention}
🆔 ᴜsᴇʀ ɪᴅ : <code>{target.id}</code>

ᴀᴄᴛɪᴏɴ : ᴡᴀʀɴɪɴɢ ʀᴇsᴇᴛᴇᴅ</b>
"""
    )


# ============================================================
# MAIN
# ============================================================

async def main():
    log.info(
        "=================================================="
    )
    log.info(
        "STARTING BIO LINK CLEANER..."
    )

    await app.start()

    try:
        me = await app.get_me()

        log.info(
            "BOT ONLINE | @%s",
            me.username or me.id
        )

        log.info(
            "WARN LIMIT | %s",
            WARN_LIMIT
        )

        log.info(
            "MUTE MINUTES | %s",
            MUTE_MINUTES
        )

        log.info(
            "LOGGER GROUP | %s",
            LOGGER_GROUP_ID or "DISABLED"
        )

        await send_startup_log()

        log.info(
            "BIO LINK CLEANER IS READY."
        )

        log.info(
            "=================================================="
        )

        await idle()

    finally:
        log.info(
            "STOPPING BIO LINK CLEANER..."
        )

        try:
            await app.stop()
        except Exception:
            pass


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        log.info(
            "BOT STOPPED BY USER."
        )

    except Exception as e:
        log.exception(
            "FATAL ERROR | %s",
            e
        )
