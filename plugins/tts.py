import io

from WinxMusic import app
from gtts import gTTS
from pyrogram import filters


@app.on_message(filters.command(["tts", "aivoice"]))
async def text_to_speech(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❗ Please provide text to convert into audio. 🎤"
        )

    text = message.text.split(None, 1)[1]
    tts = gTTS(text, lang="hi")  
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    audio_file = io.BytesIO(audio_data.read())
    audio_file.name = "Billa.mp3"
    await message.reply_audio(audio_file)


__MODULE__ = "Ai Voice"
__HELP__ = """
**📢 Text-to-Speech Commands (TTS) 🎶**

Use this feature to convert your typed text into spoken audio in Portuguese.

- `/tts <text>`: Converts the provided text into a Ai audio clip.
- `/aivoice <text>`: Same as `/tts`, just an alternate command name.

**📝 Example:**
- `/tts Hello, how are you today?`
- `/aivoice Ragnar Dalla hai !`

**⚠️ Note:**
Make sure to include text after the command for conversion to work.
"""
    
