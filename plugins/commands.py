import os
import sys
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.ia_filterdb import Media2, Media3, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, REQ_CHANNEL1, REQ_CHANNEL2, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, PM_DEL
from utils import get_size, is_subscribed, is_requested_one, is_requested_two, temp, check_loop_sub, check_loop_sub1, check_loop_sub2
import re
import json
import base64
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta

should_run_check_loop_sub = False
should_run_check_loop_sub1 = False
BATCH_FILES = {}

DELETE_TXT = """❗️❗️❗️IMPORTANT❗️️❗️❗️

ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ 5 mins 🫥 (ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs).

ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴏʀ ᴀɴʏ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ."""

async def delete_messages(client, messages):
    for msg in messages:
        try:
            await msg.delete()
            print(f"Deleted message with ID: {msg.message_id}")
        except Exception as e:
            print(f"Failed to delete message with ID: {msg.message_id}. Error: {e}")


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply(
            script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.B_NAME
            ),
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown")
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )

    if len(message.command) != 2:
        await message.reply_text(
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            parse_mode=enums.ParseMode.HTML
        )
        return

    try:
        should_run_check_loop_sub = False
        should_run_check_loop_sub1 = False
        if temp.REQ_CHANNEL1 and not await is_requested_one(client, message):
            btn = [[InlineKeyboardButton("〄 Rᴇǫᴜᴇsᴛ Tᴏ Jᴏɪɴ Cʜᴀɴɴᴇʟ 1 〄", url=client.req_link1)]]
            should_run_check_loop_sub1 = True
            try:
                if temp.REQ_CHANNEL2 and not await is_requested_two(client, message):
                    btn.append([InlineKeyboardButton("〄 Rᴇǫᴜᴇsᴛ Tᴏ Jᴏɪɴ Cʜᴀɴɴᴇʟ 2 〄", url=client.req_link2)])
                    should_run_check_loop_sub = True
            except Exception as e:
                print(e)
            if message.command[1] != "subscribe":
                try:
                    kk, file_id = message.command[1].split("_", 1)
                    pre = 'checksubp' if kk == 'filep' else 'checksub'
                    btn.append([InlineKeyboardButton("〄 Tʀʏ Aɢᴀɪɴ 〄", callback_data=f"{pre}#{file_id}")])
                except (IndexError, ValueError):
                    btn.append([InlineKeyboardButton("〄 Tʀʏ Aɢᴀɪɴ 〄", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            sh = await client.send_message(
                chat_id=message.from_user.id,
                text='📢 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐓𝐨 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 📢  ക്ലിക്ക് ചെയ്ത ശേഷം 🔄 𝐓𝐫𝐲 𝐀𝐠𝐚𝐢𝐧 🔄 എന്ന ബട്ടണിൽ അമർത്തിയാൽ നിങ്ങൾക്ക് ഞാൻ ആ സിനിമ അയച്ചു തരുന്നതാണ് 😍',
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            if should_run_check_loop_sub:
                check = await check_loop_sub(client, message)
            elif should_run_check_loop_sub1:
                check = await check_loop_sub1(client, message)
            if check:
                await sh.delete()
            else:
                return
    except Exception as e:
        return await message.reply(e)

    if temp.REQ_CHANNEL2 and not await is_requested_two(client, message):
        btn = [[InlineKeyboardButton("Join channel", url=client.req_link2)]]
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append([InlineKeyboardButton(" 🔄 Tʀʏ Aɢᴀɪɴ 🔄", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(" 🔄 Tʀʏ Aɢᴀɪɴ 🔄", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        sh = await client.send_message(
            chat_id=message.from_user.id,
            text="Request To Join This Channel",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        check = await check_loop_sub2(client, message)
        if check:
            await sh.delete()
        else:
            return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        await message.reply_text(
            text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            parse_mode=enums.ParseMode.HTML
        )
        return

    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""

    files_ = await get_file_details(file_id)
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                fileid=file_id,
                protect_content=True if pre == 'filep' else False,
            )
            filetype = msg.media
            file = getattr(msg, filetype)
            title = file.file_name
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name='' if title is None else title,
                        file_size='' if size is None else size,
                        file_caption=''
                    )
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')

    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name='' if title is None else title,
                file_size='' if size is None else size,
                file_caption=title if f_caption is None else f_caption
            )
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    try:
        ok = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
        )
    except Exception as e:
        print(e)
    da = await ok.reply(f"```{DELETE_TXT}```")
    await message.delete()
    await asyncio.sleep(300)
    await ok.delete()
    await da.delete()
    btn = [[InlineKeyboardButton(text="ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ", callback_data=f'{pre}#{file_id}')]]
    await message.reply(
        text="✅ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴀɢᴀɪɴ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ",
        reply_markup=InlineKeyboardMarkup(btn)
    )
