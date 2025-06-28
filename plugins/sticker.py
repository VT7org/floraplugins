import imghdr
import math
import os
from asyncio import gather
from traceback import format_exc
from typing import List

from PIL import Image
from WinxMusic import app
from pyrogram import Client, errors, filters, raw
from pyrogram.errors import (
    PeerIdInvalid,
    ShortnameOccupyFailed,
    StickerEmojiInvalid,
    StickerPngDimensions,
    StickerPngNopng,
    UserIsBlocked,
)
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from utils.error import capture_err

BOT_USERNAME = app.username

MAX_STICKERS = 120
SUPPORTED_TYPES = ["jpeg", "png", "webp"]
STICKER_DIMENSIONS = (512, 512)

async def get_sticker_set_by_name(client: Client, name: str) -> raw.base.messages.StickerSet:
    try:
        return await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetShortName(short_name=name),
                hash=0,
            )
        )
    except errors.exceptions.not_acceptable_406.StickersetInvalid:
        return None

async def create_sticker_set(client: Client, owner: int, title: str, short_name: str, stickers: List[raw.base.InputStickerSetItem]) -> raw.base.messages.StickerSet:
    return await client.invoke(
        raw.functions.stickers.CreateStickerSet(
            user_id=await client.resolve_peer(owner),
            title=title,
            short_name=short_name,
            stickers=stickers,
        )
    )

async def add_sticker_to_set(client: Client, stickerset: raw.base.messages.StickerSet, sticker: raw.base.InputStickerSetItem) -> raw.base.messages.StickerSet:
    return await client.invoke(
        raw.functions.stickers.AddStickerToSet(
            stickerset=raw.types.InputStickerSetShortName(short_name=stickerset.set.short_name),
            sticker=sticker,
        )
    )

async def create_sticker(sticker: raw.base.InputDocument, emoji: str) -> raw.base.InputStickerSetItem:
    return raw.types.InputStickerSetItem(document=sticker, emoji=emoji)

async def resize_file_to_sticker_size(file_path: str) -> str:
    im = Image.open(file_path)
    if (im.width, im.height) < STICKER_DIMENSIONS:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = STICKER_DIMENSIONS[0] / size1
            size1new = STICKER_DIMENSIONS[0]
            size2new = size2 * scale
        else:
            scale = STICKER_DIMENSIONS[1] / size2
            size1new = size1 * scale
            size2new = STICKER_DIMENSIONS[1]
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(STICKER_DIMENSIONS)
    try:
        os.remove(file_path)
        file_path = f"{file_path}.png"
        return file_path
    finally:
        im.save(file_path)

async def upload_document(client: Client, file_path: str, chat_id: int) -> raw.base.InputDocument:
    media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=await client.resolve_peer(chat_id),
            media=raw.types.InputMediaUploadedDocument(
                mime_type=client.guess_mime_type(file_path) or "application/zip",
                file=await client.save_file(file_path),
                attributes=[
                    raw.types.DocumentAttributeFilename(file_name=os.path.basename(file_path))
                ],
            ),
        )
    )
    return raw.types.InputDocument(
        id=media.document.id,
        access_hash=media.document.access_hash,
        file_reference=media.document.file_reference,
    )

async def get_document_from_file_id(file_id: str) -> raw.base.InputDocument:
    decoded = FileId.decode(file_id)
    return raw.types.InputDocument(
        id=decoded.media_id,
        access_hash=decoded.access_hash,
        file_reference=decoded.file_reference,
    )

@app.on_message(filters.command("stickerid"))
@capture_err
async def sticker_id(_, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply("Reply to a sticker. ✋")
    if not reply.sticker:
        return await message.reply("Reply to a sticker. 🖼️")
    await message.reply_text(f"`{reply.sticker.file_id}`")

@app.on_message(filters.command("getsticker"))
@capture_err
async def sticker_image(_, message: Message):
    r = message.reply_to_message
    if not r:
        return await message.reply("Reply to a sticker. ✋")
    if not r.sticker:
        return await message.reply("Reply to a sticker. 🖼️")
    m = await message.reply("Sending... ⏳")
    f = await r.download(f"{r.sticker.file_unique_id}.png")
    await gather(
        *[
            message.reply_photo(f),
            message.reply_document(f),
        ]
    )
    await m.delete()
    os.remove(f)

@app.on_message(filters.command("kang"))
@capture_err
async def kang(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a sticker/image to kang. 🖼️✨")
    if not message.from_user:
        return await message.reply_text("You are an anonymous admin, kang stickers in my PMs. 🛡️")
    msg = await message.reply_text("Kanging sticker... 🛠️")

    args = message.text.split()
    if len(args) > 1:
        sticker_emoji = str(args[1])
    elif message.reply_to_message.sticker and message.reply_to_message.sticker.emoji:
        sticker_emoji = message.reply_to_message.sticker.emoji
    else:
        sticker_emoji = "🤔"

    doc = message.reply_to_message.photo or message.reply_to_message.document
    try:
        if message.reply_to_message.sticker:
            sticker = await create_sticker(
                await get_document_from_file_id(message.reply_to_message.sticker.file_id),
                sticker_emoji,
            )
        elif doc:
            if doc.file_size > 10000000:
                return await msg.edit("File too large. 🚫")
            temp_file_path = await app.download_media(doc)
            image_type = imghdr.what(temp_file_path)
            if image_type not in SUPPORTED_TYPES:
                return await msg.edit(f"Unsupported format! ({image_type}) ❌")
            try:
                temp_file_path = await resize_file_to_sticker_size(temp_file_path)
            except OSError as e:
                await msg.edit_text("Something went wrong. ⚠️")
                raise Exception(f"Error resizing sticker ({temp_file_path}); {e}")
            sticker = await create_sticker(
                await upload_document(client, temp_file_path, message.chat.id),
                sticker_emoji,
            )
            if os.path.isfile(temp_file_path):
                os.remove(temp_file_path)
        else:
            return await msg.edit("Can't kang this. ❌")
    except ShortnameOccupyFailed:
        await message.reply_text("Change your name or username. 🛑")
        return
    except Exception as e:
        await message.reply_text(str(e))
        e = format_exc()
        return print(e)

    packnum = 0
    packname = "f" + str(message.from_user.id) + "_by_" + BOT_USERNAME
    limit = 0
    try:
        while True:
            if limit >= 50:
                return await msg.delete()
            stickerset = await get_sticker_set_by_name(client, packname)
            if not stickerset:
                stickerset = await create_sticker_set(
                    client,
                    message.from_user.id,
                    f"{message.from_user.first_name[:32]}'s kang pack",
                    packname,
                    [sticker],
                )
            elif stickerset.set.count >= MAX_STICKERS:
                packnum += 1
                packname = f"f{packnum}_{message.from_user.id}_by_{BOT_USERNAME}"
                limit += 1
                continue
            else:
                try:
                    await add_sticker_to_set(client, stickerset, sticker)
                except StickerEmojiInvalid:
                    return await msg.edit("[ERROR]: INVALID_EMOJI_IN_ARGUMENT ❌")
            limit += 1
            break

        await msg.edit(
            f"Sticker kanged to [Pack](t.me/addstickers/{packname})\nEmoji: {sticker_emoji} 🎨"
        )
    except (PeerIdInvalid, UserIsBlocked):
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Start", url=f"t.me/{BOT_USERNAME}")]]
        )
        await msg.edit(
            "You need to start a private chat with me. 📩",
            reply_markup=keyboard,
        )
    except StickerPngNopng:
        await message.reply_text("Stickers must be in PNG, but the given image was not. 🖼️🚫")
    except StickerPngDimensions:
        await message.reply_text("The PNG sticker dimensions are invalid. 📏❌")


__MODULE__ = "🖼Stickers"
__HELP__ = """
**COMMANDS:**

• /stickerid - **Get the file ID of a replied sticker.**
• /getsticker - **Get the image of a replied sticker.**
• /kang - **Kang a sticker to your pack.**

**INFO:**

- This bot allows users to obtain the file ID or image of a replied sticker, and also kang it to their sticker pack.
"""
    
