import os

from WinxMusic import app
from WinxMusic.misc import SUDOERS
from WinxMusic.utils.database import is_gbanned_user
from pyrogram import enums, filters
from pyrogram.types import Message

n = "\n"
w = " "


def bold(x):
    return f"**{x}:** "


def bold_ul(x):
    return f"**--{x}:**-- "


def mono(x):
    return f"`{x}`{n}"


def section(title: str, body: dict, indent: int = 2, underline: bool = False) -> str:
    text = (bold_ul(title) + n) if underline else bold(title) + n
    for key, value in body.items():
        if value is not None:
            text += (
                indent * w
                + bold(key)
                + (
                    (value[0] + n)
                    if isinstance(value, list) and isinstance(value[0], str)
                    else mono(value)
                )
            )
    return text


async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status
        if x == enums.UserStatus.RECENTLY:
            return "🟢 Was Online & last seen recently."
        elif x == enums.UserStatus.LAST_WEEK:
            return "🕒 is Offline from a week ago."
        elif x == enums.UserStatus.LONG_AGO:
            return "🔘 Offline since long time ago."
        elif x == enums.UserStatus.OFFLINE:
            return "🔴 is Offline Now."
        elif x == enums.UserStatus.ONLINE:
            return "🟢 Is Online Now."
    except BaseException:
        return "❗ **Something went wrong!**"


async def get_user_info(user, already=False):
    if not already:
        user = await app.get_users(user)
    if not user.first_name:
        return ["⚠️ Deleted account", None]
    user_id = user.id
    online = await userstatus(user_id)
    username = user.username
    first_name = user.first_name
    mention = user.mention("🔗 Link")
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    is_gbanned = await is_gbanned_user(user_id)
    is_sudo = user_id in SUDOERS
    is_premium = user.is_premium
    body = {
        "📝 Name": [first_name],
        "📛 Username": [("@" + username) if username else "N/A"],
        "🆔 ID": user_id,
        "🌍 DC ID": dc_id,
        "🔗 Mention": [mention],
        "⭐ Premium": "Yes" if is_premium else "No",
        "👀 Last Seen": online,
    }
    caption = section("👤 User Information", body)
    return [caption, photo_id]


async def get_chat_info(chat):
    chat = await app.get_chat(chat)
    username = chat.username
    link = f"[🔗 Link](t.me/{username})" if username else "N/A"
    photo_id = chat.photo.big_file_id if chat.photo else None
    info = f"""
❅─────✧❅✦❅✧─────❅
             ✦ Chat Information ✦

➻ 🆔 Chat ID ‣ {chat.id}
➻ 📝 Name ‣ {chat.title}
➻ 📛 Username ‣ {chat.username}
➻ 🌍 DC ID ‣ {chat.dc_id}
➻ 📝 Description ‣ {chat.description}
➻ 📋 Type ‣ {chat.type}
➻ ✅ Verified ‣ {chat.is_verified}
➻ 🚫 Restricted ‣ {chat.is_restricted}
➻ 👑 Creator ‣ {chat.is_creator}
➻ ⚠️ Scam ‣ {chat.is_scam}
➻ 🤥 Fake ‣ {chat.is_fake}
➻ 👥 Members ‣ {chat.members_count}
➻ 🔗 Link ‣ {link}

❅─────✧❅✦❅✧─────❅"""
    return info, photo_id


@app.on_message(filters.command("info"))
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user_input = message.text.split(None, 1)[1]
        if user_input.isdigit():
            user = int(user_input)
        elif user_input.startswith("@"):
            user = user_input
        else:
            return await message.reply_text(
                "⚠️ Please provide a valid user ID or username, or reply to a message to get user info."
            )

    m = await message.reply_text("⏳ Processing...")

    try:
        info_caption, photo_id = await get_user_info(user)
    except Exception as e:
        return await m.edit(str(e))

    if not photo_id:
        return await m.edit(info_caption, disable_web_page_preview=True)
    photo = await app.download_media(photo_id)

    await message.reply_photo(photo, caption=info_caption, quote=False)
    await m.delete()
    os.remove(photo)


@app.on_message(filters.command("chatinfo"))
async def chat_info_func(_, message: Message):
    splited = message.text.split()
    if len(splited) == 1:
        chat = message.chat.id
        if chat == message.from_user.id:
            return await message.reply_text("**❗ Usage:** /chatinfo [USERNAME|ID]")
    else:
        chat = splited[1]
    try:
        m = await message.reply_text("⏳ Processing...")

        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)

        photo = await app.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await m.edit(str(e))


__MODULE__ = "Group-Info"
__HELP__ = """
**ℹ️ User and Chat Info Commands:**

• `/info`: Get detailed information about a user — name, ID, premium status, etc.
• `/chatinfo [USERNAME|ID]`: Get detailed information about a chat — title, members, and more.
"""
    
