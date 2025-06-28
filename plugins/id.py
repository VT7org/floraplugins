from WinxMusic import app
from pyrogram import filters
from pyrogram.types import Message


@app.on_message(filters.command("id"))
async def get_id(_, message: Message):
    try:
        if not message.reply_to_message and message.chat:
            await message.reply(
                f"👤 User <b>{message.from_user.first_name}'s</b> ID is <code>{message.from_user.id}</code>.\n"
                f"💬 This chat's ID is: <code>{message.chat.id}</code>."
            )

        elif not message.reply_to_message.sticker or message.reply_to_message is None:
            if message.reply_to_message.forward_from_chat:
                await message.reply(
                    f"📥 The forwarded channel, {message.reply_to_message.forward_from_chat.title}, has ID: "
                    f"<code>{message.reply_to_message.forward_from_chat.id}</code>."
                )

            elif message.reply_to_message.forward_from:
                await message.reply(
                    f"👤 The forwarded user, {message.reply_to_message.forward_from.first_name}, has ID: "
                    f"<code>{message.reply_to_message.forward_from.id}</code>."
                )

            elif message.reply_to_message.forward_sender_name:
                await message.reply("❗ Sorry, the user's ID could not be retrieved.")
            else:
                await message.reply(
                    f"👤 User {message.reply_to_message.from_user.first_name} has ID: "
                    f"<code>{message.reply_to_message.from_user.id}</code>."
                )

        elif message.reply_to_message.sticker:
            if message.reply_to_message.forward_from_chat:
                await message.reply(
                    f"📥 The forwarded channel, {message.reply_to_message.forward_from_chat.title}, has ID: "
                    f"<code>{message.reply_to_message.forward_from_chat.id}</code>\n"
                    f"🖼️ The sticker's file ID is <code>{message.reply_to_message.sticker.file_id}</code>."
                )

            elif message.reply_to_message.forward_from:
                await message.reply(
                    f"👤 The forwarded user, {message.reply_to_message.forward_from.first_name}, has ID: "
                    f"<code>{message.reply_to_message.forward_from.id}</code>\n"
                    f"🖼️ The sticker's file ID is <code>{message.reply_to_message.sticker.file_id}</code>."
                )

            elif message.reply_to_message.forward_sender_name:
                await message.reply("❗ Sorry, the user's ID could not be retrieved.")
            else:
                await message.reply(
                    f"👤 User {message.reply_to_message.from_user.first_name} has ID: "
                    f"<code>{message.reply_to_message.from_user.id}</code>\n"
                    f"🖼️ The sticker's file ID is <code>{message.reply_to_message.sticker.file_id}</code>."
                )

        else:
            await message.reply(
                f"👤 User {message.reply_to_message.from_user.first_name} has ID: "
                f"<code>{message.reply_to_message.from_user.id}</code>."
            )

    except Exception as e:
        await message.reply(f"⚠️ An error occurred while fetching the ID.\n`{e}`")


__MODULE__ = "User-Info"
__HELP__ = """
**📘 ID Retriever:**

• `/id` — Get the ID of a user, chat, sticker, or forwarded message.
"""
