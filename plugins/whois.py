from WinxMusic import app
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.types import Message, User
from datetime import datetime


def reply_check(message: Message):
    reply_id = None
    if message.reply_to_message:
        reply_id = message.reply_to_message.message_id
    elif not message.from_user.is_self:
        reply_id = message.message_id
    return reply_id


infotext = (
    "[{full_name}](tg://user?id={user_id})\n\n"
    " ➻ User ID: `{user_id}`\n"
    " ➻ First Name: `{first_name}`\n"
    " ➻ Last Name: `{last_name}`\n"
    " ➻ Username: `@{username}`\n"
    " ➻ Last Seen: `{last_online}`"
)


def last_online(user: User):
    if user.is_bot:
        return ""
    elif user.status == "recently":
        return "recently"
    elif user.status == "within_week":
        return "within the last week"
    elif user.status == "within_month":
        return "within the last month"
    elif user.status == "long_time_ago":
        return "a long time ago :("
    elif user.status == "online":
        return "currently online"
    elif user.status == "offline":
        return datetime.fromtimestamp(user.status.date).strftime("%a, %d %b %Y, %H:%M:%S")


def full_name(user: User):
    return user.first_name + " " + user.last_name if user.last_name else user.first_name


@app.on_message(filters.command("whois"))
async def whois(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_users(get_user)
    except PeerIdInvalid:
        await message.reply("I don't know this user.")
        return

    desc = await client.get_chat(get_user)
    desc = desc.description
    await message.reply_text(
        infotext.format(
            full_name=full_name(user),
            user_id=user.id,
            user_dc=user.dc_id,
            first_name=user.first_name,
            last_name=user.last_name if user.last_name else "",
            username=user.username if user.username else "",
            last_online=last_online(user),
            bio=desc if desc else "Empty."
        ),
        disable_web_page_preview=True,
    )


__MODULE__ = "🆔 Info"
__HELP__ = """
**Command:**

• /whois - **Check information of a user.**

**Information:**

- This bot provides a command to retrieve user information.
- Use the /whois command by replying to a message or providing a User ID to fetch the user's info.

**Note:**

- The /whois command can be used to retrieve user details in the chat.
- The information includes ID, First Name, Last Name, Username, and Online Status.
"""
