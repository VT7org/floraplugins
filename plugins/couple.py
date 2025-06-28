import os
import random
from datetime import datetime, timedelta

import pytz
import requests
from PIL import Image, ImageDraw
from TheApi import api
from WinxMusic import app
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from utils import get_image, get_couple, save_couple


# Get current date in GMT+5:30 timezone
def get_today_date():
    timezone = pytz.timezone("Asia/Kolkata")
    now = datetime.now(timezone)
    return now.strftime("%d/%m/%Y")


# Get tomorrow's date in GMT+5:30 timezone
def get_tomorrow_date():
    timezone = pytz.timezone("Asia/Kolkata")
    tomorrow = datetime.now(timezone) + timedelta(days=1)
    return tomorrow.strftime("%d/%m/%Y")


# Download image from URL
def download_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "wb") as f:
            f.write(response.content)
    return path


# Dates
tomorrow = get_tomorrow_date()
today = get_today_date()


@app.on_message(filters.command(["couple", "couples"]))
async def ctest(_, message: Message):
    cid = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("⚠️ **This Function only works in groups.**")

    p1_path = "downloads/pfp.png"
    p2_path = "downloads/pfp1.png"
    test_image_path = f"downloads/test_{cid}.png"
    cppic_path = "downloads/cppic.png"

    try:
        is_selected = await get_couple(cid, today)
        if not is_selected:
            msg = await message.reply_text("💞")
            list_of_users = []

            async for i in app.get_chat_members(message.chat.id, limit=50):
                if not i.user.is_bot and not i.user.is_deleted:
                    list_of_users.append(i.user.id)

            c1_id = random.choice(list_of_users)
            c2_id = random.choice(list_of_users)
            while c1_id == c2_id:
                c1_id = random.choice(list_of_users)

            photo1 = (await app.get_chat(c1_id)).photo
            photo2 = (await app.get_chat(c2_id)).photo

            N1 = (await app.get_users(c1_id)).mention
            N2 = (await app.get_users(c2_id)).mention

            try:
                p1 = await app.download_media(photo1.big_file_id, file_name=p1_path)
            except Exception:
                p1 = download_image(
                    "https://telegra.ph/file/05aa686cf52fc666184bf.jpg", p1_path
                )
            try:
                p2 = await app.download_media(photo2.big_file_id, file_name=p2_path)
            except Exception:
                p2 = download_image(
                    "https://telegra.ph/file/05aa686cf52fc666184bf.jpg", p2_path
                )

            img1 = Image.open(p1)
            img2 = Image.open(p2)

            background_image_path = download_image(
                "https://telegra.ph/file/96f36504f149e5680741a.jpg", cppic_path
            )
            img = Image.open(background_image_path)

            img1 = img1.resize((437, 437))
            img2 = img2.resize((437, 437))

            mask = Image.new("L", img1.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img1.size, fill=255)

            mask1 = Image.new("L", img2.size, 0)
            draw = ImageDraw.Draw(mask1)
            draw.ellipse((0, 0) + img2.size, fill=255)

            img1.putalpha(mask)
            img2.putalpha(mask1)

            draw = ImageDraw.Draw(img)

            img.paste(img1, (116, 160), img1)
            img.paste(img2, (789, 160), img2)

            img.save(test_image_path)

            TXT = f"""
**Couple of the day 💘:**

{N1} + {N2} = 💚

The next couple will be selected on {tomorrow}!
            """

            await message.reply_photo(
                test_image_path,
                caption=TXT,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🌋 **Add me**",
                                url=f"https://t.me/{app.username}?startgroup=true",
                            )
                        ]
                    ]
                ),
            )

            await msg.delete()
            img_url = api.upload_image(test_image_path)
            couple = {"c1_id": c1_id, "c2_id": c2_id}
            await save_couple(cid, today, couple, img_url)

        else:
            msg = await message.reply_text("💞")
            b = await get_image(cid)
            c1_id = int(is_selected["c1_id"])
            c2_id = int(is_selected["c2_id"])
            c1_name = (await app.get_users(c1_id)).first_name
            c2_name = (await app.get_users(c2_id)).first_name

            TXT = f"""
**Couples💟 of the day 🎉:**

[{c1_name}](tg://openmessage?user_id={c1_id}) + [{c2_name}](tg://openmessage?user_id={c2_id}) = 💞

The next couple will be selected on {tomorrow}!
            """
            await message.reply_photo(
                b,
                caption=TXT,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🌋 **Add me**",
                                url=f"https://t.me/{app.username}?startgroup=true",
                            )
                        ]
                    ]
                ),
            )
            await msg.delete()

    except Exception:
        pass
    finally:
        try:
            os.remove(p1_path)
            os.remove(p2_path)
            os.remove(test_image_path)
            os.remove(cppic_path)
        except Exception:
            pass
