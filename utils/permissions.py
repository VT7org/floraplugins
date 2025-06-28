import logging
from functools import wraps
from traceback import format_exc as err

from WinxMusic import app
from WinxMusic.misc import SUDOERS
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import Message


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = (await app.get_chat_member(chat_id, user_id)).privileges
    if not member:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_video_chats:
        perms.append("can_manage_video_chats")
    return perms


async def authorised(func, sub_func2, client, message, *args, **kwargs):
    chat_id = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await app.leave_chat(chat_id)
    except Exception as e:
        logging.exception(e)
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(str(e))
    return sub_func2


async def unauthorised(
        message: Message, permission, sub_func2, bot_lacking_permission=False
):
    chat_id = message.chat.id
    if bot_lacking_permission:
        text = (
            "Sorry! 😕\n"
            "I don't have permission 🚫 to perform this action. Provide Proper Rights To Me & Try Again\n"
            f"**Required Permission:** __{permission}__"
        )
    else:
        text = (
            "You don't have Necessary permissions to perform this action. Be an Admin First ❌\n"
            f"**Required Permission:** __{permission}__"
        )
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        await app.leave_chat(chat_id)
    return sub_func2


async def bot_permissions(chat_id: int):
    perms = []
    return await member_permissions(chat_id, app.id)


def admins_only(permission: str):
    def sub_func(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id

            # Check if the bot has the required permission
            bot_perms = await bot_permissions(chatID)
            if permission not in bot_perms:
                return await unauthorised(
                    message, permission, subFunc2, bot_lacking_permission=True
                )

            if not message.from_user:
                # For anonymous admins
                if message.sender_chat and message.sender_chat.id == message.chat.id:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(message, permission, subFunc2)

            # For admins and sudo users
            user_id = message.from_user.id
            permissions = await member_permissions(chatID, user_id)
            if user_id not in SUDOERS and permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(func, subFunc2, client, message, *args, **kwargs)

        return subFunc2

    return sub_func
