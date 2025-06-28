import datetime
from re import findall

from WinxMusic import app
from WinxMusic.misc import SUDOERS
from WinxMusic.utils.database import is_gbanned_user
from WinxMusic.utils.functions import check_format, extract_text_and_keyb
from WinxMusic.utils.keyboard import ikb
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import Chat, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup

from utils import del_welcome, get_welcome, set_welcome
from utils.error import capture_err
from utils.permissions import admins_only
from .notes import extract_urls


async def handle_new_member(member, chat):
    try:
        if member.id in SUDOERS:
            return
        if await is_gbanned_user(member.id):
            await chat.ban_member(member.id)
            await app.send_message(
                chat.id,
                f"{member.mention} was globally banned and has been removed. ❌\nIf you believe this is a mistake, you can appeal the ban in the support chat. 🛡️",
            )
            return
        if member.is_bot:
            return
        return await send_welcome_message(chat, member.id)

    except ChatAdminRequired:
        return


@app.on_chat_member_updated(filters.group, group=6)
@capture_err
async def welcome(_, user: ChatMemberUpdated):
    if not (
        user.new_chat_member
        and user.new_chat_member.status not in {CMS.RESTRICTED}
        and not user.old_chat_member
    ):
        return

    member = user.new_chat_member.user if user.new_chat_member else user.from_user
    chat = user.chat
    return await handle_new_member(member, chat)


async def send_welcome_message(chat: Chat, user_id: int, delete: bool = False):
    welcome, raw_text, file_id = await get_welcome(chat.id)

    if not raw_text:
        return
    text = raw_text
    keyb = None
    if findall(r"\[.+\,.+\]", raw_text):
        text, keyb = extract_text_and_keyb(ikb, raw_text)
    u = await app.get_users(user_id)
    if "{GROUPNAME}" in text:
        text = text.replace("{GROUPNAME}", f"Group {chat.title} 🏠")
    if "{NAME}" in text:
        text = text.replace("{NAME}", f"Welcome, {u.mention}! 👋")
    if "{ID}" in text:
        text = text.replace("{ID}", f"`{user_id}` 🆔")
    if "{FIRSTNAME}" in text:
        text = text.replace("{FIRSTNAME}", f"Hi, {u.first_name}! 😊")
    if "{SURNAME}" in text:
        sname = u.last_name or "No surname"
        text = text.replace("{SURNAME}", sname)
    if "{USERNAME}" in text:
        susername = u.username or "No username"
        text = text.replace("{USERNAME}", f"@{susername} 🌀")
    if "{DATE}" in text:
        DATE = datetime.datetime.now().strftime("%Y-%m-%d")
        text = text.replace("{DATE}", f"Date: {DATE} 📅")
    if "{WEEKDAY}" in text:
        WEEKDAY = datetime.datetime.now().strftime("%A")
        text = text.replace("{WEEKDAY}", f"Weekday: {WEEKDAY} 📆")
    if "{TIME}" in text:
        TIME = datetime.datetime.now().strftime("%H:%M:%S")
        text = text.replace("{TIME}", f"Time: {TIME} 🕒 UTC")

    if welcome == "Text":
        m = await app.send_message(chat.id, text=text, reply_markup=keyb, disable_web_page_preview=True)
    elif welcome == "Photo":
        m = await app.send_photo(chat.id, photo=file_id, caption=text, reply_markup=keyb)
    else:
        m = await app.send_animation(chat.id, animation=file_id, caption=text, reply_markup=keyb)


@app.on_message(filters.command("setwelcome") & ~filters.private)
@admins_only("can_change_info")
async def set_welcome_func(_, message):
    usage = "You need to reply to a message with text, gif, or photo to set it as a welcome message.\n\nNote: Caption is required for gif and photo."
    key = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="More Help ❓", url=f"t.me/{app.username}?start=greetings")
            ],
        ]
    )
    replied_message = message.reply_to_message
    chat_id = message.chat.id
    try:
        if not replied_message:
            await message.reply_text(usage, reply_markup=key)
            return
        if replied_message.animation:
            welcome = "Animation"
            file_id = replied_message.animation.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        if replied_message.photo:
            welcome = "Photo"
            file_id = replied_message.photo.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        if replied_message.text:
            welcome = "Text"
            file_id = None
            text = replied_message.text
            raw_text = text.markdown
        if replied_message.reply_markup and not findall(r"\[.+\,.+\]", raw_text):
            urls = extract_urls(replied_message.reply_markup)
            if urls:
                response = "\n".join([f"{name}=[{text}, {url}]" for name, text, url in urls])
                raw_text = raw_text + response
        raw_text = await check_format(ikb, raw_text)
        if raw_text:
            await set_welcome(chat_id, welcome, raw_text, file_id)
            return await message.reply_text("Welcome message has been set successfully! 🎉")
        else:
            return await message.reply_text(
                "Invalid formatting, check the help section.\n\n**Usage:**\nText: `Text`\nText + Buttons: `Text ~ Buttons`",
                reply_markup=key,
            )
    except UnboundLocalError:
        return await message.reply_text("**Only text, gif, and photo welcome messages are supported. 📢**")


@app.on_message(filters.command(["delwelcome", "deletewelcome"]) & ~filters.private)
@admins_only("can_change_info")
async def del_welcome_func(_, message):
    chat_id = message.chat.id
    await del_welcome(chat_id)
    await message.reply_text("Welcome message has been deleted. 🗑️")


@app.on_message(filters.command("getwelcome") & ~filters.private)
@admins_only("can_change_info")
async def get_welcome_func(_, message):
    chat = message.chat
    welcome, raw_text, file_id = await get_welcome(chat.id)
    if not raw_text:
        return await message.reply_text("No welcome message is set. ⚠️")
    if not message.from_user:
        return await message.reply_text("You're anonymous, cannot send welcome message. 🕵️")

    await send_welcome_message(chat, message.from_user.id)

    await message.reply_text(
        f'Welcome Type: {welcome}\n\nFile ID: `{file_id}`\n\n`{raw_text.replace("`", "")}`'
    )


__MODULE__ = "🙋Welcome"
__HELP__ = """
/setwelcome - Reply to a message with correct formatting to set the welcome message.
/delwelcome - Delete the welcome message.
/getwelcome - View the current welcome message.

**WELCOME CONFIGURATION ->**

**To set a photo or gif as a welcome message, add your welcome text as a caption to the photo or gif. The caption must be in the format below.**

For text, simply send the text and then reply with the command.

The format should be like below:

**Hello** {NAME} [{ID}] Welcome to {GROUPNAME}

~ #The separator (~) must be between the text and buttons, remove this comment as well.

Button=[Page, https://yourwebsite.com]
Button2=[GitHub, https://github.com]

**NOTES ->**

Check /markdownhelp for more information on formatting and other syntax.
"""
