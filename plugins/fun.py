import requests
from WinxMusic import app
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


@app.on_message(
    filters.command(
        [
            "dice",
            "ludo",
            "dart",
            "basket",
            "basketball",
            "football",
            "slot",
            "bowling",
            "jackpot",
        ]
    )
)
async def dice(client: Client, message: Message):
    command = message.text.split()[0]
    if command == "/dice" or command == "/ludo":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔄", callback_data="send_dice")]]
        )
        value = await client.send_dice(message.chat.id, reply_markup=keyboard)

    elif command == "/dart":
        value = await client.send_dice(message.chat.id, emoji="🎯", reply_to_message_id=message.id)
        await value.reply_text("Your score is: {0}".format(value.dice.value))

    elif command == "/basket" or command == "/basketball":
        basket = await client.send_dice(message.chat.id, emoji="🏀", reply_to_message_id=message.id)
        await basket.reply_text("Your score is: {0}".format(basket.dice.value))

    elif command == "/football":
        value = await client.send_dice(message.chat.id, emoji="⚽", reply_to_message_id=message.id)
        await value.reply_text("Your score is: {0}".format(value.dice.value))

    elif command == "/slot" or command == "/jackpot":
        value = await client.send_dice(message.chat.id, emoji="🎰", reply_to_message_id=message.id)
        await value.reply_text("Your score is: {0}".format(value.dice.value))

    elif command == "/bowling":
        value = await client.send_dice(message.chat.id, emoji="🎳", reply_to_message_id=message.id)
        await value.reply_text("Your score is: {0}".format(value.dice.value))


bored_api_url = "https://apis.scrimba.com/bored/api/activity"


@app.on_message(filters.command("bored", prefixes="/"))
async def bored_command(_client: Client, message):
    response = requests.get(bored_api_url)
    if response.status_code == 200:
        data = response.json()
        activity = data.get("activity")
        if activity:
            await message.reply(f"🌀 **Feeling bored? How about:**\n\n{activity}")
        else:
            await message.reply("⚠️ **No activity found.**")
    else:
        await message.reply("❌ **Could not retrieve an activity.**")


@app.on_callback_query(filters.regex(r"send_dice"))
async def dice_again(client: Client, callback_query: CallbackQuery):
    try:
        await app.edit_message_text(
            callback_query.message.chat.id, callback_query.message.id, callback_query.message.dice.emoji
        )
    except BaseException:
        pass
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄", callback_data="send_dice")]]
    )
    await client.send_dice(callback_query.message.chat.id, reply_markup=keyboard)


__MODULE__ = "🎉 Fun"
__HELP__ = """
**For fun:**

• `/dice`: 🎲 **Roll a dice.**
• `/ludo`: 🎲 **Play Ludo.**
• `/dart`: 🎯 **Throw a dart.**
• `/basket` or `/basketball`: 🏀 **Play Basketball.**
• `/football`: ⚽ **Play Football.**
• `/slot` or `/jackpot`: 🎰 **Play Jackpot.**
• `/bowling`: 🎳 **Play Bowling.**
• `/bored`: 🌀 **Get a random activity if you're feeling bored.**
"""
