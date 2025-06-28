import re

from WinxMusic import app
from WinxMusic.utils.database import (
    deleteall_filters,
    get_filters_names,
    save_filter,
)
from WinxMusic.utils.functions import (
    check_format,
    get_data_and_name,
)
from WinxMusic.utils.keyboard import ikb
from config import BANNED_USERS
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup, Message, CallbackQuery,
)

from utils.error import capture_err
from utils.permissions import admins_only, member_permissions
from .notes import extract_urls


@app.on_message(filters.command("filter") & ~filters.private & ~BANNED_USERS)
@admins_only("can_change_info")
async def save_filters(_, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "**Usage:**\nReply to a message with /filter [FILTER_NAME] [CONTENT] to set a new filter."
            )
        replied_message = message.reply_to_message
        if not replied_message:
            replied_message = message
        data, name = await get_data_and_name(replied_message, message)
        if len(name) < 2:
            return await message.reply_text(
                f"For the filter, {name} must have more than 2 words."
            )
        if data == "error":
            return await message.reply_text(
                "**Usage:**\n__/filter [FILTER_NAME] [CONTENT]__\n`-----------OR-----------`\nReply to a message with. \n/filter [FILTER_NAME]."
            )
        if replied_message.text:
            _type = "text"
            file_id = None
        if replied_message.sticker:
            _type = "sticker"
            file_id = replied_message.sticker.file_id
        if replied_message.animation:
            _type = "animation"
            file_id = replied_message.animation.file_id
        if replied_message.photo:
            _type = "photo"
            file_id = replied_message.photo.file_id
        if replied_message.document:
            _type = "document"
            file_id = replied_message.document.file_id
        if replied_message.video:
            _type = "video"
            file_id = replied_message.video.file_id
        if replied_message.video_note:
            _type = "video_note"
            file_id = replied_message.video_note.file_id
        if replied_message.audio:
            _type = "audio"
            file_id = replied_message.audio.file_id
        if replied_message.voice:
            _type = "voice"
            file_id = replied_message.voice.file_id
        if replied_message.reply_markup and not re.findall(r"\[.+\,.+\]", data):
            urls = extract_urls(replied_message.reply_markup)
            if urls:
                response = "\n".join(
                    [f"{name}=[{text}, {url}]" for name, text, url in urls]
                )
                data = data + response
        if data:
            data = await check_format(ikb, data)
            if not data:
                return await message.reply_text(
                    "**Incorrect formatting, check the help section.**"
                )
        name = name.replace("_", " ")
        _filter = {
            "type": _type,
            "data": data,
            "file_id": file_id,
        }

        chat_id = message.chat.id
        await save_filter(chat_id, name, _filter)
        return await message.reply_text(f"__**Filter {name} saved successfully.**__")
    except UnboundLocalError:
        return await message.reply_text(
            "**Replied message is inaccessible.\nResend the message and try again.**"
        )


@app.on_message(filters.command("filters") & ~filters.private & ~BANNED_USERS)
@capture_err
async def get_filterss(_, message: Message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        return await message.reply_text("**No filters in this chat.**")
    _filters.sort()
    msg = f"List of filters in **{message.chat.title}**:\n"
    for _filter in _filters:
        msg += f"**-** `{_filter}`\n"
    await message.reply_text(msg)


@app.on_message(filters.command("stopall") & ~filters.private & ~BANNED_USERS)
@admins_only("can_change_info")
async def stop_all(_, message: Message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        await message.reply_text("**No filters in this chat.**")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Yes, do it", callback_data="stop_yes"),
                    InlineKeyboardButton("No, don't do it", callback_data="stop_no"),
                ]
            ]
        )
        await message.reply_text(
            "**Are you sure you want to delete all filters in this chat permanently?**",
            reply_markup=keyboard,
        )


@app.on_callback_query(filters.regex("stop_(.*)") & ~BANNED_USERS)
async def stop_all_cb(_, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_change_info"
    if permission not in permissions:
        return await callback_query.answer(
            f"You do not have the required permission.\nPermission: {permission}",
            show_alert=True,
        )
    input = callback_query.data.split("_", 1)[1]
    if input == "yes":
        stoped_all = await deleteall_filters(chat_id)
        if stoped_all:
            return await callback_query.message.edit(
                "**All filters deleted successfully in this chat.**"
            )
    if input == "no":
        await callback_query.message.reply_to_message.delete()
        await callback_query.message.delete()


__MODULE__ = "Filters"
__HELP__ = """
**🗃️ Filter Commands:**

• /filters - **Get all filters in the chat.**

• /filter [FILTER_NAME] - **Save a filter** (reply to a message).

📎 **Supported Filter Types:**
Text, Animation, Photo, Document, Video, Video Notes, Audio, Voice.

✨ **Tip:** To use multiple words in a filter, use:
`/filter Hi_how_are_you` to filter "Hi how are you".

• /stop [FILTER_NAME] - **Stop a filter.**

• /stopall - **Delete all filters in a chat (permanently).**

📐 **Advanced Formatting:**
You can use markdown or HTML to save text as well. See /markdownhelp for more information on formatting and other syntaxes.
"""
