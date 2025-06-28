import logging

from SafoneAPI import SafoneAPI
from WinxMusic import app
from googlesearch import search
from pyrogram import filters
from pyrogram.types import Message


@app.on_message(filters.command(["google", "gg"]))
async def google(_, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Example:\n\n`/google search query`")
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    b = await message.reply_text("Searching...🔎")
    try:
        results = search(user_input, advanced=True)
        txt = f"🔍 Search Query: {user_input}\n\nResults:"
        for result in results:
            txt += f"\n\n[❍ {result.title}]({result.url})\n<b>{result.description}</b>"
        await b.edit(
            txt,
            disable_web_page_preview=True,
        )
    except Exception as e:
        await b.edit(f"Failed: {str(e)} ❌")
        logging.exception(e)


@app.on_message(filters.command(["app", "apps"]))
async def app(_, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Example:\n\n`/app App Name`")
        return

    if message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        user_input = " ".join(message.command[1:])

    cbb = await message.reply_text("Searching Play Store...📱")
    a = await SafoneAPI().apps(user_input, 1)
    b = a["results"][0]
    icon = b["icon"]
    app_id = b["id"]
    link = b["link"]
    description = b["description"]
    title = b["title"]
    developer = b["developer"]

    info = (
        f"<b>[Title: {title}]({link})</b>\n"
        f"<b>ID</b>: <code>{app_id}</code>\n"
        f"<b>Developer</b>: {developer}\n"
        f"<b>Description</b>: {description}"
    )

    try:
        await message.reply_photo(icon, caption=info)
        await cbb.delete()
    except Exception as e:
        await message.reply_text(f"Error: {str(e)} ❌")


__MODULE__ = "🌐Google"
__HELP__ = """
/google | /gg [query] - Search on Google and return the top results.
/app | /apps [app name] - Get Play Store app information such as title, description, and developer.
"""
