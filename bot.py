# ============================================================
# BIO LINK CLEANER BOT
# ============================================================

import os
import re
import time
import asyncio
import logging

from pymongo import MongoClient

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError, FloodWait
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatPermissions,
)
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.raw.types import InputUser


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


# ============================================================
# PYROGRAM
# ============================================================

app = Client(
    "biolink_cleaner",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ============================================================
# MONGODB
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

❖ υᴘᴅᴧᴛєs ᴄʜᴧηηєʟ ➥ ᴘᴜʀᴠɪ-ʙᴏᴛs
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
/stats - ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛs.

⊚ ʜᴇʀᴇ ɪs ᴍᴀɪɴ ᴍᴏᴅᴜʟᴇs :

/auth - ᴀᴜᴛʜᴏʀɪᴢᴇ ᴀ ᴜsᴇʀ.
/unauth - ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇ ᴀ ᴜsᴇʀ.
/authusers - sʜᴏᴡ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs.
/clearauthusers - ʀᴇᴍᴏᴠᴇ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs.
/resetwarn - ʀᴇsᴇᴛ ᴛʜᴇ ᴡᴀʀɴɪɴɢ ᴄᴏᴜɴᴛ.

━━━━━━━━━━━━━━━━━━

⊚ ᴀᴅᴍɪɴ & ᴏᴡɴᴇʀ :

👑 ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ
» ᴀʟʟ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.

🛡 ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ
» ᴀʟʟ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.

━━━━━━━━━━━━━━━━━━

➻ ɴᴏᴛᴇ :- ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs
& ᴏɴʟʏ ᴜsᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs
ᴀɴᴅ ᴏᴡɴᴇʀs.

✦ 𝐏ᴏᴡᴇʀᴇᴅ вʏ » ᴀʟᴘʜᴀ-ʙᴀʙʏ</b>
"""


# ============================================================
# KEYBOARDS
# ============================================================

def start_keyboard():

    add_url = (
        f"https://t.me/{BOT_USERNAME}"
        "?startgroup=true"
    )

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⊞ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⊞",
                url=add_url
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

    add_url = (
        f"https://t.me/{BOT_USERNAME}"
        "?startgroup=true"
    )

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✚ ᴀᴅᴅ ᴍᴇ",
                url=add_url
            ),
            InlineKeyboardButton(
                "👥 sᴜᴘᴘᴏʀᴛ",
                url=SUPPORT_URL
            )
        ]
    ])


# ============================================================
# LINK DETECTION
# ============================================================

LINK_PATTERNS = [

    r"https?://[^\s]+",

    r"www\.[^\s]+\.[a-z]{2,}",

    r"(?:t\.me|telegram\.me|telegram\.dog)/[^\s]+",

    r"tg://[^\s]+",

    r"\b[a-z0-9-]+\."
    r"(?:com|net|org|me|in|co|io|xyz|"
    r"site|online|live|shop|dev|app|"
    r"store|pro|tech|info|biz|cc|tv)\b",

]


def has_bio_link(bio):

    if not bio:
        return False

    bio = str(bio).strip()

    for pattern in LINK_PATTERNS:

        if re.search(
            pattern,
            bio,
            re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# GET FULL USER / BIO
# ============================================================

async def get_user_bio(
    client,
    user_id
):

    try:

        # Get normal user first
        user = await client.get_users(
            user_id
        )

        if not user:
            return ""

        # Build InputUser
        input_user = InputUser(
            user_id=user.id,
            access_hash=user.access_hash
        )

        # Telegram Full User
        full_user = await client.invoke(
            GetFullUser(
                id=input_user
            )
        )

        bio = getattr(
            full_user.full_user,
            "about",
            None
        )

        if bio:
            return str(bio).strip()

    except FloodWait as e:

        log.warning(
            "Bio FloodWait: %s",
            e.value
        )

        await asyncio.sleep(
            e.value
        )

    except RPCError as e:

        log.warning(
            "GetFullUser failed for %s: %s",
            user_id,
            e
        )

    except Exception as e:

        log.warning(
            "Bio fetch error for %s: %s",
            user_id,
            e
        )

    return ""


# ============================================================
# ADMIN / OWNER
# ============================================================

async def is_admin_or_owner(
    client,
    chat_id,
    user_id
):

    try:

        member = await client.get_chat_member(
            chat_id,
            user_id
        )

        status = member.status

        if status == ChatMemberStatus.OWNER:
            return True

        if status == ChatMemberStatus.ADMINISTRATOR:
            return True

        status_value = str(
            getattr(
                status,
                "value",
                status
            )
        ).lower()

        return status_value in (
            "owner",
            "administrator",
            "creator"
        )

    except FloodWait as e:

        await asyncio.sleep(
            e.value
        )

        return await is_admin_or_owner(
            client,
            chat_id,
            user_id
        )

    except Exception as e:

        log.warning(
            "Admin check failed: %s",
            e
        )

        return False


async def can_manage(
    client,
    message
):

    if not message.from_user:
        return False

    return await is_admin_or_owner(
        client,
        message.chat.id,
        message.from_user.id
    )


# ============================================================
# DATABASE HELPERS
# ============================================================

def inc_stat(
    key,
    amount=1
):

    try:

        stats.update_one(
            {"_id": key},
            {
                "$inc": {
                    "value": amount
                }
            },
            upsert=True
        )

    except Exception as e:

        log.warning(
            "Stats error: %s",
            e
        )


def get_stat(key):

    try:

        data = stats.find_one(
            {"_id": key}
        )

        if data:
            return int(
                data.get(
                    "value",
                    0
                )
            )

    except Exception:
        pass

    return 0


def get_warn(
    chat_id,
    user_id
):

    try:

        data = warnings.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        })

        if data:
            return int(
                data.get(
                    "count",
                    0
                )
            )

    except Exception:
        pass

    return 0


def set_warn(
    chat_id,
    user_id,
    count
):

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


def is_authorized(
    chat_id,
    user_id
):

    try:

        return (
            auth_users.find_one({
                "chat_id": chat_id,
                "user_id": user_id
            })
            is not None
        )

    except Exception:

        return False


# ============================================================
# GET TARGET USER
# ============================================================

async def get_target(message):

    try:

        if (
            message.reply_to_message
            and
            message.reply_to_message.from_user
        ):

            return (
                message.reply_to_message.from_user
            )

        if len(
            message.command
        ) > 1:

            target = (
                message.command[1]
                .strip()
            )

            if target.lstrip("-").isdigit():

                return await app.get_users(
                    int(target)
                )

            return await app.get_users(
                target
            )

    except Exception as e:

        log.warning(
            "Target error: %s",
            e
        )

    return None


# ============================================================
# START
# ============================================================

@app.on_message(
    filters.command("start") &
    filters.private
)
async def start_private(
    _,
    message
):

    try:

        if os.path.isfile(
            START_IMAGE_PATH
        ):

            await message.reply_photo(
                photo=START_IMAGE_PATH,
                caption=START_TEXT,
                reply_markup=start_keyboard()
            )

        else:

            await message.reply_text(
                START_TEXT,
                reply_markup=start_keyboard(),
                disable_web_page_preview=True
            )

    except Exception as e:

        log.warning(
            "Start error: %s",
            e
        )


@app.on_message(
    filters.command("start") &
    filters.group
)
async def start_group(
    _,
    message
):

    try:

        if os.path.isfile(
            START_IMAGE_PATH
        ):

            await message.reply_photo(
                photo=START_IMAGE_PATH,
                caption=START_TEXT,
                reply_markup=start_keyboard()
            )

        else:

            await message.reply_text(
                START_TEXT,
                reply_markup=start_keyboard(),
                disable_web_page_preview=True
            )

    except Exception as e:

        log.warning(
            "Group start error: %s",
            e
        )


# ============================================================
# CALLBACKS
# ============================================================

@app.on_callback_query()
async def callbacks(
    _,
    query
):

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

@app.on_message(
    filters.command("ping")
)
async def ping(
    _,
    message
):

    try:

        started = time.perf_counter()

        temp = await message.reply_text(
            "<b>ᴘɪɴɢɪɴɢ... ❤️‍🔥</b>"
        )

        ping_ms = round(
            (
                time.perf_counter()
                - started
            ) * 1000,
            2
        )

        uptime = int(
            time.time()
            - BOT_START_TIME
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

        if days:

            uptime_text = (
                f"{days}ᴅ:"
                f"{hours}ʜ:"
                f"{minutes}ᴍ:"
                f"{seconds}s"
            )

        else:

            uptime_text = (
                f"{hours}ʜ:"
                f"{minutes}ᴍ:"
                f"{seconds}s"
            )

        ping_text = f"""
<b>ʜєʏ ʙᴧʙʏ !!

𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨 ɪꜱ ᴧʟɪᴠє 🥀 ᴧηᴅ
ᴡσʀᴋɪηɢ ꜰɪηє ᴡɪᴛʜ

➥ ᴘσηɢ : {ping_ms} ms
➥ ᴜᴘᴛɪϻє : {uptime_text}

✦ 𝐏σᴡєʀєᴅ вʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

        if os.path.isfile(
            PING_IMAGE_PATH
        ):

            try:
                await temp.delete()
            except Exception:
                pass

            await message.reply_photo(
                photo=PING_IMAGE_PATH,
                caption=ping_text
            )

        else:

            await temp.edit_text(
                ping_text,
                disable_web_page_preview=True
            )

    except Exception as e:

        log.warning(
            "Ping error: %s",
            e
        )


# ============================================================
# STATS
# ============================================================

@app.on_message(
    filters.command("stats")
)
async def bot_stats(
    _,
    message
):

    text = f"""
<b>✦ ʙᴏᴛ sᴛᴀᴛs

» ᴍᴇssᴀɢᴇs ᴄʜᴇᴄᴋᴇᴅ :
{get_stat("messages_checked")}

» ʙɪᴏ ʟɪɴᴋs ғᴏᴜɴᴅ :
{get_stat("bio_links")}

» ᴍᴇssᴀɢᴇs ᴅᴇʟᴇᴛᴇᴅ :
{get_stat("messages_deleted")}

» ᴡᴀʀɴɪɴɢs ɪssᴜᴇᴅ :
{get_stat("warnings")}</b>
"""

    await message.reply_text(
        text
    )


# ============================================================
# AUTH
# ============================================================

@app.on_message(
    filters.command("auth") &
    filters.group
)
async def auth_cmd(
    _,
    message
):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    target = await get_target(
        message
    )

    if not target:

        return await message.reply_text(
            "<b>» ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ ᴏʀ "
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


# ============================================================
# UNAUTH
# ============================================================

@app.on_message(
    filters.command("unauth") &
    filters.group
)
async def unauth_cmd(
    _,
    message
):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    target = await get_target(
        message
    )

    if not target:

        return await message.reply_text(
            "<b>» ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ ᴏʀ "
            "/unauth user_id</b>"
        )

    result = auth_users.delete_one({
        "chat_id": message.chat.id,
        "user_id": target.id
    })

    if result.deleted_count:

        await message.reply_text(
            f"<b>✅ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ : "
            f"{target.mention}</b>"
        )

    else:

        await message.reply_text(
            "<b>⚠️ ᴜsᴇʀ ᴡᴀs ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.</b>"
        )


# ============================================================
# AUTH USERS
# ============================================================

@app.on_message(
    filters.command("authusers") &
    filters.group
)
async def authusers_cmd(
    _,
    message
):

    if not await can_manage(
        app,
        message
    ):

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
            "<b>» ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ғᴏᴜɴᴅ.</b>"
        )

    lines = [
        "<b>◎ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs :</b>",
        ""
    ]

    for i, row in enumerate(
        rows,
        1
    ):

        username = row.get(
            "username"
        )

        name = (
            f"@{username}"
            if username
            else row.get(
                "name",
                "User"
            )
        )

        lines.append(
            f"<b>{i}. {name} "
            f"({row.get('user_id')})</b>"
        )

    await message.reply_text(
        "\n".join(lines)
    )


# ============================================================
# CLEAR AUTH
# ============================================================

@app.on_message(
    filters.command("clearauthusers") &
    filters.group
)
async def clearauthusers_cmd(
    _,
    message
):

    if not await can_manage(
        app,
        message
    ):

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
# RESET WARNING
# ============================================================

@app.on_message(
    filters.command("resetwarn") &
    filters.group
)
async def resetwarn_cmd(
    _,
    message
):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "<b>❌ ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs "
            "ᴀɴᴅ ᴏᴡɴᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs.</b>"
        )

    target = await get_target(
        message
    )

    if not target:

        return await message.reply_text(
            "<b>» ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ ᴏʀ "
            "/resetwarn user_id</b>"
        )

    set_warn(
        message.chat.id,
        target.id,
        0
    )

    await message.reply_text(
        f"<b>♻️ ᴡᴀʀɴɪɴɢ ʀᴇsᴇᴛ ғᴏʀ "
        f"{target.mention}</b>"
    )


# ============================================================
# BIO LINK MODERATION
# ============================================================

@app.on_message(
    filters.group &
    ~filters.service
)
async def bio_checker(
    client,
    message
):

    # --------------------------------------------------------
    # IGNORE INVALID MESSAGES
    # --------------------------------------------------------

    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # --------------------------------------------------------
    # ADMIN / OWNER EXEMPT
    # --------------------------------------------------------

    if await is_admin_or_owner(
        client,
        chat_id,
        user_id
    ):
        return

    # --------------------------------------------------------
    # AUTH USER EXEMPT
    # --------------------------------------------------------

    if is_authorized(
        chat_id,
        user_id
    ):
        return

    inc_stat(
        "messages_checked"
    )

    # --------------------------------------------------------
    # FETCH PROFILE BIO
    # --------------------------------------------------------

    bio = await get_user_bio(
        client,
        user_id
    )

    log.info(
        "BIO CHECK | user=%s | bio=%r",
        user_id,
        bio
    )

    # --------------------------------------------------------
    # NO LINK
    # --------------------------------------------------------

    if not has_bio_link(
        bio
    ):
        return

    # --------------------------------------------------------
    # LINK FOUND
    # --------------------------------------------------------

    inc_stat(
        "bio_links"
    )

    log.info(
        "BIO LINK FOUND | chat=%s | user=%s | bio=%r",
        chat_id,
        user_id,
        bio
    )

    # --------------------------------------------------------
    # DELETE MESSAGE
    # --------------------------------------------------------

    try:

        await message.delete()

        inc_stat(
            "messages_deleted"
        )

    except FloodWait as e:

        log.warning(
            "Delete FloodWait: %s",
            e.value
        )

        await asyncio.sleep(
            e.value
        )

    except RPCError as e:

        log.warning(
            "Delete failed: %s",
            e
        )

    # --------------------------------------------------------
    # ADD WARNING
    # --------------------------------------------------------

    current = (
        get_warn(
            chat_id,
            user_id
        ) + 1
    )

    set_warn(
        chat_id,
        user_id,
        current
    )

    inc_stat(
        "warnings"
    )

    mention = message.from_user.mention

    # ========================================================
    # MUTE
    # ========================================================

    if current >= WARN_LIMIT:

        try:

            until_date = (
                int(time.time())
                + MUTE_MINUTES * 60
            )

            await client.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(),
                until_date=until_date
            )

            mute_text = f"""
<b>🚨 𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨

⚠️ {mention} !!

ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ
ᴅᴜᴇ ᴛᴏ ʙɪᴏ ʟɪɴᴋ.

🚨 ᴡᴀʀɴɪɴɢ :- {current}/{WARN_LIMIT}

🔇 ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ
ғᴏʀ {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs.

🧹 ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ
ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ.</b>
"""

            await client.send_message(
                chat_id,
                mute_text,
                reply_markup=warning_keyboard(),
                disable_web_page_preview=True
            )

            # Reset after mute
            set_warn(
                chat_id,
                user_id,
                0
            )

        except FloodWait as e:

            log.warning(
                "Mute FloodWait: %s",
                e.value
            )

            await asyncio.sleep(
                e.value
            )

        except RPCError as e:

            log.error(
                "Mute failed: %s",
                e
            )

        except Exception as e:

            log.error(
                "Mute error: %s",
                e
            )

        return

    # ========================================================
    # WARNING
    # ========================================================

    try:

        warning_text = f"""
<b>🚨 𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨

⚠️ {mention} !!

ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ
ᴅᴜᴇ ᴛᴏ ʙɪᴏ ʟɪɴᴋ.

🚨 ᴡᴀʀɴɪɴɢ :- {current}/{WARN_LIMIT}

🧹 ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ
ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ ᴛᴏ ᴀᴠᴏɪᴅ ᴍᴜᴛᴇ.</b>
"""

        await client.send_message(
            chat_id,
            warning_text,
            reply_markup=warning_keyboard(),
            disable_web_page_preview=True
        )

    except FloodWait as e:

        log.warning(
            "Warning FloodWait: %s",
            e.value
        )

        await asyncio.sleep(
            e.value
        )

    except RPCError as e:

        log.error(
            "Warning send failed: %s",
            e
        )

    except Exception as e:

        log.error(
            "Warning error: %s",
            e
        )


# ============================================================
# STARTUP
# ============================================================

def print_startup_logger():

    try:

        import sys

        py_version = (
            f"{sys.version_info.major}."
            f"{sys.version_info.minor}."
            f"{sys.version_info.micro}"
        )

    except Exception:

        py_version = "Unknown"

    try:

        import pyrogram

        pyro_version = getattr(
            pyrogram,
            "__version__",
            "Unknown"
        )

    except Exception:

        pyro_version = "Unknown"

    log.info(
        "╔══════════════════════════════════════════════════════╗"
    )

    log.info(
        "║ ❖ BIO LINK CLEANER STARTED SUCCESSFULLY             ║"
    )

    log.info(
        "║                                                      ║"
    )

    log.info(
        "║ • PYROGRAM :- %s",
        pyro_version
    )

    log.info(
        "║ • PYTHON   :- %s",
        py_version
    )

    log.info(
        "║ • WARNING  :- %s",
        WARN_LIMIT
    )

    log.info(
        "║ • MUTE     :- %s MINUTES",
        MUTE_MINUTES
    )

    log.info(
        "║                                                      ║"
    )

    log.info(
        "║ » POWERED BY :- PURVI-BOTS                          ║"
    )

    log.info(
        "╚══════════════════════════════════════════════════════╝"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print_startup_logger()

    try:

        mongo.admin.command("ping")

        log.info(
            "MongoDB connected successfully."
        )

    except Exception as e:

        log.error(
            "MongoDB connection failed: %s",
            e
        )

        raise

    app.run()
