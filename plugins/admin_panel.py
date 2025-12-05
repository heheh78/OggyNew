from pyrogram import Client, filters
import os, json

ADMIN = int(os.environ.get("ADMIN"))
SETTINGS_FILE = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        data = {
            "prefix": "Movies_",
            "thumbnail": None,
            "auto_rename": True
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Set Prefix
@Client.on_message(filters.command("setprefix") & filters.user(ADMIN))
async def set_prefix(client, message):
    try:
        prefix = message.text.split(maxsplit=1)[1]
    except:
        return await message.reply("❗ Usage:\n/setprefix Chithram_")

    data = load_settings()
    data["prefix"] = prefix
    save_settings(data)

    await message.reply(f"✔ Prefix updated to:\n`{prefix}`")

# Set Thumbnail (Send photo with caption: /setthumb)
@Client.on_message(filters.photo & filters.user(ADMIN))
async def set_thumbnail(client, message):
    if message.caption != "/setthumb":
        return

    path = await message.download("thumb.jpg")

    data = load_settings()
    data["thumbnail"] = path
    save_settings(data)

    await message.reply("🖼️ Thumbnail Saved Successfully!")

# Show Settings
@Client.on_message(filters.command("showsettings") & filters.user(ADMIN))
async def show_settings(client, message):
    data = load_settings()

    text = f"""
🛠 **Current Bot Settings**

📌 Prefix: `{data['prefix']}`
🖼 Thumbnail: {"Yes" if data['thumbnail'] else "No"}
🚀 Auto Rename: {"Enabled" if data['auto_rename'] else "Disabled"}
"""
    await message.reply(text)
