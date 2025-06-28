from WinxMusic import app
from pyrogram import filters


@app.on_message(filters.command(["qr"]))
async def write_text(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "**𝗨𝘀𝗮𝗴𝗲**: ➡️ `/qr https://t.me/x_ifeelram`\n📌 Provide a Link or text to generate a QR Code.")
        return
    text = " ".join(message.command[1:])
    photo_url = "https://apis.xditya.me/qr/gen?text=" + text
    await app.send_photo(
        chat_id=message.chat.id, photo=photo_url, caption="✅ Here is Your QR Code! 📲"
    )


__MODULE__ = "Qr Code"

__HELP__ = """
🤖 **This Function Generates QR Codes For Free.**

🔹 **Use The /qr followed by the text or URL you want to encode into your Qr Code.**

📌 **For Example**: `/qr https://t.me/x_ifeelram`

🔍 The Bot will generate a QR Code For the provided Input

⚠️ **Note**: Make sure to include protocols while creating Qr code via Links (`http://` or `https://`) for URLs.

🎉 Enjoy Creating Qr Codes For Hassle-Free!
"""
