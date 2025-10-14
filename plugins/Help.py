from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse

@Client.on_message(filters.command("help"))
async def generate_link(client, message):
    command_text = message.text.split(maxsplit=1)
    if len(command_text) < 2:
        user_mention = message.from_user.mention

        text = f"""❝ 𝖧𝖾𝗒 {user_mention}, സിനിമ/മൂവി റിക്വസ്റ്റ് ചെയ്യാൻ ചില കാര്യങ്ങൾ ശ്രദ്ധിക്കുക ❞

🔹 കറക്റ്റ് സ്പെല്ലിംഗിൽ മാത്രം ചോദിക്കുക (ഇംഗ്ലീഷിൽ)  
🔸 Movies should be typed in **English** only.  
🔹 സിനിമയുടെ പേര് [വർഷം ഭാഷ] ഫോർമാറ്റിൽ അയയ്ക്കുക  
🔸 Send movies in the format: **MovieName [Year Language]**  
🔹 OTT റിലീസ് ആകാത്ത സിനിമകൾ ചോദിക്കരുത്  
🔸 Do not request movies that are not released on OTT yet.  
🔹 Symbols ഒഴിവാക്കുക: [+:;'*!-&.. etc]  
🔸 Avoid symbols when sending movie names.  

‼ Report to admin ▶ @iam_fraz_bot"""

        # Prepare Google search URL for correct spelling
        query = "movie correct spelling site:google.com"
        google_search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"

        # Add inline button
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Correct Spelling on Google", url=google_search_url)]
        ])

        await message.reply(text, reply_markup=buttons)
        return
