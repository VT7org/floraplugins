import asyncio
from random import choice

import pyfiglet
from WinxMusic import app
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


def figle(text):
    x = pyfiglet.FigletFont.getFonts()
    font = choice(x)
    figled = str(pyfiglet.figlet_format(text, font=font))
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="🔄 **Change**", callback_data="figlet"),
                InlineKeyboardButton(text="❌ **Close**", callback_data="close_reply"),
            ]
        ]
    )
    return figled, keyboard


@app.on_message(filters.command("figlet"))
async def echo(bot, message):
    global text
    try:
        text = message.text.split(" ", 1)[1]
    except IndexError:
        return await message.reply_text("💡 **Usage example:**\n\n`/figlet OpenAI`")
    kul_text, keyboard = figle(text)
    await message.reply_text(
        f"🎨 **Here is your Figlet:**\n<pre>{kul_text}</pre>",
        quote=True,
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex("figlet"))
async def figlet_handler(Client, query: CallbackQuery):
    try:
        kul_text, keyboard = figle(text)
        await query.message.edit_text(
            f"🎨 **Here is your Figlet:**\n<pre>{kul_text}</pre>", reply_markup=keyboard
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        return await query.answer(str(e), show_alert=True)


__MODULE__ = "🎨 Figlet"
__HELP__ = """
**Figlet**

• /figlet <text> - **Create a Figlet from the provided text.**
"""
