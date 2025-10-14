# Kanged From @TroJanZheX
import asyncio
import re, traceback
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, AUTO_DEL, PM_DEL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, temp
from database.users_chats_db import db
from database.ia_filterdb import get_file_details, get_search_results, get_bad_files, Media2, Media3, db as clientDB, db2 as clientDB2, db3 as clientDB3
from database.gfilters_mdb import find_gfilter, get_gfilters
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.text & filters.incoming & filters.group)
async def give_filter(client, message):
    ok = await global_filters(client, message)
    if ok == False:
        await auto_filter(client, message)       
        
@Client.on_message(filters.private & filters.incoming)
async def give_fpm(client, message):
    ok = await global_filters(client, message)
    if ok == False:
        await auto_filter(client, message)   
  
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    btn = [
        [
            InlineKeyboardButton(
                text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
            ),
        ]
        for file in files
    ]
    
    if 0 < offset <= 8:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 8
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 8) + 1} / {math.ceil(total / 8)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 8) + 1} / {math.ceil(total / 8)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 8) + 1} / {math.ceil(total / 8)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()                        
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption = title if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"        
        try:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
            return         
        except QueryIdInvalid:
            await query.answer("This query is no longer valid.", show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if temp.REQ_CHANNEL1 and not await is_requested_one(client, query):
            await query.answer("നിങ്ങൾ മുകളിൽ കാണുന്ന ചാനലിൽ ജോയിൻ ആയിട്ടില്ല❌ ഒന്നൂടെ ആയി നോക്കുക ശേഷം സിനിമ വരും✅\n\n𝗌𝗈𝗅𝗏𝖾 𝗂𝗌𝗌𝗎𝖾?-𝖨𝖿 𝖳𝗁𝖾𝗋𝖾 𝖠𝗋𝖾 2 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖳𝗈 𝖩𝗈𝗂𝗇, 𝖩𝗈𝗂𝗇 𝖥𝗂𝗋𝗌𝗍 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖳𝗁𝖾𝗇 𝖩𝗈𝗂𝗇 𝖳𝗁𝖾 𝖲𝖾𝖼𝗈𝗇𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝗔𝗳𝘁𝗲𝗿 5𝘀𝗲𝗰", show_alert=True)
            return
        if temp.REQ_CHANNEL2 and not await is_requested_two(client, query):
            await query.answer("Update Channel 2 ഒന്നൂടെ ജോയിൻ ആവുക എന്നിട്ട് Try Again ക്ലിക്ക് ചെയ്യുക സിനിമ കിട്ടുന്നതാണ്🫶🏼\n\n𝗌𝗈𝗅𝗏𝖾 𝗂𝗌𝗌𝗎𝖾?-𝖨𝖿 𝖳𝗁𝖾𝗋𝖾 𝖠𝗋𝖾 2 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖳𝗈 𝖩𝗈𝗂𝗇, 𝖩𝗈𝗂𝗇 𝖥𝗂𝗋𝗌𝗍 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖳𝗁𝖾𝗇 𝖩𝗈𝗂𝗇 𝖳𝗁𝖾 𝖲𝖾𝖼𝗈𝗇𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝗔𝗳𝘁𝗲𝗿 5𝘀𝗲𝗰", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.file_name
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"        
        await query.answer()
        xd = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == "checksubp" else False            
        )
        replied = xd.id    
        da = await message.reply(DELETE_TXT, reply_to_message_id=replied)
        await asyncio.sleep(30)
        await message.delete()
        await da.delete()
        await asyncio.sleep(PM_DEL)
        await xd.delete()
    elif query.data == "pages":
        await query.answer("ok da", show_alert=True)
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        files_media1, files_media2, total_media = await get_bad_files(keyword)        
        await query.message.edit_text(f"<b>Fᴏᴜɴᴅ {total_media} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>")
        await asyncio.sleep(5)
        deleted = 0
        async with lock:
            try:
                # Delete files from Media collection
                for file in files_media1:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media2.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
                # Delete files from Mediaa collection
                for file in files_media2:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media3.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            except Exception as e:
                logger.exception
                await query.message.edit_text(f'Eʀʀᴏʀ: {e}')
            else:
                await query.message.edit_text(f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>")
            
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('🔗 OUR CHANELS LINKS 🔗', url=f'https://t.me/MC_CINEMAS')
            ],[
            InlineKeyboardButton('📌 MY GROUP', url=f'https://t.me/+x2Gy5vsCW0xhOTA1'),
            InlineKeyboardButton('🛠 MY OWNER', url='https://t.me/Leomc_bot')
            ],[      
            InlineKeyboardButton('🪬ʜᴇʟᴘ🪬', callback_data='help'),
            InlineKeyboardButton('✨ ᴀʙᴏᴜᴛ',  callback_data='about')
            ],[
            InlineKeyboardButton('➕ ADD ME TO YOUR GROUP ➕', url='https://t.me/Mc_elsa_v10_bot?startgroup=true')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')    
    elif query.data == "stats":
        await query.message.edit_text(text="ᴘʟᴇᴀꜱʀ ᴡᴀɪᴛ ꜱᴛᴀᴛᴜꜱ ɪꜱ ʟᴏᴀᴅɪɴɢ...")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        tot1 = await Media2.count_documents()
        tot2 = await Media3.count_documents()
        total = tot1 + tot2
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        stats = await clientDB.command('dbStats')
        used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))        
        stats2 = await clientDB2.command('dbStats')
        used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
        stats3 = await clientDB3.command('dbStats')
        used_dbSize3 = (stats3['dataSize']/(1024*1024))+(stats3['indexSize']/(1024*1024))
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, round(used_dbSize, 2), tot1, round(used_dbSize2, 2), tot2, round(used_dbSize3, 2)),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 150:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:                
                okd = await msg.reply(
                   text="🎬 **Movie Not Found / മൂവി കണ്ടില്ല** 😔\n\n"
                    "Your spelling might be incorrect or the movie is not yet indexed.\n"
                    "നിങ്ങളുടെ സ്പെല്ലിംഗ് തെറ്റായിരിക്കാം അല്ലെങ്കിൽ മൂവി ഇന്റക്സുചെയ്യപ്പെട്ടിട്ടില്ല.\n\n"
                    "🔹 Please search the movie on Google 🔍 and copy the correct name.\n"
                    "   Google-ൽ മൂവി തിരയുക 🔍, ശരിയായ പേരു കോപ്പി ചെയ്ത് ഇവിടെ അയയ്ക്കുക.\n\n"
                    "🔹 Send the movie name with release year, e.g., `Marco 2024`.\n"
                    "   റിലീസ് വർഷം കൂടി ചേർത്തു അയയ്ക്കുക, ഉദാ: `Marco 2024`.\n\n"
                    "🔹 Make sure the movie is released on OTT.\n"
                    "   മൂവി OTT-ൽ റിലീസ് ആയതാണെന്ന് ഉറപ്പാക്കുക.",                    
                    reply_to_message_id=msg.id,
                    parse_mode=None,
                    disable_web_page_preview=True
                )
                await client.schedule.add_job(okd.delete, 'date', run_date=datetime.now() + timedelta(seconds=15))
                return
        else:
            return
    else:      
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'file'
    btn = [
        [
            InlineKeyboardButton(
                text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'
            ),
        ]
        for file in files
    ]
    if total_results <= 8:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    else:
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 8)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )    
    cap = f"Here is what i found {total_results} for your query {search}"
    ok = await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=None, disable_web_page_preview=True)
    await client.schedule.add_job(ok.delete, 'date', run_date=datetime.now() + timedelta(seconds=AUTO_DEL))
        
async def global_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            knd3 = await client.send_message(
                                group_id, 
                                reply_text, 
                                parse_mode=None,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(60)
                            await knd3.delete()
                            await message.delete()

                        else:
                            button = eval(btn)
                            knd2 = await client.send_message(
                                group_id,
                                reply_text,
                                parse_mode=None,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(60)
                            await knd2.delete()
                            await message.delete()

                    elif btn == "[]":
                        knd1 = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id,
                            parse_mode=None,
                            disable_web_page_preview=True
                        )
                        await asyncio.sleep(60)
                        await knd1.delete()
                        await message.delete()

                    else:
                        button = eval(btn)
                        knd = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id,
                            parse_mode=None,
                            disable_web_page_preview=True
                        )
                        await asyncio.sleep(60)
                        await knd.delete()
                        await message.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
