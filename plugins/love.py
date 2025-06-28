import random

from WinxMusic import app
from pyrogram import filters


def get_random_message(love_percentage):
    if love_percentage <= 30:
        return random.choice(
            [
                "💔 Love is in the air, but it needs a little spark.",
                "🌱 A good start, but there's room to grow.",
                "✨ It's just the beginning of something beautiful.",
            ]
        )
    elif love_percentage <= 70:
        return random.choice(
            [
                "💞 There's a strong connection. Keep nurturing it.",
                "🌼 You two have good potential. Work on it together.",
                "🌸 Love is blooming—keep going!",
            ]
        )
    else:
        return random.choice(
            [
                "💖 Wow! A perfect couple!",
                "💘 A match made in heaven. Cherish this bond.",
                "💞 Destined to be together. Congratulations!",
            ]
        )


@app.on_message(filters.command("love", prefixes="/"))
def love_command(client, message):
    command, *args = message.text.split(" ")
    if len(args) >= 2:
        name1 = args[0].strip()
        name2 = args[1].strip()

        love_percentage = random.randint(10, 100)
        love_message = get_random_message(love_percentage)

        response = f"{name1}💕 + {name2}💕 = {love_percentage}%\n\n{love_message}"
    else:
        response = "⚠️ Please enter two names after the command `/love`."
    app.send_message(message.chat.id, response)


__MODULE__ = "💕 Love"
__HELP__ = """
**🧡 Love Calculator:**

• `/love [name1] [name2]`: 💕 Calculates the love percentage between two people and gives a cute message.
"""
