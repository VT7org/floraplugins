import asyncio
from contextlib import suppress
from string import ascii_lowercase
from typing import Dict, Union

from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    ChatPrivileges,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import *
from WinxMusic import app
from WinxMusic.core.mongo import mongodb
from WinxMusic.utils.database import save_filter
from WinxMusic.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
from utils.error import capture_err
from WinxMusic.utils.permissions import adminsOnly, member_permissions

warnsdb = mongodb.warns

__MODULE__ = "Admin Tools"
__HELP__ = """
**Moderation Commands:**

- /ban - 🚷 **Ban a user**
- /sban - 🧹 **Delete all messages from a user and ban them**
- /tban - ⏰ **Ban a user for a specific time**
- /unban - 🔓 **Unban a user**

**Warnings and Notices:**
- /warn - ⚠️ **Warn a user**
- /swarn - 🧹 **Delete all messages from a user and warn them**
- /rmwarn - 🗑️ **Remove all warnings from a user**
- /warns - 📋 **Show a user's warnings**

**Removal Actions:**
- /kick - 🚪 **Kick a user**
- /skick - 🧹 **Delete the message and kick the user**

**Cleanup and Messages:**
- /purge - 🧽 **Clear messages**
- /purge [n] - 🔢 **Clear "n" messages starting from the replied message**
- /del - 🗑️ **Delete the replied message**

**Permission Management:**
- /promote - 🏆 **Promote a member**
- /fullpromote - 🏅 **Promote a member with all rights**
- /demote - ⚙️ **Demote a member**

**Message Pinning:**
- /pin - 📌 **Pin a message**
- /unpin - 📍 **Unpin a message**
- /unpinall - 📍🗑️ **Unpin all messages**

**Mute and Unmute:**
- /mute - 🔇 **Mute a user**
- /tmute - ⏰🔇 **Mute a user for a specific time**
- /unmute - 🔊 **Unmute a user**

**Other Commands:**
- /zombies - 👻 **Ban deleted accounts**
- /report | @admins | @admin - 📢 **Report a message to administrators**
- /link - 🔗 **Send the group/supergroup invite link**
"""

async def int_to_alpha(user_id: int) -> str:
    """Convert a user ID to an alphabetic string using the first 10 lowercase letters."""
    alphabet = list(ascii_lowercase)[:10]
    text = ""
    for digit in str(user_id):
        text += alphabet[int(digit)]
    return text

async def get_warns_count() -> dict:
    """Get the total number of chats and warnings in the database."""
    chats_count = 0
    warns_count = 0
    async for chat in warnsdb.find({"chat_id": {"$lt": 0}}):
        for user in chat["warns"]:
            warns_count += chat["warns"][user]["warns"]
        chats_count += 1
    return {"chats_count": chats_count, "warns_count": warns_count}

async def get_warns(chat_id: int) -> Dict[str, int]:
    """Retrieve all warnings for a specific chat."""
    warns = await warnsdb.find_one({"chat_id": chat_id})
    return warns["warns"] if warns else {}

async def get_warn(chat_id: int, name: str) -> Union[bool, dict]:
    """Get warning details for a specific user in a chat."""
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    return warns.get(name, False)

async def add_warn(chat_id: int, name: str, warn: dict):
    """Add or update a warning for a user in a chat."""
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    warns[name] = warn
    await warnsdb.update_one(
        {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
    )

async def remove_warns(chat_id: int, name: str) -> bool:
    """Remove all warnings for a user in a chat."""
    name = name.lower().strip()
    warns = await get_warns(chat_id)
    if name in warns:
        del warns[name]
        await warnsdb.update_one(
            {"chat_id": chat_id}, {"$set": {"warns": warns}}, upsert=True
        )
        return True
    return False

@app.on_message(filters.command(["kick", "skick"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def kick_func(client: Client, message: Message):
    """Kick a user from the chat, optionally deleting their messages."""
    try:
        user_id, reason = await extract_user_and_reason(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if user_id == client.me.id:
            return await message.reply_text("❌ **I can't kick myself, but I can leave if you want.**")
        if user_id in SUDOERS:
            return await message.reply_text("👑 **Trying to kick a sudo user? Think again!**")
        admins = [member.user.id async for member in client.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )]
        if user_id in admins:
            return await message.reply_text("⚠️ **I can't kick an admin. You know the rules, and so do I.**")

        mention = (await client.get_users(user_id)).mention
        msg = f"""
**🚫 User kicked:** {mention}
**👤 Kicked by:** {message.from_user.mention if message.from_user else 'Anonymous'}
**📄 Reason:** {reason or 'No reason provided'}"""
        
        await message.chat.ban_member(user_id)
        if message.command[0] == "skick":
            if message.reply_to_message:
                await message.reply_to_message.delete()
            await client.delete_user_history(message.chat.id, user_id)
        await message.reply_text(msg)
        await asyncio.sleep(1)
        await message.chat.unban_member(user_id)
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command(["ban", "sban", "tban"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def ban_func(client: Client, message: Message):
    """Ban a user from the chat, with options for silent or temporary bans."""
    try:
        user_id, reason = await extract_user_and_reason(message, sender_chat=True)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if user_id == client.me.id:
            return await message.reply_text("❌ **I can't ban myself, but I can leave if you want.**")
        if user_id in SUDOERS:
            return await message.reply_text("👑 **Trying to ban a sudo user? Think again!**")
        admins = [member.user.id async for member in client.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )]
        if user_id in admins:
            return await message.reply_text("⚠️ **I can't ban an admin. You know the rules, and so do I.**")

        mention = (await client.get_users(user_id)).mention if not message.reply_to_message or not message.reply_to_message.sender_chat else message.reply_to_message.sender_chat.title
        msg = f"""
**🚫 User banned:** {mention}
**👤 Banned by:** {message.from_user.mention if message.from_user else 'Anonymous'}\n"""
        
        if message.command[0] == "sban":
            if message.reply_to_message:
                await message.reply_to_message.delete()
            await client.delete_user_history(message.chat.id, user_id)
        
        if message.command[0] == "tban":
            split = reason.split(None, 1)
            time_value = split[0]
            temp_reason = split[1] if len(split) > 1 else ""
            try:
                temp_ban = await time_converter(message, time_value)
                if len(time_value[:-1]) < 3:
                    msg += f"**⏳ Banned for:** {time_value}\n"
                    if temp_reason:
                        msg += f"**📄 Reason:** {temp_reason}"
                    await message.chat.ban_member(user_id, until_date=temp_ban)
                    await message.reply_text(msg)
                else:
                    await message.reply_text("⚠️ **Cannot use more than 99.**")
                return
            except AttributeError:
                await message.reply_text("⚠️ **Invalid time format.**")
                return
        
        if reason and message.command[0] != "tban":
            msg += f"**📄 Reason:** {reason}"
        await message.chat.ban_member(user_id)
        await message.reply_text(msg)
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command("unban") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def unban_func(client: Client, message: Message):
    """Unban a user from the chat."""
    try:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if message.reply_to_message and message.reply_to_message.sender_chat and message.reply_to_message.sender_chat.id != message.chat.id:
            return await message.reply_text("⚠️ **Cannot unban a channel.**")
        
        await message.chat.unban_member(user_id)
        mention = (await client.get_users(user_id)).mention
        await message.reply_text(f"🔓 **Unbanned!** {mention}")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command(["promote", "fullpromote"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_promote_members")
async def promote_func(client: Client, message: Message):
    """Promote a member to admin, optionally with full privileges."""
    try:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if user_id == client.me.id:
            return await message.reply_text("❌ **I can't promote myself.**")
        
        bot = await client.get_chat_member(message.chat.id, client.me.id)
        if not bot.privileges or not bot.privileges.can_promote_members:
            return await message.reply_text("⚠️ **I don't have sufficient permissions.**")

        mention = (await client.get_users(user_id)).mention
        privileges = ChatPrivileges(
            can_change_info=bot.privileges.can_change_info if message.command[0] == "fullpromote" else False,
            can_invite_users=bot.privileges.can_invite_users,
            can_delete_messages=bot.privileges.can_delete_messages,
            can_restrict_members=bot.privileges.can_restrict_members if message.command[0] == "fullpromote" else False,
            can_pin_messages=bot.privileges.can_pin_messages if message.command[0] == "fullpromote" else False,
            can_promote_members=bot.privileges.can_promote_members if message.command[0] == "fullpromote" else False,
            can_manage_chat=bot.privileges.can_manage_chat,
            can_manage_video_chats=bot.privileges.can_manage_video_chats,
        )
        
        await message.chat.promote_member(user_id=user_id, privileges=privileges)
        await message.reply_text(f"{'🏆' if message.command[0] == 'fullpromote' else '🏅'} **{'Promoted with full rights!' if message.command[0] == 'fullpromote' else 'Promoted!'}** {mention}")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command("demote") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_promote_members")
async def demote_func(client: Client, message: Message):
    """Demote an admin to a regular member."""
    try:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if user_id == client.me.id:
            return await message.reply_text("❌ **I can't demote myself.**")
        if user_id in SUDOERS:
            return await message.reply_text("👑 **Trying to demote a sudo user? Think again!**")
        
        member = await client.get_chat_member(message.chat.id, user_id)
        if member.status != ChatMemberStatus.ADMINISTRATOR:
            return await message.reply_text("⚠️ **The mentioned user is not an admin.**")
        
        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_invite_users=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_chat=False,
                can_manage_video_chats=False,
            )
        )
        mention = (await client.get_users(user_id)).mention
        await message.reply_text(f"⬇️ **Demoted!** {mention}")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error While Demoting:** {str(e)}")

@app.on_message(filters.command("purge") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_delete_messages")
async def purge_func(client: Client, message: Message):
    """Delete messages from the replied message to the current message."""
    try:
        if not message.reply_to_message:
            return await message.reply_text("⚠️ **Reply to a message to start purging.**")
        
        cmd = message.command
        purge_to = message.id
        if len(cmd) > 1 and cmd[1].isdigit():
            purge_to = min(message.reply_to_message.id + int(cmd[1]), message.id)
        
        message_ids = []
        for msg_id in range(message.reply_to_message.id, purge_to):
            message_ids.append(msg_id)
            if len(message_ids) == 100:
                await client.delete_messages(chat_id=message.chat.id, message_ids=message_ids, revoke=True)
                message_ids = []
        
        if message_ids:
            await client.delete_messages(chat_id=message.chat.id, message_ids=message_ids, revoke=True)
        await message.delete()
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command("del") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_delete_messages")
async def delete_func(client: Client, message: Message):
    """Delete the replied message."""
    try:
        if not message.reply_to_message:
            return await message.reply_text("⚠️ **Reply to a message to delete it.**")
        await message.reply_to_message.delete()
        await message.delete()
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command(["pin", "unpin"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_pin_messages")
async def pin_func(client: Client, message: Message):
    """Pin or unpin a replied message."""
    try:
        if not message.reply_to_message:
            return await message.reply_text("⚠️ **Reply to a message to pin/unpin.**")
        
        r = message.reply_to_message
        if message.command[0] == "unpin":
            await r.unpin()
            await message.reply_text(f"📌 **Message [unpinned]({r.link}).**", disable_web_page_preview=True)
        else:
            await r.pin(disable_notification=True)
            await message.reply_text(f"📌 **Message [pinned]({r.link}).**", disable_web_page_preview=True)
            msg = f"🔔 **Pinned message confirmation:** ~ [Check, {r.link}]"
            filter_ = dict(type="text", data=msg)
            await save_filter(message.chat.id, "~pinned", filter_)
    except Exception as e:
        await message.reply_text(f"⚠️ **Error Raised While Pinning the message:** {str(e)}")

@app.on_message(filters.command("unpinall") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_pin_messages")
async def unpin_all_func(client: Client, message: Message):
    """Prompt to unpin all messages in the chat."""
    try:
        await message.reply_text(
            "⚠️ **Are you sure you want to unpin all messages?**",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text="✔️ Yes", callback_data="unpin_yes"),
                    InlineKeyboardButton(text="❌ No", callback_data="unpin_no"),
                ]
            ])
        )
    except Exception as e:
        await message.reply_text(f"⚠️ **Error Raised While  Unpinning All Messages:** {str(e)}")

@app.on_callback_query(filters.regex(r"unpin_(yes|no)"))
async def unpin_callback(client: Client, query: CallbackQuery):
    """Handle unpin all confirmation callbacks."""
    try:
        if query.data == "unpin_yes":
            await client.unpin_all_chat_messages(query.message.chat.id)
            await query.message.edit_text("📌 **All pinned messages have been unpinned.**")
        else:
            await query.message.edit_text("❌ **Unpinning of all messages canceled.**")
    except Exception as e:
        await query.message.edit_text(f"⚠️ **Error In Unpin Function or Insufficient Rights:** {str(e)}")

@app.on_message(filters.command(["mute", "tmute"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def mute_func(client: Client, message: Message):
    """Mute a user, optionally for a specific time."""
    try:
        user_id, reason = await extract_user_and_reason(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if user_id == client.me.id:
            return await message.reply_text("❌ **I can't mute myself.**")
        if user_id in SUDOERS:
            return await message.reply_text("👑 **Trying to mute a sudo user? Think again!**")
        admins = [member.user.id async for member in client.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )]
        if user_id in admins:
            return await message.reply_text("⚠️ **I can't mute an admin. You know the rules, and so how do I.**")

        mention = (await client.get_users(user_id)).mention
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Unmute", callback_data=f"unmute_{user_id}")]
        ])
        msg = f"""
🔇 **User muted:** {mention}
👤 **Muted by:** {message.from_user.mention if message.from_user else 'Anonymous'}\n"""
        
        if message.command[0] == "tmute":
            split = reason.split(None, 1)
            time_value = split[0]
            temp_reason = split[1] if len(split) > 1 else ""
            try:
                temp_mute = await time_converter(message, time_value)
                if len(time_value[:-1]) < 3:
                    msg += f"⏳ **Muted for:** {time_value}\n"
                    if temp_reason:
                        msg += f"📄 **Reason:** {temp_reason}"
                    await message.chat.restrict_member(user_id, permissions=ChatPermissions(), until_date=temp_mute)
                    await message.reply_text(msg, reply_markup=keyboard)
                else:
                    await message.reply_text("⚠️ **Cannot use more than 99.**")
                return
            except AttributeError:
                await message.reply_text("⚠️ **Invalid time format.**")
                return
        
        if reason:
            msg += f"📄 **Reason:** {reason}"
        await message.chat.restrict_member(user_id, permissions=ChatPermissions())
        await message.reply_text(msg, reply_markup=keyboard)
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command("unmute") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def unmute_func(client: Client, message: Message):
    """Unmute a user in the chat."""
    try:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        
        await message.chat.unban_member(user_id)
        mention = (await client.get_users(user_id)).mention
        await message.reply_text(f"✅ **Unmuted!** {mention}")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error in Unmute Function:** {str(e)}")

@app.on_message(filters.command(["warn", "swarn"]) & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def warn_user(client: Client, message: Message):
    """Warn a user, banning them after 3 warnings."""
    try:
        user_id, reason = await extract_user_and_reason(message)
        chat_id = message.chat.id
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        if user_id == client.me.id:
            return await message.reply_text("❌ **I can't warn myself, but I can leave if you want.**")
        if user_id in SUDOERS:
            return await message.reply_text("👑 **I can't warn a sudo user, they manage me!**")
        admins = [member.user.id async for member in client.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )]
        if user_id in admins:
            return await message.reply_text("⚠️ **I can't warn an admin, rules are rules.**")

        user = await client.get_users(user_id)
        mention = user.mention
        alpha_id = await int_to_alpha(user_id)
        warns = await get_warn(chat_id, alpha_id)
        warn_count = warns["warns"] if warns else 0
        
        if message.command[0] == "swarn":
            if message.reply_to_message:
                await message.reply_to_message.delete()
            await client.delete_user_history(message.chat.id, user_id)
        
        if warn_count >= 2:
            await message.chat.ban_member(user_id)
            await message.reply_text(f"🔴 **Warning limit exceeded for {mention}! User banned!**")
            await remove_warns(chat_id, alpha_id)
        else:
            warn = {"warns": warn_count + 1}
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚨 Remove Warnings", callback_data=f"unwarn_{user_id}")]
            ])
            msg = f"""
**⚠️ User warned:** {mention}
**🔹 Warned by:** {message.from_user.mention if message.from_user else 'Anonymous'}
**📄 Reason:** {reason or 'No reason provided'}
**⚠️ Warnings:** {warn_count + 1}/3"""
            await message.reply_text(msg, reply_markup=keyboard)
            await add_warn(chat_id, alpha_id, warn)
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_callback_query(filters.regex("unwarn_") & ~BANNED_USERS)
async def remove_warning(client: Client, query: CallbackQuery):
    """Remove a warning for a user via callback."""
    try:
        from_user = query.from_user
        chat_id = query.message.chat.id
        permissions = await member_permissions(chat_id, from_user.id)
        if "can_restrict_members" not in permissions:
            return await query.answer(
                "❌ **You don't have sufficient permissions to perform this action.**\n"
                "**Required permission:** can_restrict_members",
                show_alert=True
            )
        
        user_id = int(query.data.split("_")[1])
        alpha_id = await int_to_alpha(user_id)
        warns = await get_warn(chat_id, alpha_id)
        warn_count = warns["warns"] if warns else 0
        if warn_count == 0:
            return await query.answer("⚠️ **The user has no warnings.**")
        
        warn = {"warns": warn_count - 1}
        await add_warn(chat_id, alpha_id, warn)
        text = f"~~{query.message.text.markdown}~~\n\n__Warning removed by {from_user.mention}__"
        await query.message.edit_text(text)
    except Exception as e:
        await query.answer(f"⚠️ **Error:** {str(e)}", show_alert=True)

@app.on_message(filters.command("rmwarn") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_restrict_members")
async def remove_warnings(client: Client, message: Message):
    """Remove all warnings for a user."""
    try:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user.**")
        
        mention = (await client.get_users(user_id)).mention
        chat_id = message.chat.id
        alpha_id = await int_to_alpha(user_id)
        warns = await get_warn(chat_id, alpha_id)
        warn_count = warns["warns"] if warns else 0
        
        if warn_count == 0:
            await message.reply_text(f"✅ **{mention} has no warnings.**")
        else:
            await remove_warns(chat_id, alpha_id)
            await message.reply_text(f"🗑️ **Warnings for {mention} have been removed.**")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error While Removing warnings:** {str(e)}")

@app.on_message(filters.command("warns") & ~filters.private & ~BANNED_USERS)
@capture_err
async def check_warns(client: Client, message: Message):
    """Check the number of warnings for a user."""
    try:
        user_id = await extract_user(message)
        if not user_id:
            return await message.reply_text("❌ **Couldn't find that user , Make Sure User Is A participant Of This Group or Not.**")
        
        mention = (await client.get_users(user_id)).mention
        alpha_id = await int_to_alpha(user_id)
        warns = await get_warn(message.chat.id, alpha_id)
        warn_count = warns["warns"] if warns else 0
        
        if warn_count == 0:
            return await message.reply_text(f"✅ **{mention} has no warnings.**")
        return await message.reply_text(f"⚠️ **{mention} has {warn_count}/3 warnings.**")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error While Checking Warnings:** {str(e)}")

@app.on_message(filters.command("link") & ~filters.private & ~BANNED_USERS)
@adminsOnly("can_invite_users")
async def invite_func(client: Client, message: Message):
    """Share the group's invite link."""
    try:
        if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return await message.reply_text("⚠️ **This command is only for groups and supergroups.**")
        
        chat = await client.get_chat(message.chat.id)
        link = chat.invite_link or await client.export_chat_invite_link(message.chat.id)
        text = f"🔗 **Here is the group's invite link:**\n\n{link}"
        await message.reply_text(text, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(f"⚠️ **Error While Getting Invite Link of This Chat:** {str(e)}")
