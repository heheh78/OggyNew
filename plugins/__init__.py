import asyncio
import traceback
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid
from info import ADMINS
from database.users_chats_db import db
from utils import temp


# 🧠 Hidden credit (Base64 encoded)
_secret_credit = base64.b64decode("4pyTIMKpIMKpIMKpIMKpIMKpIMKpIMKpIMKpIMKpIMKpIMKpICZhbXA7Q3liZXJfRmNyYWNrZXImYW1wOw==").decode()

def _verify_credit():
    if "Cyber_Fcracker" not in _secret_credit:
        raise SystemExit("❌ Code Tampered: Credit Removed or Modified!")


# ────────────────────────────────
# 📥 Handle join requests
# ────────────────────────────────
@Client.on_chat_join_request()
async def join_request_handler(_, req: ChatJoinRequest):
    try:
        user_id = req.from_user.id
        chat_id = req.chat.id

        if chat_id == temp.REQ_CHANNEL1:
            await db.add_req_one(user_id)
        elif chat_id == temp.REQ_CHANNEL2:
            await db.add_req_two(user_id)

    except Exception as e:
        print(f"[JoinReq Error] {e}")


# ────────────────────────────────
# ⚙️ Force Subscribe Commands Help
# ────────────────────────────────
@Client.on_message(filters.command("fusub") & filters.user(ADMINS))
async def fusub_help(_, m):
    _verify_credit()  # Credit verification before execution

    btns = [
        [InlineKeyboardButton("📢 View Chat 1", callback_data="viewchat:1"),
         InlineKeyboardButton("📢 View Chat 2", callback_data="viewchat:2")],
        [InlineKeyboardButton("🧹 Purge One", callback_data="purge:1"),
         InlineKeyboardButton("🧹 Purge Two", callback_data="purge:2")],
        [InlineKeyboardButton("📊 Total Stats", callback_data="totalreq")]
    ]

    text = (
        "<b>🧩 Force Subscribe Control Panel</b>\n\n"
        "• Use the below buttons to manage Force Subscribe channels easily.\n"
        "• Or use manual commands if needed:\n\n"
        "<b>Manual Commands</b>\n"
        "— /setchat1 [id] → Set Channel 1\n"
        "— /setchat2 [id] → Set Channel 2\n"
        "— /delchat1 → Delete Channel 1\n"
        "— /delchat2 → Delete Channel 2\n"
        "— /purge_one → Clear DB 1\n"
        "— /purge_two → Clear DB 2\n"
        "— /totalreq → Show Total Requests\n\n"
        f"© <a href='https://t.me/Cyber_Fcracker'>@Cyber_Fcracker</a>"
    )
    await m.reply(text, reply_markup=InlineKeyboardMarkup(btns), disable_web_page_preview=True)


# ────────────────────────────────
# 📋 Inline Panel Actions
# ────────────────────────────────
@Client.on_callback_query(filters.regex(r"viewchat:(\d)"))
async def view_chat(bot, cq):
    _verify_credit()

    ch = cq.data.split(":")[1]
    try:
        if ch == "1":
            if not temp.REQ_CHANNEL1:
                return await cq.answer("❌ Channel 1 not set.", show_alert=True)
            chat = await bot.get_chat(temp.REQ_CHANNEL1)
            count = await db.get_all_one_count()
            link = getattr(bot, "req_link1", "No link available")
        else:
            if not temp.REQ_CHANNEL2:
                return await cq.answer("❌ Channel 2 not set.", show_alert=True)
            chat = await bot.get_chat(temp.REQ_CHANNEL2)
            count = await db.get_all_two_count()
            link = getattr(bot, "req_link2", "No link available")

        text = (
            f"📢 <b>Force Subscribe Channel {ch}</b>\n\n"
            f"Name: {chat.title}\n"
            f"ID: <code>{chat.id}</code>\n"
            f"Invite: {link}\n"
            f"Total Requests: {count}\n\n"
            f"{_secret_credit}"
        )
        btns = [
            [InlineKeyboardButton("🔄 Refresh Link", callback_data=f"refresh:{ch}"),
             InlineKeyboardButton("🗑️ Delete", callback_data=f"delete:{ch}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_fusub")]
        ]
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), disable_web_page_preview=True)

    except Exception as e:
        await cq.answer(f"❌ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex(r"refresh:(\d)"))
async def refresh_link(bot, cq):
    _verify_credit()
    ch = cq.data.split(":")[1]
    try:
        if ch == "1" and temp.REQ_CHANNEL1:
            new_link = (await bot.create_chat_invite_link(temp.REQ_CHANNEL1, creates_join_request=True)).invite_link
            bot.req_link1 = new_link
            await cq.answer("✅ Channel 1 link refreshed!", show_alert=True)
        elif ch == "2" and temp.REQ_CHANNEL2:
            new_link = (await bot.create_chat_invite_link(temp.REQ_CHANNEL2, creates_join_request=True)).invite_link
            bot.req_link2 = new_link
            await cq.answer("✅ Channel 2 link refreshed!", show_alert=True)
        else:
            await cq.answer("❌ Channel not set.", show_alert=True)
    except Exception as e:
        await cq.answer(f"❌ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex(r"delete:(\d)"))
async def delete_channel(bot, cq):
    _verify_credit()
    ch = cq.data.split(":")[1]
    try:
        if ch == "1" and temp.REQ_CHANNEL1:
            old = temp.REQ_CHANNEL1
            temp.REQ_CHANNEL1 = None
            bot.req_link1 = None
            await db.update_loadout('channel1', None, bot.me.id)
            await db.delete_all_one()
            await cq.answer(f"✅ Channel 1 ({old}) deleted.", show_alert=True)
        elif ch == "2" and temp.REQ_CHANNEL2:
            old = temp.REQ_CHANNEL2
            temp.REQ_CHANNEL2 = None
            bot.req_link2 = None
            await db.update_loadout('channel2', None, bot.me.id)
            await db.delete_all_two()
            await cq.answer(f"✅ Channel 2 ({old}) deleted.", show_alert=True)
        else:
            await cq.answer("❌ Channel not set.", show_alert=True)
    except Exception as e:
        await cq.answer(f"❌ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex(r"purge:(\d)"))
async def purge_data(bot, cq):
    _verify_credit()
    ch = cq.data.split(":")[1]
    if ch == "1":
        await db.delete_all_one()
        await cq.answer("🧹 Channel 1 DB cleared.", show_alert=True)
    else:
        await db.delete_all_two()
        await cq.answer("🧹 Channel 2 DB cleared.", show_alert=True)


@Client.on_callback_query(filters.regex("totalreq"))
async def total_req_cb(bot, cq):
    _verify_credit()
    try:
        c1 = await db.get_all_one_count()
        c2 = await db.get_all_two_count()
        total = c1 + c2
        text = (
            f"📊 <b>Total Force Subscribe Stats</b>\n\n"
            f"Channel 1: {c1}\nChannel 2: {c2}\nTotal: {total}\n\n"
            f"{_secret_credit}"
        )
        btns = [[InlineKeyboardButton("⬅️ Back", callback_data="back_fusub")]]
        await cq.answer()
        await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(btns), disable_web_page_preview=True)
    except Exception as e:
        await cq.answer(f"❌ Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("back_fusub"))
async def back_to_main(_, cq):
    _verify_credit()
    await fusub_help(_, cq.message)


# ────────────────────────────────
# 💾 Set Channels
# ────────────────────────────────
@Client.on_message(filters.command("setchat1") & filters.user(ADMINS))
async def set_chat1(bot, m):
    _verify_credit()
    if len(m.command) == 1:
        return await m.reply("Usage: /setchat1 channel_id")

    cid = m.text.split(" ", 1)[1]
    try:
        chat = await bot.get_chat(int(cid))
        link = (await bot.create_chat_invite_link(chat.id, creates_join_request=True)).invite_link
    except PeerIdInvalid:
        return await m.reply("❌ Invalid channel or bot not added.")
    except ChatAdminRequired:
        return await m.reply("❌ Bot must be admin in that channel.")
    except Exception as e:
        return await m.reply(f"❌ Error: {e}")

    await db.update_loadout('channel1', chat.id, bot.me.id)
    temp.REQ_CHANNEL1 = chat.id
    bot.req_link1 = link

    await m.reply(f"✅ Channel 1 Set:\n<b>{chat.title}</b>\nID: <code>{chat.id}</code>\nInvite: {link}\n\n{_secret_credit}")


@Client.on_message(filters.command("setchat2") & filters.user(ADMINS))
async def set_chat2(bot, m):
    _verify_credit()
    if len(m.command) == 1:
        return await m.reply("Usage: /setchat2 channel_id")

    cid = m.text.split(" ", 1)[1]
    try:
        chat = await bot.get_chat(int(cid))
        link = (await bot.create_chat_invite_link(chat.id, creates_join_request=True)).invite_link
    except PeerIdInvalid:
        return await m.reply("❌ Invalid channel or bot not added.")
    except ChatAdminRequired:
        return await m.reply("❌ Bot must be admin in that channel.")
    except Exception as e:
        return await m.reply(f"❌ Error: {e}")

    await db.update_loadout('channel2', chat.id, bot.me.id)
    temp.REQ_CHANNEL2 = chat.id
    bot.req_link2 = link

    await m.reply(f"✅ Channel 2 Set:\n<b>{chat.title}</b>\nID: <code>{chat.id}</code>\nInvite: {link}\n\n{_secret_credit}")


# ────────────────────────────────
# 📊 Total Request command
# ────────────────────────────────
@Client.on_message(filters.command("totalreq") & filters.user(ADMINS))
async def totalreq(bot, m):
    _verify_credit()
    c1 = await db.get_all_one_count()
    c2 = await db.get_all_two_count()
    await m.reply(
        f"📊 Force Subscribe Stats\n\nChannel 1: {c1}\nChannel 2: {c2}\nTotal: {c1 + c2}\n\n{_secret_credit}"
          )
