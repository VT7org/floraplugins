import nekos
from WinxMusic import app
from pyrogram import filters
from pyrogram.types import Message


@app.on_message(filters.command("hug"))
async def hug(_, message: Message):
    try:
        if message.reply_to_message:
            await message.reply_video(
                nekos.img("hug"),
                caption=f"{message.from_user.mention} gave a warm hug to {message.reply_to_message.from_user.mention} 🤗",
            )
        else:
            await message.reply_video(
                nekos.img("hug"), caption="Here's a warm hug just for you! 🤗"
            )
    except Exception as e:
        await message.reply_text(f"Error: {e}")


__MODULE__ = "🫂 Hug"
__HELP__ = """
**🤗 Hug Command:**

• `/hug`: Sends a hugging animation. If used as a reply, it will tag the sender and the recipient of the hug.

**Usage Instructions:**

• Use `/hug` to send a hug animation.
• Reply to a user's message with `/hug` to hug them directly.

**Note:**

• Make sure your chat settings allow the bot to send videos for this to work properly.
"""
