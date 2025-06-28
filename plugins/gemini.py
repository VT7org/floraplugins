import requests
from MukeshAPI import api
from WinxMusic import app
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from pyrogram.types import Message


@app.on_message(filters.command(["gemini"]))
async def gemini_handler(_client: Client, message: Message):
    await app.send_chat_action(message.chat.id, ChatAction.TYPING)
    if (
            message.text.startswith(f"/gemini@{app.username}")
            and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text("Example: `/gemini who is Lord Ram`")
            return

    try:
        response = api.gemini(user_input)
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        x = response["results"]
        if x:
            await message.reply_text(x, quote=True)
        else:
            await message.reply_text("Sorry! Please try again.")
    except requests.exceptions.RequestException as e:
        await message.reply_text("Failed to process the request From Gemini.")
        
