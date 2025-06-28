import requests
from WinxMusic import app
from pyrogram import filters
from pyrogram.types import Message


@app.on_message(filters.command(["address", "fake"]))
async def fk_address(_, message: Message):
    query = message.text.split(maxsplit=1)[1].strip()
    url = f"https://randomuser.me/api/?nat={query}"
    response = requests.get(url)
    data = response.json()

    if "results" in data:
        fk = data["results"][0]

        name = f"{fk['name']['title']} {fk['name']['first']} {fk['name']['last']}"
        address = (
            f"{fk['location']['street']['number']} {fk['location']['street']['name']}"
        )
        city = fk["location"]["city"]
        state = fk["location"]["state"]
        country = fk["location"]["country"]
        postal = fk["location"]["postcode"]
        email = fk["email"]
        phone = fk["phone"]
        picture = fk["picture"]["large"]
        gender = fk["gender"]

        fkinfo = f"""
**👤 Name:** `{name}`
**⚧️ Gender:** `{gender}`
**🏠 Address:** `{address}`
**🌎 Country:** `{country}`
**🏙️ City:** `{city}`
**🌐 State:** `{state}`
**📮 Postal Code:** `{postal}`
**📧 Email:** `{email}`
**📞 Phone:** `{phone}`
        """

        await message.reply_photo(photo=picture, caption=fkinfo)
    else:
        await message.reply_text(
            "❌ **No address found.Check Your Country Code Try again!**")


__MODULE__ = "📄 Fake"
__HELP__ = """
• /fake [country code] - **Generates a random fake address eg. /fake IN for india**
• /address [country code] -  its Alternative command
"""
