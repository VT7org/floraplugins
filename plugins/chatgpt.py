from TheApi import api
from WinxMusic import app
from config import BANNED_USERS
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from pyrogram.types import Message


@app.on_message(filters.command(["chatgpt", "ai", "ask"]) & ~BANNED_USERS)
async def chatgpt_chat(bot: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "💡 **Usage example:**\n\n`/ai Who is the Veer Savarkar"
        )
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    results = api.chatgpt(user_input)
    await message.reply_text(f"🤖 **Response:**\n\n{results}")


__MODULE__ = "Intelligence"
__HELP__ = """
**Commands:**

• /advice - **Get a random piece of advice from the bot**
• /ai [your question] - **Ask a question to ChatGPT AI**
• /gemini [your question] - **Ask a question to Google's Gemini AI**
"""
