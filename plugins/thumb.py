import re

from WinxMusic import app
from pyrogram import filters
from youtubesearchpython.__future__ import VideosSearch


async def gen_infos(url):
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
        title = result["title"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return title, thumbnail


def is_url(url):
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.match(regex, url)
    if match:
        return True, match.group(1)
    return False, None


@app.on_message(
    filters.command(["getthumb", "genthumb", "thumb", "thumbnail"], prefixes="/")
)
async def get_thumbnail_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ Please provide a YouTube video link after the command to get its thumbnail 📷"
        )
    try:
        a = await message.reply_text("⏳ Processing...")
        url = message.text.split(" ")[1]
        i, video_id = is_url(url)
        if not i:
            return await a.edit("❌ Please provide a valid YouTube link. 🔗")

        title, thumb = await gen_infos(url)
        caption = f"<b>[{title}](https://t.me/{app.username}?start=info_{video_id})</b>"
        await message.reply_photo(thumb, caption=caption)
        await a.delete()
    except Exception as e:
        await a.edit(f"❌ An error occurred: {e}")



__MODULE__ = "📷YT Thumbnail"
__HELP__ = """
**YouTube Thumbnail Bot Commands 📺**

Use these commands to fetch the thumbnail of any YouTube video:

- `/getthumb <yt_link>`: Get the 2k/4k thumbnail of a YouTube video 🖼️.
- `/genthumb <yt_link>`: Same as `/getthumb`.
- `/thumb <yt_link>`: Same as `/getthumb`.
- `/thumbnail <yt_link>`: Same as `/getthumb`.

**Example:**
- `/getthumb https://www.youtube.com/watch?v=Tl4bQBfOtbg`

**Note:**
You must provide a valid YouTube video link after the command to fetch the thumbnail.
"""
