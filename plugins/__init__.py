import json
import subprocess
import sys, os

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest, Message
from pyrogram.errors import ChatAdminRequired, FloodWait, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from info import ADMINS
from database.users_chats_db import db
from utils import temp


# ────────────────────────────────
# 🔹 Handle join requests
# ────────────────────────────────
@Client.on_chat_join_request()
async def join_reqs(_, join_req: ChatJoinRequest):
    user_id = join_req.from_user.id
    try:
        if join_req.chat.id == temp.REQ_CHANNEL1:
            await db.add_req_one(user_id)
        elif join_req.chat.id == temp.REQ_CHANNEL2:
            await db.add_req_two(user_id)
    except Exception as e:
        print(f"Error adding join request: {e}")


# ────────────────────────────────
# 🔹 Force Subscribe Help
# ────────────────────────────────
@Client.on_message(filters.command("fusub") & filters.user(ADMINS))
async def fusub_help(bot, message):
    text = (
        "<b>🧩 Force Subscribe Commands</b>\n\n"
        "‣ <b>/setchat1</b> - Set Force Subscribe Channel 1\n"
        "‣ <b>/setchat2</b> - Set Force Subscribe Channel 2\n"
        "‣ <b>/delchat1</b> - Delete Force Subscribe Channel 1\n"
        "‣ <b>/delchat2</b> - Delete Force Subscribe Channel 2\n"
        "‣ <b>/viewchat1</b> - View Invite Link & Info for Channel 1\n"
        "‣ <b>/viewchat2</b> - View Invite Link & Info for Channel 2\n"
        "‣ <b>/purge_one</b> - Clear all Channel 1 requests from DB\n"
        "‣ <b>/purge_two</b> - Clear all Channel 2 requests from DB\n"
        "‣ <b>/totalreq</b> - View Total Force Subscribe User Counts\n"
    )
    await message.reply(text, disable_web_page_preview=True)


# ────────────────────────────────
# 🔹 Set Force Subscribe Channels
# ────────────────────────────────
@Client.on_message(filters.command("setchat1") & filters.user(ADMINS))
async def set_chat1(bot, m):
    if len(m.command) == 1:
        return await m.reply("Usage: `/setchat1 channel_id`", quote=True)

    raw_id = m.text.split(" ", 1)[1]
    if temp.REQ_CHANNEL1:
        await db.update_loadout('channel1', None, bot.me.id)
        await db.delete_all_one()
        temp.REQ_CHANNEL1 = None
        bot.req_link1 = None

    try:
        chat = await bot.get_chat(int(raw_id))
    except ChatAdminRequired:
        return await m.reply("❌ Bot is not an admin in this channel.")
    except PeerIdInvalid:
        return await m.reply("❌ Invalid channel ID or bot not added.")
    except Exception as e:
        return await m.reply(f"❌ Error: {e}")

    try:
        link = (await bot.create_chat_invite_link(chat.id, creates_join_request=True)).invite_link
    except Exception as e:
        print(e)
        link = "None"

    await db.update_loadout('channel1', chat.id, bot.me.id)
    temp.REQ_CHANNEL1 = chat.id
    bot.req_link1 = link

    text = (
        f"✅ <b>Force Subscribe Channel 1 Added!</b>\n\n"
        f"Chat ID: <code>{chat.id}</code>\n"
        f"Chat Name: {chat.title}\n"
        f"Invite Link: {link}"
    )
    await m.reply(text, disable_web_page_preview=True)


@Client.on_message(filters.command("setchat2") & filters.user(ADMINS))
async def set_chat2(bot, m):
    if len(m.command) == 1:
        return await m.reply("Usage: `/setchat2 channel_id`", quote=True)

    raw_id = m.text.split(" ", 1)[1]
    if temp.REQ_CHANNEL2:
        await db.update_loadout('channel2', None, bot.me.id)
        await db.delete_all_two()
        temp.REQ_CHANNEL2 = None
        bot.req_link2 = None

    try:
        chat = await bot.get_chat(int(raw_id))
    except ChatAdminRequired:
        return await m.reply("❌ Bot is not an admin in this channel.")
    except PeerIdInvalid:
        return await m.reply("❌ Invalid channel ID or bot not added.")
    except Exception as e:
        return await m.reply(f"❌ Error: {e}")

    try:
        link = (await bot.create_chat_invite_link(chat.id, creates_join_request=True)).invite_link
    except Exception as e:
        print(e)
        link = "None"

    await db.update_loadout('channel2', chat.id, bot.me.id)
    temp.REQ_CHANNEL2 = chat.id
    bot.req_link2 = link

    text = (
        f"✅ <b>Force Subscribe Channel 2 Added!</b>\n\n"
        f"Chat ID: <code>{chat.id}</code>\n"
        f"Chat Name: {chat.title}\n"
        f"Invite Link: {link}"
    )
    await m.reply(text, disable_web_page_preview=True)


# ────────────────────────────────
# 🔹 View Force Subscribe Channels
# ────────────────────────────────
@Client.on_message(filters.command("viewchat1") & filters.user(ADMINS))
async def view_chat1(bot, m):
    if not temp.REQ_CHANNEL1:
        return await m.reply("❌ No channel set for Force Sub 1.")
    try:
        chat = await bot.get_chat(int(temp.REQ_CHANNEL1))
        link = bot.req_link1 if hasattr(bot, 'req_link1') else "No link available"
        count = await db.get_all_one_count()
        await m.reply(
            f"📢 <b>Force Subscribe Channel 1</b>\n\n"
            f"Name: {chat.title}\n"
            f"Chat ID: <code>{chat.id}</code>\n"
            f"Invite Link: {link}\n"
            f"Total Requests: {count}"
        )
    except Exception as e:
        await m.reply(f"Error: {e}")


@Client.on_message(filters.command("viewchat2") & filters.user(ADMINS))
async def view_chat2(bot, m):
    if not temp.REQ_CHANNEL2:
        return await m.reply("❌ No channel set for Force Sub 2.")
    try:
        chat = await bot.get_chat(int(temp.REQ_CHANNEL2))
        link = bot.req_link2 if hasattr(bot, 'req_link2') else "No link available"
        count = await db.get_all_two_count()
        await m.reply(
            f"📢 <b>Force Subscribe Channel 2</b>\n\n"
            f"Name: {chat.title}\n"
            f"Chat ID: <code>{chat.id}</code>\n"
            f"Invite Link: {link}\n"
            f"Total Requests: {count}"
        )
    except Exception as e:
        await m.reply(f"Error: {e}")


# ────────────────────────────────
# 🔹 Delete Force Subscribe Channels
# ────────────────────────────────
@Client.on_message(filters.command("delchat1") & filters.user(ADMINS))
async def del_chat1(bot, m):
    if not temp.REQ_CHANNEL1:
        return await m.reply("❌ No Force Sub Channel 1 set.")
    old_id = temp.REQ_CHANNEL1
    temp.REQ_CHANNEL1 = None
    bot.req_link1 = None
    await db.update_loadout('channel1', None, bot.me.id)
    await db.delete_all_one()
    await m.reply(f"✅ Force Sub Channel 1 Deleted.\nOld Chat ID: <code>{old_id}</code>")


@Client.on_message(filters.command("delchat2") & filters.user(ADMINS))
async def del_chat2(bot, m):
    if not temp.REQ_CHANNEL2:
        return await m.reply("❌ No Force Sub Channel 2 set.")
    old_id = temp.REQ_CHANNEL2
    temp.REQ_CHANNEL2 = None
    bot.req_link2 = None
    await db.update_loadout('channel2', None, bot.me.id)
    await db.delete_all_two()
    await m.reply(f"✅ Force Sub Channel 2 Deleted.\nOld Chat ID: <code>{old_id}</code>")


# ────────────────────────────────
# 🔹 Purge DB Requests
# ────────────────────────────────
@Client.on_message(filters.command("purge_one") & filters.user(ADMINS))
async def purge_one(bot, m):
    await db.delete_all_one()
    await m.reply("🧹 All Force Subscribe requests from Channel 1 cleared!")


@Client.on_message(filters.command("purge_two") & filters.user(ADMINS))
async def purge_two(bot, m):
    await db.delete_all_two()
    await m.reply("🧹 All Force Subscribe requests from Channel 2 cleared!")


# ────────────────────────────────
# 🔹 Total Requests
# ────────────────────────────────
@Client.on_message(filters.command("totalreq") & filters.user(ADMINS))
async def total_requests(bot, m):
    try:
        count1 = await db.get_all_one_count()
        count2 = await db.get_all_two_count()
        total = count1 + count2
        await m.reply(
            f"📊 <b>Total Force Subscribe Stats</b>\n\n"
            f"Channel 1 Requests: {count1}\n"
            f"Channel 2 Requests: {count2}\n"
            f"Total Combined: {total}"
        )
    except Exception as e:
        await m.reply(f"Error: {e}")
