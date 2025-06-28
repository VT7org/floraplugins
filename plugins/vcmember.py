from WinxMusic import app
from WinxMusic.utils import winxbin
from WinxMusic.utils.database import get_assistant, get_lang
from pyrogram import filters
from pyrogram.enums import ChatType
from strings import get_string


@app.on_message(
    filters.command(["vcuser", "vcusers", "vcmember", "vcmembers"]) & filters.admin
)
async def vc_members(client, message):
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except:
        _ = get_string("en")

    msg = await message.reply_text(
        "🚫 Sorry! The bot allows a limited number of video calls due to CPU overload. "
        "Too many chats are using video at the moment. Try switching to audio or try again later. 🎙️"
    )

    userbot = await get_assistant(message.chat.id)
    TEXT = ""

    try:
        async for m in userbot.get_call_members(message.chat.id):
            chat_id = m.chat.id
            username = m.chat.username
            is_hand_raised = "🙋‍♂️" if m.is_hand_raised else "✋"
            is_video_enabled = "📹" if m.is_video_enabled else "📵"
            is_left = "🚶‍♂️" if m.is_left else "🔊"
            is_screen_sharing_enabled = "🖥️" if m.is_screen_sharing_enabled else "❌"
            is_muted = "🔇" if bool(m.is_muted and not m.can_self_unmute) else "🔈"
            is_speaking = "💬" if not m.is_muted else "🤐"

            if m.chat.type != ChatType.PRIVATE:
                title = m.chat.title
            else:
                try:
                    title = (await client.get_users(chat_id)).mention
                except:
                    title = m.chat.first_name

            TEXT += (
                f"👤 User: {title}\n"
                f"🆔 ID: {chat_id}\n"
                f"🔗 Username: {username}\n"
                f"📹 Video: {is_video_enabled}\n"
                f"🖥️ Screen Sharing: {is_screen_sharing_enabled}\n"
                f"🙋 Hand Raised: {is_hand_raised}\n"
                f"🔈 Muted: {is_muted}\n"
                f"💬 Speaking: {is_speaking}\n"
                f"🚶 Left: {is_left}\n\n"
            )

        if len(TEXT) < 4000:
            await msg.edit(TEXT or "⚠️ No members found in the voice chat.")
        else:
            link = await winxbin(TEXT)
            await msg.edit(
                f"📄 Voice chat member list is too long. View here: {link}",
                disable_web_page_preview=True,
            )
    except ValueError:
        await msg.edit("❗ Error: Failed to fetch the voice chat members.")


__MODULE__ = "VC-Users"
__HELP__ = """
**🎙️ Voice Chat User Commands:**

Use these commands to list all members in the current voice chat session:

- `/vcusers` or `/vcmembers` — View all users currently connected to the voice chat.
- Shows information like: video on/off, muted, hand raised, speaking status, etc.

**Example:**
- Just run the command while a voice chat is active in the group.

⚠️ *Bot needs to be in the call and have necessary permissions to view participants.*
"""
    
