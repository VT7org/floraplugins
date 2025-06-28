from pyrogram import enums, filters
from pyrogram.types import Message
from WinxMusic import app
from utils.permissions import admins_only


# REMOVE GROUP PHOTO
@app.on_message(filters.command("removephoto"))
@admins_only("can_change_info")
async def delete_chat_photo(_, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("**This command only works in groups!**")

    msg = await message.reply_text("**Processing...** 🕒")
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.privileges and member.privileges.can_change_info:
            await app.delete_chat_photo(chat_id)
            await msg.edit(f"**Group profile photo removed!**\nBy {message.from_user.mention}")
        else:
            raise PermissionError
    except Exception:
        await msg.edit("**You need permission to change group info in order to remove the photo!**")


# SET GROUP PHOTO
@app.on_message(filters.command("setphoto"))
@admins_only("can_change_info")
async def set_chat_photo(_, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("**This command only works in groups!**")

    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("**Reply to a photo to set it as the new group picture.**")

    msg = await message.reply_text("**Processing...** 🖼️")
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.privileges and member.privileges.can_change_info:
            photo = await message.reply_to_message.download()
            await message.chat.set_photo(photo=photo)
            await msg.edit(f"**Group photo updated successfully!**\nBy {message.from_user.mention}")
        else:
            raise PermissionError
    except Exception:
        await msg.edit("**You need permission to change group info in order to update the photo!**")


# SET GROUP TITLE
@app.on_message(filters.command("settitle"))
@admins_only("can_change_info")
async def set_group_title(_, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("**This command only works in groups!**")

    msg = await message.reply_text("**Processing...** 📝")
    chat_id = message.chat.id
    user_id = message.from_user.id

    title = None
    if message.reply_to_message and message.reply_to_message.text:
        title = message.reply_to_message.text
    elif len(message.command) > 1:
        title = message.text.split(None, 1)[1]

    if not title:
        return await msg.edit("**Please reply with or provide the new group title.**")

    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.privileges and member.privileges.can_change_info:
            await message.chat.set_title(title)
            await msg.edit(f"**Group name updated successfully!**\nBy {message.from_user.mention}")
        else:
            raise PermissionError
    except Exception:
        await msg.edit("**You need permission to change group info in order to update the title!**")


# SET GROUP DESCRIPTION
@app.on_message(filters.command(["setdescription", "setdes"]))
@admins_only("can_change_info")
async def set_group_description(_, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text("**This command only works in groups!**")

    msg = await message.reply_text("**Processing...** 📋")
    chat_id = message.chat.id
    user_id = message.from_user.id

    description = None
    if message.reply_to_message and message.reply_to_message.text:
        description = message.reply_to_message.text
    elif len(message.command) > 1:
        description = message.text.split(None, 1)[1]

    if not description:
        return await msg.edit("**Please reply with or provide a new group description.**")

    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.privileges and member.privileges.can_change_info:
            await message.chat.set_description(description)
            await msg.edit(f"**Group description updated successfully!**\nBy {message.from_user.mention}")
        else:
            raise PermissionError
    except Exception:
        await msg.edit("**You need permission to change group info in order to update the description!**")
        
