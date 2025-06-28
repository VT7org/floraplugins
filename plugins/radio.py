import asyncio
import logging

from WinxMusic import app
from WinxMusic.utils.database import get_assistant
from config import BANNED_USERS
from pyrogram import filters, Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import Message

RADIO_STATION = {
    "Air Bilaspur": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio110/playlist.m3u8",
    "Air Raipur": "http://air.pc.cdn.bitgravity.com/air/live/pbaudio118/playlist.m3u8",
    "Capital FM": "http://media-ice.musicradio.com/CapitalMP3?.mp3&listening-from-radio-garden=1616312105154",
    "English": "https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8",
    "Mirchi": "http://peridot.streamguys.com:7150/Mirchi",
    "Radio Today": "http://stream.zenolive.com/8wv4d8g4344tv",
    "Retro Bollywood": "https://stream.zeno.fm/g372rxef798uv",
    "Hits Of Bollywood": "https://stream.zeno.fm/60ef4p33vxquv",
    "Dhol Radio": "https://radio.dholradio.co:8000/radio.mp3",
    "City 91.1 FM": "https://prclive1.listenon.in/",
    "Radio Udaan": "http://173.212.234.220/radio/8000/radio.mp3",
    "All India Radio Patna": "https://air.pc.cdn.bitgravity.com/air/live/pbaudio087/playlist.m3u8",
    "Mirchi 98.3 FM": "https://playerservices.streamtheworld.com/api/livestream-redirect/NJS_HIN_ESTAAC.m3u8",
    "Hungama 90s Once Again": "https://stream.zeno.fm/rm4i9pdex3cuv",
    "Hungama Evergreen Bollywood": "https://server.mixify.in:8010/radio.mp3"
}

valid_stations = "\n".join([f"`{name}`" for name in sorted(RADIO_STATION.keys())])


@app.on_message(
    filters.command(["radioplayforce", "radio", "cradio"])
    & filters.group
    & ~BANNED_USERS
)
async def radio(client: Client, message: Message):
    msg = await message.reply_text("Please wait a moment... ⏳")
    try:
        try:
            userbot = await get_assistant(message.chat.id)
            get = await app.get_chat_member(message.chat.id, userbot.id)
        except ChatAdminRequired:
            return await msg.edit_text(
                f"❗ Missing permission to invite assistant {userbot.mention} to the group {message.chat.title}."
            )
        if get.status == ChatMemberStatus.BANNED:
            return await msg.edit_text(
                text=f"⚠️ Assistant {userbot.mention} is banned in {message.chat.title}\n\nPlease unban to proceed..."
            )
    except UserNotParticipant:
        if message.chat.username:
            invitelink = message.chat.username
            try:
                await userbot.resolve_peer(invitelink)
            except Exception as ex:
                logging.exception(ex)
        else:
            try:
                invitelink = await client.export_chat_invite_link(message.chat.id)
            except ChatAdminRequired:
                return await msg.edit_text(
                    f"❗ Missing permission to invite {userbot.mention} to the group {message.chat.title}."
                )
            except Exception as ex:
                return await msg.edit_text(
                    f"Error: Failed to invite {userbot.mention}.\n\nReason: `{ex}`"
                )
        if invitelink.startswith("https://t.me/+"):
            invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
        anon = await msg.edit_text(
            f"🔄 Inviting {userbot.mention} to {message.chat.title}..."
        )
        try:
            await userbot.join_chat(invitelink)
            await asyncio.sleep(2)
            await msg.edit_text(
                f"🎉 {userbot.mention} successfully joined, starting the broadcast..."
            )
        except Exception as ex:
            if "channels.JoinChannel" in str(ex) or "Username not found" in str(ex):
                return await msg.edit_text(
                    f"⚠️ Missing permission to invite {userbot.mention} to {message.chat.title}."
                )
            else:
                return await msg.edit_text(f"Invite error: `{ex}`")

    await msg.delete()
    station_name = " ".join(message.command[1:])
    RADIO_URL = RADIO_STATION.get(station_name)
    if RADIO_URL:
        await message.reply_text(
            f"📻 Playing: `{station_name}`"
        )
    else:
        await message.reply(
            f"🎶 To listen, choose an available radio station:\n{valid_stations}"
        )


__MODULE__ = "📻Radio"
__HELP__ = f"""
/radio [station] - Broadcast a radio station in the group! 📻
Available stations:
{valid_stations}
"""
