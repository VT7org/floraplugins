import asyncio

from WinxMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

SPAM_CHATS = []


async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]
    return user_id in admin_ids


@app.on_message(
    filters.command(["all", "allmention", "mentionall", "tagall"], prefixes=["/", "@"])
)
async def tag_all_users(_, message):
    admin = await is_admin(message.chat.id, message.from_user.id)
    if not admin:
        return

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "🔴 A mention process is already running! If you want to stop it, use /cancel."
        )

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        await message.reply_text(
            "🔹 **You need to provide a message to tag everyone, like »** `@all Hello everyone!`"
        )
        return

    if replied:
        usernum = 0
        usertxt = ""
        try:
            SPAM_CHATS.append(message.chat.id)
            async for m in app.get_chat_members(message.chat.id):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                usernum += 1
                usertxt += f"[{m.user.first_name}](tg://user?id={m.user.id})  "
                if usernum == 7:
                    await replied.reply_text(usertxt, disable_web_page_preview=True)
                    await asyncio.sleep(1)
                    usernum = 0
                    usertxt = ""
            if usernum != 0:
                await replied.reply_text(usertxt, disable_web_page_preview=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        finally:
            try:
                SPAM_CHATS.remove(message.chat.id)
            except Exception:
                pass
    else:
        try:
            usernum = 0
            usertxt = ""
            text = message.text.split(None, 1)[1]
            SPAM_CHATS.append(message.chat.id)
            async for m in app.get_chat_members(message.chat.id):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                usernum += 1
                usertxt += f"[{m.user.first_name}](tg://user?id={m.user.id})  "
                if usernum == 7:
                    await app.send_message(
                        message.chat.id, f"{text}\n{usertxt}", disable_web_page_preview=True
                    )
                    await asyncio.sleep(2)
                    usernum = 0
                    usertxt = ""
            if usernum != 0:
                await app.send_message(
                    message.chat.id, f"{text}\n\n{usertxt}", disable_web_page_preview=True
                )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        finally:
            try:
                SPAM_CHATS.remove(message.chat.id)
            except Exception:
                pass


async def tag_all_admins(_, message):
    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "🔴 A mention process is already running! If you want to stop it, use /cancel."
        )

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        await message.reply_text(
            "🔹 **You need to provide a message to tag all admins, like »** `@admins Hello team!`"
        )
        return

    if replied:
        usernum = 0
        usertxt = ""
        try:
            SPAM_CHATS.append(message.chat.id)
            async for m in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                usernum += 1
                usertxt += f"[{m.user.first_name}](tg://user?id={m.user.id})  "
                if usernum == 7:
                    await replied.reply_text(usertxt, disable_web_page_preview=True)
                    await asyncio.sleep(1)
                    usernum = 0
                    usertxt = ""
            if usernum != 0:
                await replied.reply_text(usertxt, disable_web_page_preview=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        finally:
            try:
                SPAM_CHATS.remove(message.chat.id)
            except Exception:
                pass
    else:
        usernum = 0
        usertxt = ""
        try:
            text = message.text.split(None, 1)[1]
            SPAM_CHATS.append(message.chat.id)
            async for m in app.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                if message.chat.id not in SPAM_CHATS:
                    break
                if m.user.is_deleted or m.user.is_bot:
                    continue
                usernum += 1
                usertxt += f"[{m.user.first_name}](tg://user?id={m.user.id})  "
                if usernum == 7:
                    await app.send_message(
                        message.chat.id, f"{text}\n{usertxt}", disable_web_page_preview=True
                    )
                    await asyncio.sleep(2)
                    usernum = 0
                    usertxt = ""
            if usernum != 0:
                await app.send_message(
                    message.chat.id, f"{text}\n\n{usertxt}", disable_web_page_preview=True
                )
        except FloodWait as e:
            await asyncio.sleep(e.value)
        finally:
            try:
                SPAM_CHATS.remove(message.chat.id)
            except Exception:
                pass


@app.on_message(
    filters.command(
        [
            "stopmention",
            "cancel",
            "cancelmention",
            "offmention",
            "mentionoff",
            "cancelall",
        ],
        prefixes=["/", "@"],
    )
)
async def cancelcmd(_, message):
    chat_id = message.chat.id
    admin = await is_admin(chat_id, message.from_user.id)
    if not admin:
        return

    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass
        return await message.reply_text(
            "🛑 **Mention process stopped successfully!**"
        )
    else:
        await message.reply_text("⚠️ **No active mention process found!**")
        return


__MODULE__ = "🔹Tag-All"
__HELP__ = """
@all or /all | /tagall or @tagall | /mentionall or @mentionall [text] or [reply to any message] – Mention all group members 🤖

/admins | @admins | /report [text] or [reply to any message] – Mention all group administrators 👮

/cancel or @cancel | /offmention or @offmention | /mentionoff or @mentionoff | /cancelall or @cancelall – Stop any ongoing mention process ❌

**__Note__** This command can only be used by chat administrators. Ensure both the bot and the assistant are administrators in your group 🔒
"""

                
