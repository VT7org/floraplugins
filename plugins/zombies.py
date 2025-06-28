import asyncio

from WinxMusic import app
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from utils.permissions import admins_only

chat_queue = []

stop_process = False


@app.on_message(filters.command(["zombies"]))
@admins_only("can_restrict_members")
async def remove(_, message: Message):
    global stop_process
    try:
        try:
            sender = await app.get_chat_member(message.chat.id, message.from_user.id)
            has_permissions = sender.privileges
        except BaseException:
            has_permissions = message.sender_chat

        if has_permissions:
            bot = await app.get_chat_member(message.chat.id, "self")
            if bot.status == ChatMemberStatus.MEMBER:
                await message.reply(
                    "🚨 | **I need admin rights to remove deleted accounts.**"
                )
            else:
                if len(chat_queue) > 30:
                    await message.reply(
                        "⚠️ | **Currently handling the max limit of 30 chats. Try again later!**"
                    )
                else:
                    if message.chat.id in chat_queue:
                        await message.reply(
                            "🔄 | **A cleanup is already running in this chat. Use `/stop` to interrupt.**"
                        )
                    else:
                        chat_queue.append(message.chat.id)
                        deletedList = []
                        async for member in app.get_chat_members(message.chat.id):
                            if member.user.is_deleted:
                                deletedList.append(member.user)
                        lenDeletedList = len(deletedList)
                        if lenDeletedList == 0:
                            await message.reply(
                                "✔️ | **No deleted accounts found in this chat.**")
                            chat_queue.remove(message.chat.id)
                        else:
                            k = 0
                            processTime = lenDeletedList * 1
                            temp = await app.send_message(
                                message.chat.id,
                                f"🧭 | **Found {lenDeletedList} deleted accounts.**\n⏳ | **Estimated time:** {processTime} seconds."
                            )
                            if stop_process:
                                stop_process = False
                            while len(deletedList) > 0 and not stop_process:
                                deletedAccount = deletedList.pop(0)
                                try:
                                    await app.ban_chat_member(
                                        message.chat.id, deletedAccount.id
                                    )
                                except FloodWait as e:
                                    await asyncio.sleep(e.value)
                                except Exception:
                                    pass
                                k += 1
                            if k == lenDeletedList:
                                await message.reply(
                                    f"✅ | **Successfully removed all deleted accounts from this chat.**"
                                )
                                await temp.delete()
                            else:
                                await message.reply(
                                    f"✅ | **Removed {k} deleted accounts from this chat.**"
                                )
                                await temp.delete()
                            chat_queue.remove(message.chat.id)
        else:
            await message.reply(
                "👮🏻 | **Only admins can use this command.**"
            )
    except FloodWait as e:
        await asyncio.sleep(e.value)


__MODULE__ = "🧟‍♂️Gc Cleaner"
__HELP__ = """
**🧹 Deleted Account Cleanup**

• /zombies - **Remove deleted accounts from the group.**

**Details:**
- Module: Deleted Account Removal
- Required Permission: Can restrict members

**Note:**
- Use this command directly in the group chat for best results.
- Only group admins can run this command.
"""
