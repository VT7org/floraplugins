import re
import requests
from WinxMusic import app
from config import LOG_GROUP_ID
from pyrogram import filters
from pyrogram.types import Message


@app.on_message(filters.command(["ig", "insta", "reel"]))
async def download_instagram_video(_, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "Please provide the Instagram reel URL after the command. 📲"
        )
        return

    url = message.text.split()[1]
    if not re.match(
        re.compile(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"), url
    ):
        return await message.reply_text(
            "The URL you provided is not a valid Instagram link."
        )

    status_msg = await message.reply_text("Processing... ⏳")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    response = requests.get(api_url)
    try:
        result = response.json()
        data = result["result"]
    except Exception as e:
        error_text = f"Error occurred Please Share Reels Url:\n{e} ❌"
        try:
            await status_msg.edit(error_text)
        except Exception:
            await message.reply_text(error_text)
            return await app.send_message(LOG_GROUP_ID, error_text)
        return await app.send_message(LOG_GROUP_ID, error_text)

    if not result["error"]:
        video_url = data["url"]
        duration = data["duration"]
        quality = data["quality"]
        extension = data["extension"]
        size = data["formattedSize"]

        caption = (
            f"**Duration:** {duration} 🕒\n"
            f"**Quality:** {quality} 📹\n"
            f"**Format:** {extension} 🎥\n"
            f"**File Size:** {size} 💾"
        )

        await status_msg.delete()
        await message.reply_video(video_url, caption=caption)
    else:
        try:
            return await status_msg.edit("Failed to download the reel ❗")
        except Exception:
            return await message.reply_text("Failed to download the reel ❗")


__MODULE__ = "📲Instagram Reels"
__HELP__ = """
**Instagram Reel Downloader:**

• `/ig [URL]`: Downloads reels from Instagram. Provide the reel URL after the command.
• `/insta [URL]`: Same as above.
• `/reel [URL]`: Same as above.

⚠️ Ensure the URL is from a valid Instagram reel post.
"""
