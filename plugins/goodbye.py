import datetime
from re import findall

from WinxMusic import app
from WinxMusic.misc import SUDOERS
from WinxMusic.utils.database import is_gbanned_user
from WinxMusic.utils.functions import check_format, extract_text_and_keyb
from WinxMusic.utils.keyboard import ikb
from pyrogram import filters, Client
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Message

from utils import (
    del_goodbye,
    get_goodbye,
    set_goodbye,
    is_greetings_on,
    set_greetings_on,
    set_greetings_off,
)
from utils.error import capture_err
from utils.permissions import admins_only
from .notes import extract_urls


async def handle_left_member(member, chat: Chat):
    try:
        if member.id in SUDOERS:
            return
        if await is_gbanned_user(member.id):
            await chat.ban_member(member.id)
            await app.send_message(
                chat.id,
                f"{member.mention} was globally banned and removed."
                + " If you believe this is a mistake, please appeal in the help chat.",
            )
            return
        if member.is_bot:
            return
        return await send_left_message(chat, member.id)

    except ChatAdminRequired:
        return


@app.on_message(filters.left_chat_member & filters.group, group=6)
@capture_err
async def goodbye(_, message: Message):
    if message.from_user:
        member = await app.get_users(message.from_user.id)
        chat = message.chat
        return await handle_left_member(member, chat)


async def send_left_message(chat: Chat, user_id: int, delete: bool = False):
    is_on = await is_greetings_on(chat.id, "goodbye")
    if not is_on:
        return

    goodbye, raw_text, file_id = await get_goodbye(chat.id)
    if not raw_text:
        return

    text = raw_text
    keyb = None

    if findall(r"\[.+\,.+\]", raw_text):
        text, keyb = extract_text_and_keyb(ikb, raw_text)

    u = await app.get_users(user_id)

    replacements = {
        "{NAME}": u.mention,
        "{ID}": f"`{user_id}`",
        "{FIRSTNAME}": u.first_name,
        "{GROUPNAME}": chat.title,
        "{SURNAME}": u.last_name or "None",
        "{USERNAME}": u.username or "None",
        "{DATE}": datetime.datetime.now().strftime("%Y-%m-%d"),
        "{WEEKDAY}": datetime.datetime.now().strftime("%A"),
        "{TIME}": datetime.datetime.now().strftime("%H:%M:%S") + " UTC",
    }

    for placeholder, value in replacements.items():
        if placeholder in text:
            text = text.replace(placeholder, value)

    if goodbye == "Text":
        m = await app.send_message(
            chat.id,
            text=text,
            reply_markup=keyb,
            disable_web_page_preview=True,
        )
    elif goodbye == "Photo":
        m = await app.send_photo(
            chat.id,
            photo=file_id,
            caption=text,
            reply_markup=keyb,
        )
    else:
        m = await app.send_animation(
            chat.id,
            animation=file_id,
            caption=text,
            reply_markup=keyb,
        )


@app.on_message(filters.command("setgoodbye") & ~filters.private)
@admins_only("can_change_info")
async def set_goodbye_func(_, message: Message):
    usage = "You need to reply to a text, gif or photo to set it as the goodbye message.\n\nNote: Captions are required for gif and photo."
    key = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="More Help", url=f"t.me/{app.username}?start=greetings")]]
    )
    replied_message = message.reply_to_message
    chat_id = message.chat.id
    try:
        if not replied_message:
            await message.reply_text(usage, reply_markup=key)
            return
        if replied_message.animation:
            goodbye = "Animation"
            file_id = replied_message.animation.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        if replied_message.photo:
            goodbye = "Photo"
            file_id = replied_message.photo.file_id
            text = replied_message.caption
            if not text:
                return await message.reply_text(usage, reply_markup=key)
            raw_text = text.markdown
        if replied_message.text:
            goodbye = "Text"
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
            await set_goodbye(chat_id, goodbye, raw_text, file_id)
            return await message.reply_text("Goodbye message has been set successfully.")
        else:
            return await message.reply_text(
                "Invalid formatting. Please check the help section.\n\n**Usage:**\nText: `Message`\nText + buttons: `Message ~ Buttons`",
                reply_markup=key,
            )
    except UnboundLocalError:
        return await message.reply_text(
            "**Only text, gif, and photo are supported as goodbye messages.**"
        )


@app.on_message(filters.command(["delgoodbye", "deletegoodbye"]) & ~filters.private)
@admins_only("can_change_info")
async def del_goodbye_func(_, message: Message):
    chat_id = message.chat.id
    await del_goodbye(chat_id)
    await message.reply_text("Goodbye message deleted successfully.")


@app.on_message(filters.command("goodbye") & ~filters.private)
@admins_only("can_change_info")
async def goodbye(client: Client, message: Message):
    command = message.text.split()

    if len(command) == 1:
        return await get_goodbye_func(client, message)

    if len(command) == 2:
        action = command[1].lower()
        if action in ["on", "enable", "y", "yes", "true", "t"]:
            success = await set_greetings_on(message.chat.id, "goodbye")
            if success:
                await message.reply_text("I will now say goodbye to members who leave.")
            else:
                await message.reply_text("Failed to enable goodbye messages.")
        elif action in ["off", "disable", "n", "no", "false", "f"]:
            success = await set_greetings_off(message.chat.id, "goodbye")
            if success:
                await message.reply_text("I'll remain silent when someone leaves.")
            else:
                await message.reply_text("Failed to disable goodbye messages.")
        else:
            await message.reply_text(
                "Invalid command. Please use:\n"
                "/goodbye - Show your goodbye message\n"
                "/goodbye [on, y, true, enable, t] - to enable goodbye messages\n"
                "/goodbye [off, n, false, disable, f, no] - to disable goodbye messages\n"
                "/delgoodbye or /deletegoodbye - to delete the goodbye message and disable it"
            )
    else:
        await message.reply_text(
            "Invalid command. Please use:\n"
            "/goodbye - Show your goodbye message\n"
            "/goodbye [on, y, true, enable, t] - to enable goodbye messages\n"
            "/goodbye [off, n, false, disable, f, no] - to disable goodbye messages\n"
            "/delgoodbye or /deletegoodbye - to delete the goodbye message and disable it"
        )


async def get_goodbye_func(_, message: Message):
    chat = message.chat
    goodbye, raw_text, file_id = await get_goodbye(chat.id)
    if not raw_text:
        return await message.reply_text("You forgot to set a goodbye message.")
    if not message.from_user:
        return await message.reply_text("You are anonymous; I can't show the goodbye message.")

    await send_left_message(chat, message.from_user.id)
    is_grt = await is_greetings_on(chat.id, "goodbye")
    text = "Enabled" if is_grt else "Disabled"
    await message.reply_text(
        f"Currently saying goodbye to members: {text}\nGoodbye type: {goodbye}\n\nFile ID: `{file_id}`\n\n`{raw_text.replace('`', '')}`"
    )


__MODULE__ = "Goodbye"
__HELP__ = """
Goodbye Help:

/setgoodbye - Reply to a message with proper formatting to set a goodbye message.

/goodbye - Show your currently set goodbye message.

/goodbye [on, y, true, enable, t] - Enable goodbye messages.

/goodbye [off, n, false, disable, f, no] - Disable goodbye messages.

/delgoodbye or /deletegoodbye - Delete the goodbye message and disable it.

**Set Goodbye Message ->**

To set a photo or gif as the goodbye message, reply with the goodbye text as the caption. The caption must follow the format below.

For text messages, send the text and reply to it using the command.

Format:
Hello {NAME} [{ID}], welcome to {GROUPNAME}

~ #This separator (~) should be between the text and buttons. Remove this line when using.

Button1=[Duck, https://duckduckgo.com]  
Button2=[GitHub, https://github.com]

**NOTES ->**  
Check /markdownhelp for formatting help and advanced syntax Related knowledge.
"""
