from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("help"))
async def generate_link(client, message):
    command_text = message.text.split(maxsplit=1)
    if len(command_text) < 2:
        user_mention = message.from_user.mention
        text = f"""❝ 𝖧𝖾𝗒 {user_mention} താഴെ ഉള്ള കാര്യങ്ങൾ ശ്രദ്ധിക്കുക ❞

🔹കറക്റ്റ് സ്പെല്ലിംഗിൽ ചോദിക്കുക. (ഇംഗ്ലീഷിൽ മാത്രം)
🔸സിനിമകൾ ഇംഗ്ലീഷിൽ Type ചെയ്ത് മാത്രം ചോദിക്കുക.
🔹OTT റിലീസ് ആകാത്ത സിനിമകൾ ചോദിക്കരുത്.
🔸സിനിമയുടെ പേര് [വർഷം ഭാഷ] ഈ രീതിയിൽ ചോദിക്കുക.
🔹സിനിമ Request ചെയ്യുമ്പോൾ Symbols ഒഴിവാക്കുക. [+:;'*!-&.. etc

‼ 𝖱𝖾𝗉𝗈𝗋𝗍 𝗍𝗈 𝖺𝖽𝗆𝗂𝗇 ▶ @iam_fraz_bot"""

        await message.reply(text)
        return
