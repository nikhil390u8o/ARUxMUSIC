import asyncio 
import aiohttp
import time
from urllib.parse import quote
from pyrogram.enums import ChatMemberStatus
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import AudioPiped, VideoPiped, HighQualityAudio, HighQualityVideo
from pytgcalls import PyTgCalls
import ARUMUZIC.clients as _clients
from ARUMUZIC.clients import bot, assistant

def get_call():
    return _clients.call

import config
import settings as S

MUSIC_API = "https://your-api.onrender.com"  # ← Apna Render URL daalo

# --- Configuration for Queues ---
if not hasattr(config, "queues"):
    config.queues = {}

# --- Utils ---
def fmt_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}" if hours > 0 else f"{minutes:02}:{seconds:02}"

def gen_btn_progressbar(total_sec, current_sec):
    bar_length = 9 
    if total_sec <= 0: total_sec = 1
    percentage = min(100, max(0, (current_sec / total_sec) * 100))
    filled_blocks = int(percentage / (100 / bar_length))
    bar = "▰" * filled_blocks + "▱" * (bar_length - filled_blocks)
    return f"{fmt_time(current_sec)} {bar} {fmt_time(total_sec)}"

# --- BUTTONS ---
def get_player_buttons(duration, elapsed=0, token=None):
    _token       = token or config.BOT_TOKEN
    cfg          = S.get_all(_token)
    support_link = cfg.get("support_link", "https://t.me/sxyaru")
    owner_name   = cfg.get("owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"
    owner_url    = f"https://t.me/{owner_name}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text=gen_btn_progressbar(duration, elapsed), callback_data="prog_update")],
        [
            InlineKeyboardButton("▷", "resume_cb"),
            InlineKeyboardButton("Ⅱ", "pause_cb"),
            InlineKeyboardButton("↺", "replay_cb"),
            InlineKeyboardButton("⏭", "skip_cb"),
            InlineKeyboardButton("▢", "stop_cb")
        ],
        [
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url=owner_url),
            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=support_link)
        ],
        [InlineKeyboardButton("🗑️ ᴄʟᴏsᴇ", callback_data="close_cb")]
    ])

# --- API CALL ---
async def fetch_stream(query: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{MUSIC_API}/stream?query={quote(query)}",
            timeout=aiohttp.ClientTimeout(total=30)
        ) as r:
            return await r.json()

# --- ASSISTANT JOIN ---
async def ensure_assistant(client, chat_id):
    ast_id = (await assistant.get_me()).id
    try:
        ast_member = await client.get_chat_member(chat_id, ast_id)
        if ast_member.status == ChatMemberStatus.BANNED:
            await client.unban_chat_member(chat_id, ast_id)
            invitelink = await client.export_chat_invite_link(chat_id)
            await assistant.join_chat(invitelink)
    except Exception:
        try:
            if hasattr(client, 'chat') and getattr(client.chat, 'username', None):
                await assistant.join_chat(client.chat.username)
            else:
                invitelink = await client.export_chat_invite_link(chat_id)
                await assistant.join_chat(invitelink)
        except Exception:
            pass

# --- PLAY NEXT (AUDIO) ---
async def play_next(chat_id: int):
    if chat_id not in config.queues or len(config.queues[chat_id]) <= 1:
        config.queues[chat_id] = []
        try: await get_call().leave_group_call(chat_id)
        except: pass
        return

    config.queues[chat_id].pop(0)
    song = config.queues[chat_id][0]
    title      = song["title"]
    duration   = song["duration"]
    user_name  = song["by"]
    thumb_url  = song["thumb"]     # ← YT thumbnail
    query      = song["query"]     # fresh URL ke liye

    try:
        # Fresh stream URL nikalo (purana expire ho sakta hai)
        data       = await fetch_stream(query)
        stream_url = data["audio_url"]

        try:
            await get_call().change_stream(chat_id, AudioPiped(stream_url, HighQualityAudio()))
        except:
            await get_call().join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))

        _token     = bot.bot_token
        cfg        = S.get_all(_token)
        owner_name = cfg.get("owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"
        owner_url  = f"https://t.me/{owner_name}"

        text = (
            f"<blockquote><b>❍ ɴᴇxᴛ sᴏɴɢ sᴛʀᴇᴀᴍ sᴛᴀʀᴛᴇᴅ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> {title}\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`</blockquote>"
            f"<b>‣ ʙᴏᴛ ʙᴀsᴇᴅ ᴏɴ : ᴀʀᴜ x ʏᴛ</b>\n"
            f"<b>‣ ᴀᴘɪ ᴍᴀᴅᴇ ʙʏ: <a href='{owner_url}'>{owner_name}</a></b>"
        )

        pmp = await bot.send_photo(chat_id, photo=thumb_url, caption=text,
                                   reply_markup=get_player_buttons(duration, token=_token))
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
    except:
        await play_next(chat_id)

# --- PLAY NEXT (VIDEO) ---
async def play_next_video(chat_id: int):
    if chat_id not in config.queues or len(config.queues[chat_id]) <= 1:
        config.queues[chat_id] = []
        try: await get_call().leave_group_call(chat_id)
        except: pass
        return

    config.queues[chat_id].pop(0)
    song = config.queues[chat_id][0]
    title     = song["title"]
    duration  = song["duration"]
    user_name = song["by"]
    thumb_url = song["thumb"]
    query     = song["query"]

    try:
        data      = await fetch_stream(query)
        video_url = data["video_url"]

        try:
            await get_call().change_stream(chat_id, VideoPiped(video_url, HighQualityVideo()))
        except:
            await get_call().join_group_call(chat_id, VideoPiped(video_url, HighQualityVideo()))

        _token     = bot.bot_token
        cfg        = S.get_all(_token)
        owner_name = cfg.get("owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"
        owner_url  = f"https://t.me/{owner_name}"

        text = (
            f"<blockquote><b>❍ ɴᴇxᴛ ᴠɪᴅᴇᴏ sᴛʀᴇᴀᴍ sᴛᴀʀᴛᴇᴅ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> {title}\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`</blockquote>"
            f"<b>‣ ʙᴏᴛ ʙᴀsᴇᴅ ᴏɴ : ᴀʀᴜ x ʏᴛ</b>\n"
            f"<b>‣ ᴀᴘɪ ᴍᴀᴅᴇ ʙʏ: <a href='{owner_url}'>{owner_name}</a></b>"
        )

        pmp = await bot.send_photo(chat_id, photo=thumb_url, caption=text,
                                   reply_markup=get_player_buttons(duration, token=_token))
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))
    except:
        await play_next_video(chat_id)

# --- STREAM END ---
@_clients.call.on_stream_end()
async def stream_end_handler(client, update):
    chat_id = update.chat_id
    if chat_id in config.queues and len(config.queues[chat_id]) > 1:
        mode = config.queues[chat_id][0].get("mode", "audio")
        if mode == "video":
            await play_next_video(chat_id)
        else:
            await play_next(chat_id)
    else:
        try:
            config.queues[chat_id] = []
            await get_call().leave_group_call(chat_id)
        except: pass

# --- TIMER UPDATE ---
async def update_timer(chat_id, message_id, duration):
    start_time = time.time()
    while True:
        await asyncio.sleep(15)
        if chat_id not in config.queues or not config.queues[chat_id]: break
        elapsed_time = min(duration, int(time.time() - start_time))
        if elapsed_time >= duration: break
        try:
            await bot.edit_message_reply_markup(
                chat_id, message_id,
                reply_markup=get_player_buttons(duration, elapsed_time)
            )
        except: break

# ══════════════════════════════════════════════
#  /play — AUDIO
# ══════════════════════════════════════════════
@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(client, msg: Message):
    try: await msg.delete()
    except: pass

    chat_id   = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"
    if len(msg.command) < 2:
        return await msg.reply("❌ **ɢɪᴠᴇ ᴀ ǫᴜᴇʀʏ!**")

    query = msg.text.split(None, 1)[1].strip()
    m     = await msg.reply("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b></blockquote>")

    await ensure_assistant(client, chat_id)

    # API Call
    try:
        data = await fetch_stream(query)
    except:
        return await m.edit("❌ **API Error! Try again.**")

    if "error" in data:
        return await m.edit(f"❌ **{data['error']}**")

    title      = data.get("title", "Unknown")
    duration   = int(data.get("duration", 0))
    stream_url = data.get("audio_url")
    thumb_url  = data.get("thumbnail")   # ← YouTube thumbnail ✅

    song_data = {
        "title": title, "url": stream_url, "duration": duration,
        "by": user_name, "thumb": thumb_url, "query": query, "mode": "audio"
    }

    if chat_id not in config.queues:
        config.queues[chat_id] = []

    # Queue check
    if len(config.queues[chat_id]) > 0:
        try:
            await get_call().get_call(chat_id)
            config.queues[chat_id].append(song_data)
            return await m.edit(
                f"<b>✅ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ (#{len(config.queues[chat_id])-1})</b>\n"
                f"🎵 **ᴛɪᴛʟᴇ:** {title}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("▷ ᴘʟᴀʏ ɴᴏᴡ", callback_data="skip_cb")
                ]])
            )
        except:
            config.queues[chat_id] = []

    config.queues[chat_id].append(song_data)
    await m.delete()

    try:
        await get_call().join_group_call(chat_id, AudioPiped(stream_url, HighQualityAudio()))

        _token     = client.bot_token
        cfg        = S.get_all(_token)
        owner_name = cfg.get("owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"
        owner_url  = f"https://t.me/{owner_name}"

        caption = (
            f"<b>❍ Sᴛᴀʀᴛᴇᴅ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> {title}\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`\n"
            f"<b>‣ ʙᴏᴛ ʙᴀsᴇᴅ ᴏɴ : ᴀʀᴜ x ʏᴛ</b>\n"
            f"<b>‣ ᴀᴘɪ ᴍᴀᴅᴇ ʙʏ: <a href='{owner_url}'>{owner_name}</a></b>"
        )

        pmp = await bot.send_photo(
            chat_id, photo=thumb_url,
            caption=caption,
            reply_markup=get_player_buttons(duration, token=_token)
        )
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))

    except Exception as e:
        if "No active group call" in str(e):
            return await bot.send_message(chat_id, "❌ **sᴛᴀʀᴛ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ғɪʀsᴛ!**")
        config.queues[chat_id] = []
        await bot.send_message(chat_id, f"❌ **Error:** {e}")

# ══════════════════════════════════════════════
#  /vplay — VIDEO
# ══════════════════════════════════════════════
@bot.on_message(filters.command("vplay") & filters.group)
async def vplay_cmd(client, msg: Message):
    try: await msg.delete()
    except: pass

    chat_id   = msg.chat.id
    user_name = msg.from_user.first_name if msg.from_user else "User"
    if len(msg.command) < 2:
        return await msg.reply("❌ **ɢɪᴠᴇ ᴀ ǫᴜᴇʀʏ!**")

    query = msg.text.split(None, 1)[1].strip()
    m     = await msg.reply("<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b></blockquote>")

    await ensure_assistant(client, chat_id)

    try:
        data = await fetch_stream(query)
    except:
        return await m.edit("❌ **API Error! Try again.**")

    if "error" in data:
        return await m.edit(f"❌ **{data['error']}**")

    title     = data.get("title", "Unknown")
    duration  = int(data.get("duration", 0))
    video_url = data.get("video_url")
    thumb_url = data.get("thumbnail")   # ← YouTube thumbnail ✅

    song_data = {
        "title": title, "url": video_url, "duration": duration,
        "by": user_name, "thumb": thumb_url, "query": query, "mode": "video"
    }

    if chat_id not in config.queues:
        config.queues[chat_id] = []

    if len(config.queues[chat_id]) > 0:
        try:
            await get_call().get_call(chat_id)
            config.queues[chat_id].append(song_data)
            return await m.edit(
                f"<b>✅ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ (#{len(config.queues[chat_id])-1})</b>\n"
                f"🎬 **ᴛɪᴛʟᴇ:** {title}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("▷ ᴘʟᴀʏ ɴᴏᴡ", callback_data="skip_cb")
                ]])
            )
        except:
            config.queues[chat_id] = []

    config.queues[chat_id].append(song_data)
    await m.delete()

    try:
        await get_call().join_group_call(chat_id, VideoPiped(video_url, HighQualityVideo()))

        _token     = client.bot_token
        cfg        = S.get_all(_token)
        owner_name = cfg.get("owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"
        owner_url  = f"https://t.me/{owner_name}"

        caption = (
            f"<b>❍ Sᴛᴀʀᴛᴇᴅ Vɪᴅᴇᴏ Sᴛʀᴇᴀᴍɪɴɢ |</b>\n\n"
            f"<b>‣ Tɪᴛʟᴇ :</b> {title}\n"
            f"<b>‣ Dᴜʀᴀᴛɪᴏɴ :</b> <code>{fmt_time(duration)}</code>\n"
            f"<b>‣ Rᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> `{user_name}`\n"
            f"<b>‣ ʙᴏᴛ ʙᴀsᴇᴅ ᴏɴ : ᴀʀᴜ x ʏᴛ</b>\n"
            f"<b>‣ ᴀᴘɪ ᴍᴀᴅᴇ ʙʏ: <a href='{owner_url}'>{owner_name}</a></b>"
        )

        pmp = await bot.send_photo(
            chat_id, photo=thumb_url,
            caption=caption,
            reply_markup=get_player_buttons(duration, token=_token)
        )
        asyncio.create_task(update_timer(chat_id, pmp.id, duration))

    except Exception as e:
        if "No active group call" in str(e):
            return await bot.send_message(chat_id, "❌ **sᴛᴀʀᴛ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ғɪʀsᴛ!**")
        config.queues[chat_id] = []
        await bot.send_message(chat_id, f"❌ **Error:** {e}")
