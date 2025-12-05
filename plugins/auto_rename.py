from pyrogram import Client, filters
from plugins.admin_panel import load_settings
import os

DB_CHANNEL = int(os.environ.get("DB_CHANNEL"))
DUMP_CHANNEL = int(os.environ.get("DUMP_CHANNEL"))

@Client.on_message(filters.chat(DB_CHANNEL) & filters.media)
async def auto_rename(client, message):

    settings = load_settings()
    prefix = settings["prefix"]
    thumb = settings["thumbnail"]

    media = message.document or message.video or message.audio
    if not media:
        return

    old_name = media.file_name
    new_name = prefix + old_name

    # download renamed
    downloaded = await message.download(file_name=new_name)

    # send renamed file
    await client.send_document(
        chat_id=DUMP_CHANNEL,
        document=downloaded,
        caption=f"✨ Renamed: `{new_name}`",
        thumb=thumb if thumb else None
    )

    # remove temp
    os.remove(downloaded)
