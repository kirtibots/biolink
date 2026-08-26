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


# ============================================================
# BIO LINK CLEANER BOT
# ============================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")

BOT_USERNAME = os.getenv(
    "BOT_USERNAME",
    "BiolinkCleanerBot"
).lstrip("@")

SUPPORT_URL = os.getenv(
    "SUPPORT_URL",
    "https://t.me/"
)

UPDATE_URL = os.getenv(
    "UPDATE_URL",
    "https://t.me/"
)

OWNER_URL = os.getenv(
    "OWNER_URL",
    "https://t.me/"
)

PROMO_URL = os.getenv(
    "PROMO_URL",
    "https://t.me/"
)

PING_IMAGE_PATH = os.getenv(
    "PING_IMAGE_PATH",
    "ping.jpg"
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
# START
# ============================================================

START_TEXT = """
❖ <b>ʜᴇʏ, ɪ'ᴍ ʙɪᴏ ʟɪɴᴋ ᴄʟᴇᴀɴᴇʀ</b> 🚨🥳

༺ <b>ᴀ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ ʙᴏᴛ ғᴏʀ ɢʀᴏᴜᴘs.</b>

» ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ᴡʜᴇɴ ᴜsᴇʀ ʜᴀs ᴀ ʟɪɴᴋ ɪɴ ʙɪᴏ.
» sᴜᴘᴘᴏʀᴛ ᴀᴜᴛʜ ᴜsᴇʀ & ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.
» ᴡᴀʀɴ & ᴍᴜᴛᴇ ᴜsᴇʀs ᴡɪᴛʜ ᴍᴇɴᴛɪᴏɴ.

➳ <b>ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.</b>

✦ <b>ᴍᴀᴅᴇ ʙʏ :-</b>
<a href="https://t.me/">ᴘᴜʀᴠɪ-ʙᴏᴛs™</a>
"""


# ============================================================
# ABOUT
# ============================================================

ABOUT_TEXT = """
─────────────────────────

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

❖ υᴘᴅᴧᴛєs ᴄʜᴧηηєʟ ➥
<a href="https://t.me/">ᴘᴜʀᴠɪ-ʙᴏᴛs</a>

❖ sυᴘᴘσʀᴛ ᴄʜᴧᴛ ➥
<a href="https://t.me/">ᴘᴜʀᴠɪ-ᴜᴘᴅᴀᴛᴇs</a>

─────────────────────────

➤ ʙσᴛ sᴛᴧᴛυs & ϻσʀє ʙσᴛs -
<a href="https://t.me/">ᴄʟɪᴄᴋ ʜєʀє</a>

➤ ᴘᴧɪᴅ ᴘʀσϻσᴛɪση :-
<a href="https://t.me/">ᴄσηᴛᴧᴄᴛ ʜєʀє</a>

─────────────────────────
"""


# ============================================================
# HELP
# ============================================================

HELP_TEXT = """
❖ ʜᴇʀᴇ ɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ ʙᴏᴛ.

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

⊚ ᴍᴇᴍʙᴇʀ :

👤 ɴᴏʀᴍᴀʟ ᴍᴇᴍʙᴇʀ
» ɴᴏ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs.

━━━━━━━━━━━━━━━━━━

➻ ɴᴏᴛᴇ :- ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs
& ᴏɴʟʏ ᴜsᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs
ᴀɴᴅ ᴏᴡɴᴇʀs.

✦ 𝐏ᴏᴡᴇʀᴇᴅ вʏ » ᴀʟᴘʜᴀ-ʙᴀʙʏ
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
# LINK DETECTOR
# ============================================================

def is_link(text):

    if not text:
        return False

    patterns = [
        r"https?://\S+",
        r"(?:www\.)\S+\.\S+",
        r"(?:t\.me|telegram\.me|telegram\.dog)/\S+",
        r"tg://\S+",
        r"\b[a-z0-9.-]+\.(?:com|net|org|me|in|co|io|xyz|site|online|live|shop|dev|app)\b",
    ]

    return any(
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
        for pattern in patterns
    )


def has_bio_link(bio):

    return bool(
        bio and is_link(bio)
    )


# ============================================================
# STATS
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
            "Stats error: %s",
            e
        )


def get_stat(key):

    try:

        data = stats.find_one(
            {"_id": key}
        )

        return int(
            data.get("value", 0)
        ) if data else 0

    except Exception:
        return 0


# ============================================================
# WARNING DATABASE
# ============================================================

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


# ============================================================
# AUTH
# ============================================================

def is_authorized(chat_id, user_id):

    try:

        return auth_users.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        }) is not None

    except Exception:
        return False


# ============================================================
# ADMIN + OWNER CHECK
# ============================================================

async def is_admin(
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

        status_value = getattr(
            status,
            "value",
            status
        )

        status_value = str(
            status_value
        ).lower()

        return status_value in (
            "owner",
            "administrator"
        )

    except FloodWait as e:

        await asyncio.sleep(
            e.value
        )

        return await is_admin(
            client,
            chat_id,
            user_id
        )

    except RPCError as e:

        log.warning(
            "Admin check failed: %s",
            e
        )

        return False

    except Exception as e:

        log.warning(
            "Admin check error: %s",
            e
        )

        return False


async def can_manage(
    client,
    message
):

    if not message.from_user:
        return False

    if not message.chat:
        return False

    return await is_admin(
        client,
        message.chat.id,
        message.from_user.id
    )


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

            return await app.get_users(
                target
            )

    except RPCError:
        return None

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
async def start_private(_, message):

    await message.reply_text(
        START_TEXT,
        reply_markup=start_keyboard(),
        disable_web_page_preview=True
    )


@app.on_message(
    filters.command("start") &
    filters.group
)
async def start_group(_, message):

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

    except RPCError:

        try:
            await query.answer(
                "Unable to update message.",
                show_alert=True
            )
        except Exception:
            pass


# ============================================================
# PING WITH IMAGE
# ============================================================

@app.on_message(
    filters.command("ping")
)
async def ping(_, message):

    try:

        started = time.perf_counter()

        temp = await message.reply_text(
            "ᴘɪɴɢɪɴɢ... ❤️‍🔥"
        )

        ping_ms = round(
            (
                time.perf_counter()
                - started
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
ʜєʏ ʙᴧʙʏ !!

<b>𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ</b> 🚨 ɪꜱ ᴧʟɪᴠє 🥀 ᴧηᴅ
ᴡσʀᴋɪηɢ ꜰɪηє ᴡɪᴛʜ

➥ ᴘσηɢ : <code>{ping_ms} ms</code>
➥ ᴜᴘᴛɪϻє : <code>{uptime_text}</code>

✦ 𝐏σᴡєʀєᴅ вʏ » <b>ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

        if os.path.exists(
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

    except FloodWait as e:

        log.warning(
            "Ping FloodWait: %s",
            e.value
        )

    except RPCError as e:

        log.warning(
            "Ping RPC error: %s",
            e
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
async def bot_stats(_, message):

    text = (
        "✦ <b>ʙᴏᴛ sᴛᴀᴛs</b>\n\n"
        f"» ᴍᴇssᴀɢᴇs ᴄʜᴇᴄᴋᴇᴅ: "
        f"<code>{get_stat('messages_checked')}</code>\n"
        f"» ʙɪᴏ ʟɪɴᴋs ғᴏᴜɴᴅ: "
        f"<code>{get_stat('bio_links')}</code>\n"
        f"» ᴍᴇssᴀɢᴇs ᴅᴇʟᴇᴛᴇᴅ: "
        f"<code>{get_stat('messages_deleted')}</code>\n"
        f"» ᴡᴀʀɴɪɴɢs ɪssᴜᴇᴅ: "
        f"<code>{get_stat('warnings')}</code>"
    )

    await message.reply_text(text)


# ============================================================
# AUTH
# ============================================================

@app.on_message(
    filters.command("auth") &
    filters.group
)
async def auth_cmd(_, message):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "❌ <b>Only group admins "
            "and owners can use this command.</b>"
        )

    target = await get_target(message)

    if not target:

        return await message.reply_text(
            "» Reply to a user or use "
            "<code>/auth user_id</code>."
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
        f"✅ <b>ᴀᴜᴛʜᴏʀɪᴢᴇᴅ:</b> "
        f"{target.mention}\n\n"
        "» ᴜsᴇʀ ɪs ɴᴏᴡ ᴇxᴇᴍᴘᴛ ғʀᴏᴍ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋ."
    )


# ============================================================
# UNAUTH
# ============================================================

@app.on_message(
    filters.command("unauth") &
    filters.group
)
async def unauth_cmd(_, message):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "❌ <b>Only group admins "
            "and owners can use this command.</b>"
        )

    target = await get_target(message)

    if not target:

        return await message.reply_text(
            "» Reply to a user or use "
            "<code>/unauth user_id</code>."
        )

    result = auth_users.delete_one({
        "chat_id": message.chat.id,
        "user_id": target.id
    })

    if result.deleted_count:

        await message.reply_text(
            f"✅ <b>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ:</b> "
            f"{target.mention}"
        )

    else:

        await message.reply_text(
            "⚠️ <b>User was not authorized.</b>"
        )


# ============================================================
# AUTH USERS
# ============================================================

@app.on_message(
    filters.command("authusers") &
    filters.group
)
async def authusers_cmd(_, message):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "❌ <b>Only group admins "
            "and owners can use this command.</b>"
        )

    rows = list(
        auth_users.find({
            "chat_id": message.chat.id
        }).limit(50)
    )

    if not rows:

        return await message.reply_text(
            "» <b>No authorized users found.</b>"
        )

    lines = [
        "◎ <b>ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs:</b>",
        ""
    ]

    for i, row in enumerate(
        rows,
        1
    ):

        username = row.get("username")

        name = (
            f"@{username}"
            if username
            else row.get(
                "name",
                "User"
            )
        )

        lines.append(
            f"{i}. {name} "
            f"<code>{row.get('user_id')}</code>"
        )

    await message.reply_text(
        "\n".join(lines)
    )


# ============================================================
# CLEAR AUTH USERS
# ============================================================

@app.on_message(
    filters.command("clearauthusers") &
    filters.group
)
async def clearauthusers_cmd(_, message):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "❌ <b>Only group admins "
            "and owners can use this command.</b>"
        )

    result = auth_users.delete_many({
        "chat_id": message.chat.id
    })

    await message.reply_text(
        f"✅ <b>Removed "
        f"{result.deleted_count} "
        f"authorized user(s).</b>"
    )


# ============================================================
# RESET WARNING
# ============================================================

@app.on_message(
    filters.command("resetwarn") &
    filters.group
)
async def resetwarn_cmd(_, message):

    if not await can_manage(
        app,
        message
    ):

        return await message.reply_text(
            "❌ <b>Only group admins "
            "and owners can use this command.</b>"
        )

    target = await get_target(message)

    if not target:

        return await message.reply_text(
            "» Reply to a user or use "
            "<code>/resetwarn user_id</code>."
        )

    set_warn(
        message.chat.id,
        target.id,
        0
    )

    await message.reply_text(
        f"♻️ <b>Warning count reset for</b> "
        f"{target.mention}"
    )


# ============================================================
# BIO LINK CHECKER
# ============================================================

@app.on_message(
    filters.group &
    ~filters.service
)
async def bio_checker(_, message):

    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # --------------------------------------------------------
    # OWNER + ADMIN EXEMPT
    # --------------------------------------------------------

    if await is_admin(
        app,
        chat_id,
        user_id
    ):
        return

    inc_stat(
        "messages_checked"
    )

    # --------------------------------------------------------
    # GET USER BIO
    # --------------------------------------------------------

    try:

        user = await app.get_users(
            user_id
        )

        bio = (
            getattr(
                user,
                "bio",
                ""
            ) or ""
        )

    except FloodWait as e:

        log.warning(
            "Bio FloodWait: %s",
            e.value
        )

        return

    except RPCError as e:

        log.warning(
            "Bio fetch error: %s",
            e
        )

        return

    except Exception as e:

        log.warning(
            "Bio error: %s",
            e
        )

        return

    # --------------------------------------------------------
    # NO LINK
    # --------------------------------------------------------

    if not has_bio_link(bio):
        return

    # --------------------------------------------------------
    # AUTH EXEMPT
    # --------------------------------------------------------

    if is_authorized(
        chat_id,
        user_id
    ):
        return

    inc_stat(
        "bio_links"
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

    except RPCError as e:

        log.warning(
            "Delete failed: %s",
            e
        )

    # --------------------------------------------------------
    # WARNING COUNT
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
    # 3/3 = MUTE
    # ========================================================

    if current >= WARN_LIMIT:

        try:

            until_date = (
                int(time.time())
                + (
                    MUTE_MINUTES * 60
                )
            )

            await app.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(),
                until_date=until_date
            )

            mute_text = f"""
<b>🚨 𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨</b>

⚠️ <b>{mention}</b> !!

<b>ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ
ᴅᴜᴇ ᴛᴏ ʙɪᴏ ʟɪɴᴋ.</b>

🚨 <b>ᴡᴀʀɴɪɴɢ :-</b>
<code>{current}/{WARN_LIMIT}</code>

🔇 <b>ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ
ғᴏʀ {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs.</b>

🧹 <b>ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ
ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ.</b>
"""

            await app.send_message(
                chat_id,
                mute_text,
                reply_markup=warning_keyboard(),
                disable_web_page_preview=True
            )

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

        except RPCError as e:

            log.warning(
                "Mute failed: %s",
                e
            )

    # ========================================================
    # 1/3 OR 2/3 = WARNING
    # ========================================================

    else:

        try:

            warning_text = f"""
<b>🚨 𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨</b>

⚠️ <b>{mention}</b> !!

<b>ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ
ᴅᴜᴇ ᴛᴏ ʙɪᴏ ʟɪɴᴋ.</b>

🚨 <b>ᴡᴀʀɴɪɴɢ :-</b>
<code>{current}/{WARN_LIMIT}</code>

🧹 <b>ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ
ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ ᴛᴏ ᴀᴠᴏɪᴅ ᴍᴜᴛᴇ.</b>
"""

            await app.send_message(
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

        except RPCError as e:

            log.warning(
                "Warning send failed: %s",
                e
            )


# ============================================================
# STARTUP LOGGER
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

    plugin_count = os.getenv(
        "PLUGIN_COUNT",
        "15"
    )

    bot_name = os.getenv(
        "LOGGER_BOT_NAME",
        "Purvi 🐒"
    )

    powered_by = os.getenv(
        "LOGGER_POWERED_BY",
        "PURVI-BOTS"
    )

    log.info(
        "╔══════════════════════════════════════════════════════╗"
    )

    log.info(
        "║ ❖ BOT STARTED SUCCESSFULLY                           ║"
    )

    log.info(
        "║                                                      ║"
    )

    log.info(
        "║ • BOT      :- %s",
        bot_name
    )

    log.info(
        "║ • PLUGINS  :- %s LOADED",
        plugin_count
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
        "║                                                      ║"
    )

    log.info(
        "║ » POWERED BY :- %s",
        powered_by
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
