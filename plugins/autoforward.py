from pyrogram import Client, filters
from info import OWNER_ID

# Add your source channels here
SOURCE_CHANNELS = [-1001234567890]   # edit this
DEST_CHANNEL = -1009876543210        # edit this

# Custom caption format
CUSTOM_CAPTION = "🔥 New Update Uploaded!\n\n{old_caption}"

@Client.on_message(filters.chat(SOURCE_CHANNELS) & (filters.video | filters.document | filters.photo | filters.audio))
async def auto_forward_handler(bot, message):

    old_caption = message.caption or ""
    final_caption = CUSTOM_CAPTION.format(old_caption=old_caption)

    try:
        # copy the message + new caption
        await message.copy(
            chat_id=DEST_CHANNEL,
            caption=final_caption
        )

    except Exception as e:
        # send error to owner
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"❌ Auto-Forward Error:\n{e}"
        )
