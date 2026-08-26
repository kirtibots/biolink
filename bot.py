import os, re, time, asyncio, logging
from pymongo import MongoClient
from pyrogram import Client, filters, idle
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
)

# ================= CONFIG =================

API_ID = int(os.getenv("API_ID", "21692000"))
API_HASH = os.getenv("API_HASH", "1e37856155373adf855c061c49847ced")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")

BOT_USERNAME = os.getenv("BOT_USERNAME", "Radhaprobot").lstrip("@")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/annu_support")
UPDATE_URL = os.getenv("UPDATE_URL", "https://t.me/annu_updates")
OWNER_URL = os.getenv("OWNER_URL", "https://t.me/")
START_IMAGE = os.getenv("START_IMAGE_PATH", "https://h.uguu.se/FekWWcsz.jpg")
PING_IMAGE = os.getenv("PING_IMAGE_PATH", START_IMAGE)

WARN_LIMIT = int(os.getenv("WARN_LIMIT", "3"))
MUTE_MINUTES = int(os.getenv("MUTE_MINUTES", "60"))
LOGGER_ID = int(os.getenv("LOGGER_GROUP_ID", "0"))

if not BOT_TOKEN or not MONGO_URI:
    raise RuntimeError("BOT_TOKEN and MONGO_URI are required.")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
log = logging.getLogger("BIO-BOT")

# ================= APP =================

app = Client(
    "biolink_cleaner",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= DATABASE =================

mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
db = mongo["bio_link_cleaner"]

groups = db.groups
auth = db.auth_users
warns = db.warnings
stats = db.stats

def stat(name, n=1):
    try:
        stats.update_one(
            {"_id": name},
            {"$inc": {"value": n}},
            upsert=True
        )
    except Exception:
        pass

def get_stat(name):
    try:
        x = stats.find_one({"_id": name})
        return x.get("value", 0) if x else 0
    except Exception:
        return 0

def get_warn(chat_id, user_id):
    x = warns.find_one({"chat_id": chat_id, "user_id": user_id})
    return x.get("count", 0) if x else 0

def set_warn(chat_id, user_id, count):
    warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True
    )

# ================= TEXT =================

START_TEXT = """
<b>❖ ʜєʏ ʙᴧʙʏ !!

𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨 ɪs ᴧʟɪᴠє 🥀

➥ ᴀ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ ʙᴏᴛ ғᴏʀ ɢʀᴏᴜᴘs.
➥ ʙɪᴏ ʟɪɴᴋ ᴜsᴇʀs ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇ.
➥ ᴡᴀʀɴ & ᴍᴜᴛᴇ sʏsᴛᴇᴍ.
➥ ᴀᴅᴍɪɴ & ᴀᴜᴛʜ ᴄᴏᴍᴍᴀɴᴅs.

➳ ᴄʟɪᴄᴋ ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴄᴏᴍᴍᴀɴᴅs.

✦ 𝐏σᴡєʀєᴅ вʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

ABOUT_TEXT = """
<b>❖ ᴀʙᴏᴜᴛ ᴍᴇ

➥ ʙɪᴏ ʟɪɴᴋ ᴄʜᴇᴄᴋᴇʀ ғᴏʀ ɢʀᴏᴜᴘs.
➥ ᴘʏᴛʜᴏɴ + ᴘʏʀᴏɢʀᴀᴍ + ᴍᴏɴɢᴏᴅʙ.
➥ ᴡᴀʀɴɪɴɢ & ᴀᴜᴛᴏ ᴍᴜᴛᴇ.

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

HELP_TEXT = """
<b>❖ ʜᴇʟᴘ

/start - sᴛᴀʀᴛ ʙᴏᴛ
/ping - ᴄʜᴇᴄᴋ sᴛᴀᴛᴜs
/stats - ʙᴏᴛ sᴛᴀᴛs

/auth - ᴀᴜᴛʜᴏʀɪᴢᴇ
/unauth - ʀᴇᴍᴏᴠᴇ ᴀᴜᴛʜ
/authusers - ᴀᴜᴛʜ ᴜsᴇʀs
/clearauthusers - ᴄʟᴇᴀʀ ᴀᴜᴛʜ
/resetwarn - ʀᴇsᴇᴛ ᴡᴀʀɴɪɴɢ

❖ ᴡᴀʀɴ ʟɪᴍɪᴛ : {WARN_LIMIT}
❖ ᴍᴜᴛᴇ : {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs</b>
""".format(
    WARN_LIMIT=WARN_LIMIT,
    MUTE_MINUTES=MUTE_MINUTES
)

# ================= BUTTONS =================

def home_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⊞ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⊞",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )],
        [
            InlineKeyboardButton("≡ ᴏᴡɴᴇʀ ≡", url=OWNER_URL),
            InlineKeyboardButton("≡ ᴀʙᴏᴜᴛ ≡", callback_data="about")
        ],
        [InlineKeyboardButton(
            "≡ ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs ≡",
            callback_data="help"
        )]
    ])

def about_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("≡ sᴜᴘᴘᴏʀᴛ ≡", url=SUPPORT_URL),
            InlineKeyboardButton("≡ ᴜᴘᴅᴀᴛᴇ ≡", url=UPDATE_URL)
        ],
        [InlineKeyboardButton("≡ ʙᴀᴄᴋ ≡", callback_data="back")]
    ])

def help_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("≡ sᴜᴘᴘᴏʀᴛ ≡", url=SUPPORT_URL),
            InlineKeyboardButton("≡ ʙᴀᴄᴋ ≡", callback_data="back")
        ]
    ])

# ================= BIO CHECK =================

LINK_RE = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/|tg://|"
    r"\b[\w-]+\.(com|net|org|me|in|co|io|xyz|site|online|live|shop|"
    r"dev|app|store|pro|tech|info|biz|cc|tv)\b)",
    re.I
)

async def get_bio(user_id):
    try:
        u = await app.get_chat(user_id)
        return (u.bio or "").strip()
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await get_bio(user_id)
    except Exception:
        return ""

async def is_admin(chat_id, user_id):
    try:
        m = await app.get_chat_member(chat_id, user_id)
        return m.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        )
    except Exception:
        return False

async def is_auth(chat_id, user_id):
    try:
        return auth.find_one({
            "chat_id": chat_id,
            "user_id": user_id
        }) is not None
    except Exception:
        return False

# ================= START =================

@app.on_message(filters.command("start") & filters.private)
async def start(_, m):
    try:
        await m.reply_photo(
            START_IMAGE,
            caption=START_TEXT,
            reply_markup=home_kb()
        )
    except Exception:
        await m.reply_text(
            START_TEXT,
            reply_markup=home_kb()
        )

@app.on_message(filters.command("start") & filters.group)
async def group_start(_, m):
    try:
        await m.reply_photo(
            START_IMAGE,
            caption=START_TEXT,
            reply_markup=home_kb()
        )
    except Exception:
        await m.reply_text(
            START_TEXT,
            reply_markup=home_kb()
        )

# ================= CALLBACK =================

@app.on_callback_query()
async def callbacks(_, q):
    try:
        if q.data == "about":
            await q.message.edit_text(
                ABOUT_TEXT,
                reply_markup=about_kb()
            )
        elif q.data == "help":
            await q.message.edit_text(
                HELP_TEXT,
                reply_markup=help_kb()
            )
        elif q.data == "back":
            await q.message.edit_text(
                START_TEXT,
                reply_markup=home_kb()
            )
        await q.answer()
    except Exception:
        try:
            await q.answer("Error", show_alert=True)
        except Exception:
            pass

# ================= PING =================

START_TIME = time.time()

@app.on_message(filters.command("ping"))
async def ping(_, m):
    ms = round((time.time() - START_TIME) * 1000, 2)
    up = int(time.time() - START_TIME)

    d, r = divmod(up, 86400)
    h, r = divmod(r, 3600)
    mi, s = divmod(r, 60)

    text = f"""
<b>ʜєʏ ʙᴧʙʏ !!

𝐁ɪᴏ 𝐋ɪɴᴋ 𝐂ʟᴇᴀɴᴇʀ 🚨 ɪs ᴧʟɪᴠє 🥀

➥ ᴘɪɴɢ : {ms} ms
➥ ᴜᴘᴛɪᴍᴇ : {d}ᴅ {h}ʜ {mi}ᴍ {s}s

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>
"""

    try:
        await m.reply_photo(PING_IMAGE, caption=text)
    except Exception:
        await m.reply_text(text)

# ================= STATS =================

@app.on_message(filters.command("stats"))
async def stats_cmd(_, m):
    await m.reply_text(
        f"""<b>✦ ʙᴏᴛ sᴛᴀᴛs

» ᴍᴇssᴀɢᴇs : {get_stat("messages")}
» ʙɪᴏ ʟɪɴᴋs : {get_stat("bio_links")}
» ᴅᴇʟᴇᴛᴇᴅ : {get_stat("deleted")}

✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ » ᴘᴜʀᴠɪ ʙᴏᴛꜱ</b>"""
    )

# ================= AUTH =================

@app.on_message(filters.command("auth") & filters.group)
async def authorize(_, m):
    if not await is_admin(m.chat.id, m.from_user.id):
        return await m.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs.")

    target = m.reply_to_message.from_user if m.reply_to_message else None
    if not target:
        return await m.reply_text("↪️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")

    auth.update_one(
        {"chat_id": m.chat.id, "user_id": target.id},
        {"$set": {"name": target.first_name}},
        upsert=True
    )
    await m.reply_text(f"✅ <b>{target.first_name}</b> ᴀᴜᴛʜᴏʀɪᴢᴇᴅ.")

@app.on_message(filters.command("unauth") & filters.group)
async def unauthorize(_, m):
    if not await is_admin(m.chat.id, m.from_user.id):
        return

    target = m.reply_to_message.from_user if m.reply_to_message else None
    if not target:
        return await m.reply_text("↪️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")

    auth.delete_one({
        "chat_id": m.chat.id,
        "user_id": target.id
    })
    await m.reply_text("✅ ᴜsᴇʀ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ.")

@app.on_message(filters.command("authusers") & filters.group)
async def authusers(_, m):
    if not await is_admin(m.chat.id, m.from_user.id):
        return

    users = list(auth.find({"chat_id": m.chat.id}))
    if not users:
        return await m.reply_text("❌ ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs.")

    text = "<b>✦ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs\n\n"
    text += "\n".join(
        f"• {x.get('name', 'User')} — <code>{x['user_id']}</code>"
        for x in users
    )
    await m.reply_text(text + "</b>")

@app.on_message(filters.command("clearauthusers") & filters.group)
async def clear_auth(_, m):
    if not await is_admin(m.chat.id, m.from_user.id):
        return
    auth.delete_many({"chat_id": m.chat.id})
    await m.reply_text("✅ ᴀʟʟ ᴀᴜᴛʜ ᴜsᴇʀs ᴄʟᴇᴀʀᴇᴅ.")

# ================= RESET WARN =================

@app.on_message(filters.command("resetwarn") & filters.group)
async def resetwarn(_, m):
    if not await is_admin(m.chat.id, m.from_user.id):
        return

    target = m.reply_to_message.from_user if m.reply_to_message else None
    if not target:
        return await m.reply_text("↪️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.")

    set_warn(m.chat.id, target.id, 0)
    await m.reply_text("✅ ᴡᴀʀɴɪɴɢ ʀᴇsᴇᴛ.")

# ================= BIO MODERATION =================

@app.on_message(filters.group & ~filters.service)
async def checker(_, m):
    if not m.from_user:
        return

    if await is_admin(m.chat.id, m.from_user.id):
        return

    if await is_auth(m.chat.id, m.from_user.id):
        return

    stat("messages")

    bio = await get_bio(m.from_user.id)

    if not LINK_RE.search(bio):
        return

    stat("bio_links")

    try:
        await m.delete()
        stat("deleted")
    except Exception:
        return

    count = get_warn(m.chat.id, m.from_user.id) + 1

    if count >= WARN_LIMIT:
        try:
            await app.restrict_chat_member(
                m.chat.id,
                m.from_user.id,
                permissions=ChatPermissions(),
                until_date=int(time.time()) + MUTE_MINUTES * 60
            )
            set_warn(m.chat.id, m.from_user.id, 0)

            await m.reply_text(
                f"🔇 <b>{m.from_user.first_name}</b> ᴍᴜᴛᴇᴅ "
                f"ғᴏʀ {MUTE_MINUTES} ᴍɪɴᴜᴛᴇs."
            )
        except Exception as e:
            log.warning("Mute error: %s", e)
    else:
        set_warn(m.chat.id, m.from_user.id, count)

        await m.reply_text(
            f"⚠️ <b>{m.from_user.first_name}</b>\n"
            f"ʙɪᴏ ᴍᴇ ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ.\n\n"
            f"ᴡᴀʀɴɪɴɢ : {count}/{WARN_LIMIT}"
        )

# ================= STARTUP =================

async def main():
    await app.start()

    me = await app.get_me()
    log.info(
        "BOT STARTED: @%s",
        me.username or me.id
    )

    if LOGGER_ID:
        try:
            await app.send_message(
                LOGGER_ID,
                f"🟢 <b>Bot Started</b>\n\n"
                f"Bot: @{me.username or me.id}\n"
                f"Bio Cleaner: ON\n"
                f"Warning System: ON\n"
                f"Auto Mute: ON"
            )
        except Exception as e:
            log.warning("Logger error: %s", e)

    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
