import requests
from WinxMusic import app
from pyrogram import filters

truth_api_url = "https://api.truthordarebot.xyz/v1/truth"
dare_api_url = "https://api.truthordarebot.xyz/v1/dare"


@app.on_message(filters.command("truth"))
def get_truth(client, message):
    try:
        response = requests.get(truth_api_url)
        if response.status_code == 200:
            truth_question = response.json()["question"]
            message.reply_text(f"💬 Truth Question:\n\n{truth_question}")
        else:
            message.reply_text(
                "⚠️ Failed to fetch a truth question. Please try again later."
            )
    except Exception:
        message.reply_text(
            "❌ An error occurred while getting a truth question. Please try again later."
        )


@app.on_message(filters.command("dare"))
def get_dare(client, message):
    try:
        response = requests.get(dare_api_url)
        if response.status_code == 200:
            dare_question = response.json()["question"]
            message.reply_text(f"🔥 Dare:\n\n{dare_question}")
        else:
            message.reply_text(
                "⚠️ Failed to fetch a dare. Please try again later."
            )
    except Exception:
        message.reply_text(
            "❌ An error occurred while getting a dare. Please try again later."
        )


__MODULE__ = "🔥Truth-Dare"
__HELP__ = """
**📜 BOT COMMANDS: TRUTH OR DARE**

Use the commands below to play a game of Truth or Dare:

- `/truth`: 🔎 Get a truth question. Answer it honestly!
- `/dare`: 🔥 Get a daring challenge. Do it if you're brave enough!

**📌 Examples:**
- `/truth`: "What's your most embarrassing moment?"
- `/dare`: "Do 10 push-ups."

**⚠️ NOTE:**
If there are issues retrieving questions, please try again later.
"""
