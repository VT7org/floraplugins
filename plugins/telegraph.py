import os

from TheApi import api
from WinxMusic import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@app.on_message(filters.command(["tgm", "tgt", "telegraph", "tg"]))
async def get_link_group(client, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ Please reply to a media file to upload it to Telegraph 📤"
        )

    media = message.reply_to_message
    file_size = 0
    if media.photo:
        file_size = media.photo.file_size
    elif media.video:
        file_size = media.video.file_size
    elif media.document:
        file_size = media.document.file_size

    if file_size > 15 * 1024 * 1024:
        return await message.reply_text(
            "⚠️ Please send a media file smaller than 15MB."
        )

    try:
        text = await message.reply("🔄 Processing...")

        async def progress(current, total):
            try:
                await text.edit_text(f"📥 Downloading... {current * 100 / total:.1f}%")
            except Exception:
                pass

        try:
            local_path = await media.download(progress=progress)
            await text.edit_text("📤 Uploading to Telegraph...")

            upload_path = api.upload_image(local_path)

            await text.edit_text(
                f"🌐 | [Upload Link]({upload_path})",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "📂 View File",
                                url=upload_path,
                            )
                        ]
                    ]
                ),
            )

            try:
                os.remove(local_path)
            except Exception:
                pass

        except Exception as e:
            await text.edit_text(f"❌ Failed to upload file\n\n<i>Reason: {e}</i>")
            try:
                os.remove(local_path)
            except Exception:
                pass
            return
    except Exception:
        pass



__MODULE__ = "📎Telegraph"
__HELP__ = """
**Telegraph Upload Commands**

Use these commands to upload media files to [Telegraph](https://telegra.ph):

- `/tgm`: Uploads the replied media to Telegraph.
- `/tgt`: Same as `/tgm`.
- `/telegraph`: Same as `/tgm`.
- `/tg`: Same as `/tgm`.

**Example:**
- Reply to a photo or video with `/tgm` to upload it to Telegraph.

**Note:**
You must reply to a media file for the upload to work.
"""
