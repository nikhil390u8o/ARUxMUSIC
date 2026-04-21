import asyncio
from ARUMUZIC.clients import bot, assistant, call
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
import settings as S


@Client.on_message(filters.command("start"))
async def start_cmd(client, msg: Message):
    try:
        await msg.delete()
    except:
        pass

    me = await client.get_me()
    bot_name     = me.first_name
    bot_username = me.username

    # ── Dynamic settings ────────────────────────────────────────────────────
    token = client.bot_token

    START_IMG    = S.get(token, "start_img")
    support_link = S.get(token, "support_link")
    owner_id     = S.get(token, "owner_id")
    owner_name   = S.get(token, "owner_username") or "sxyaru"

    # ── Animation ───────────────────────────────────────────────────────────
    m = await client.send_message(msg.chat.id, "<code>ʜᴇʏ...</code>")
    await asyncio.sleep(0.8)
    await m.edit_text("<code>ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ? ✨</code>")
    await asyncio.sleep(0.8)
    await m.edit_text(f"<code>ɪ ᴀᴍ {bot_name} 🎵\nsᴛᴀʀᴛɪɴɢ.....</code>")
    await asyncio.sleep(1.0)
    await m.delete()

    text = (
        "<b>╔══════════════════╗</b>\n"
        "<b>   🎵 ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ 🎵   </b>\n"
        "<b>╚══════════════════╝</b>\n\n"
        "<b>👋 ʜᴇʟʟᴏ! ɪ ᴀᴍ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ</b>\n"
        "<b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.</b>\n\n"
        f"✨ <b>ᴍᴀᴅᴇ ᴡɪᴛʜ ❤️ ʙʏ:</b> <a href='https://t.me/{owner_name}'>ᴀʀᴜ x ᴀᴘɪ [ʙᴏᴛs]</a>\n"
        "<b>ᴛʜɪs ʙᴏᴛ ɪs ʙᴀsᴇᴅ ᴏɴ ᴊɪᴏ sᴀᴠᴀɴ ᴀᴜᴅɪᴏ ᴀᴘɪ ɴᴏ ᴠɪᴅᴇᴏ ᴘʟᴀʏ ғᴜɴᴄᴛɪᴏɴ 👽</b>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help_menu"),
            InlineKeyboardButton("📂 ʀᴇᴘᴏ", callback_data="repo_menu")
        ],
        [
            InlineKeyboardButton("👤 ᴏᴡɴᴇʀ", url=f"https://t.me/{owner_name}"),
            InlineKeyboardButton("📢 sᴜᴘᴘᴏʀᴛ", url=support_link)
        ],
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                                 url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ])

    await client.send_photo(
        msg.chat.id,
        photo=START_IMG,
        caption=text,
        reply_markup=buttons
    )
