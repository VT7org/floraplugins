import io
import os
import os.path
import time
from inspect import getfullargspec
from os.path import exists, isdir

from WinxMusic import app
from WinxMusic.misc import SUDOERS
from pyrogram import filters
from pyrogram.types import Message

from utils.error import capture_err

MAX_MESSAGE_SIZE_LIMIT = 4095


def humanbytes(size):
    """Convert bytes to a human-readable format."""
    if not size:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.2f} {unit}"


@app.on_message(filters.command("ls") & ~filters.forwarded & ~filters.via_bot & SUDOERS)
@capture_err
async def lst(_, message: Message):
    prefix = message.text.split()[0][0]
    chat_id = message.chat.id
    path = os.getcwd()
    text = message.text.split(" ", 1)
    directory = None
    if len(text) > 1:
        directory = text[1].strip()
        path = directory
    if not exists(path):
        await eor(
            message,
            text=f"❌ **No directory or file named** `{directory}`. **Please check again!**",
        )
        return
    if isdir(path):
        if directory:
            msg = f"📁 **Files and Folders in** `{path}`:\n\n"
            lists = os.listdir(path)
        else:
            msg = "📂 **Files and Folders in Current Directory:**\n\n"
            lists = os.listdir(path)
        files = ""
        folders = ""
        for contents in sorted(lists):
            thepathoflight = path + "/" + contents
            if not isdir(thepathoflight):
                size = os.stat(thepathoflight).st_size
                if contents.endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += "🎵 " + f"`{contents}`\n"
                elif contents.endswith((".opus")):
                    files += "🎙 " + f"`{contents}`\n"
                elif contents.endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
                    files += "🎞 " + f"`{contents}`\n"
                elif contents.endswith((".zip", ".tar", ".tar.gz", ".rar", ".7z", ".xz")):
                    files += "🗜 " + f"`{contents}`\n"
                elif contents.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")):
                    files += "🖼 " + f"`{contents}`\n"
                elif contents.endswith((".exe", ".deb")):
                    files += "⚙️ " + f"`{contents}`\n"
                elif contents.endswith((".iso", ".img")):
                    files += "💿 " + f"`{contents}`\n"
                elif contents.endswith((".apk", ".xapk")):
                    files += "📱 " + f"`{contents}`\n"
                elif contents.endswith((".py")):
                    files += "🐍 " + f"`{contents}`\n"
                else:
                    files += "📄 " + f"`{contents}`\n"
            else:
                folders += f"📁 `{contents}`\n"
        if files or folders:
            msg = msg + folders + files
        else:
            msg += "__Empty path__"
    else:
        size = os.stat(path).st_size
        msg = "📄 **Details of the specified file:**\n\n"
        if path.endswith((".mp3", ".flac", ".wav", ".m4a")):
            mode = "🎵 "
        elif path.endswith((".opus")):
            mode = "🎙 "
        elif path.endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
            mode = "🎞 "
        elif path.endswith((".zip", ".tar", ".tar.gz", ".rar", ".7z", ".xz")):
            mode = "🗜 "
        elif path.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".webp")):
            mode = "🖼 "
        elif path.endswith((".exe", ".deb")):
            mode = "⚙️ "
        elif path.endswith((".iso", ".img")):
            mode = "💿 "
        elif path.endswith((".apk", ".xapk")):
            mode = "📱 "
        elif path.endswith((".py")):
            mode = "🐍 "
        else:
            mode = "📄 "
        time.ctime(os.path.getctime(path))
        time2 = time.ctime(os.path.getmtime(path))
        time3 = time.ctime(os.path.getatime(path))
        msg += f"**📍 Location:** `{path}`\n"
        msg += f"**🔖 Icon:** `{mode}`\n"
        msg += f"**📏 Size:** `{humanbytes(size)}`\n"
        msg += f"**🕒 Last Modified:** `{time2}`\n"
        msg += f"**📅 Last Accessed:** `{time3}`"

    if len(msg) > MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "ls.txt"
            await app.send_document(
                chat_id,
                out_file,
                caption=path,
            )
            await message.delete()
    else:
        await eor(message, text=msg)


@app.on_message(filters.command("rm") & ~filters.forwarded & ~filters.via_bot & SUDOERS)
@capture_err
async def rm_file(_, message: Message):
    if len(message.command) < 2:
        return await eor(message,
                         text="🚫 **Please provide the name of a file to delete.**")
    file = message.text.split(" ", 1)[1]
    if exists(file):
        os.remove(file)
        await eor(message, text=f"🗑️ **{file} has been deleted Successfully ✅.**")
    else:
        await eor(message, text=f"❌ **{file} does not exist!**")


async def eor(msg: Message, **kwargs: dict):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})
