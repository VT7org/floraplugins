import asyncio

from WinxMusic import app
from pyrogram import enums, filters, Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message


@app.on_message(filters.command("bots") & filters.group)
async def bots(_client: Client, message: Message):
    try:
        bot_list = []
        async for bot in app.get_chat_members(
                message.chat.id, filter=enums.ChatMembersFilter.BOTS
        ):
            bot_list.append(bot.user)
        len_bot_list = len(bot_list)
        text3 = f"**🤖 Bot List - {message.chat.title}**\n\nBots:\n"
        while len(bot_list) > 1:
            bot = bot_list.pop(0)
            text3 += f"├ @{bot.username}\n"
        else:
            bot = bot_list.pop(0)
            text3 += f"└ @{bot.username}\n\n"
            text3 += f"**Total bots:** {len_bot_list}"
            await app.send_message(message.chat.id, text3)
    except FloodWait as e:
        await asyncio.sleep(e.value)


__MODULE__ = "🤖 Bots"
__HELP__ = """
**Bots**

• /bots - **Get a list of bots in the group.**
"""
