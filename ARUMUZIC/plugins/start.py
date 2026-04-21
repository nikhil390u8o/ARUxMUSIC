import asyncio
from ARUMUZIC.clients import bot, assistant
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import config
import settings as S


@Client.on_message(filters.command("start"))
async def start_cmd(client, msg: Message):
    # Track user
    S.add_user(config.BOT_TOKEN, msg.from_user.id)
    if msg.chat.id != msg.from_user.id:
        S.add_group(config.BOT_TOKEN, msg.chat.id)

    try:
        await msg.delete()
    except:
        pass

    me           = await client.get_me()
    bot_name     = me.first_name
    bot_username = me.username

    START_IMG    = S.get(config.BOT_TOKEN, "start_img")
    support_link = S.get(config.BOT_TOKEN, "support_link")
    owner_name   = S.get(config.BOT_TOKEN, "owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"
    owner_id     = S.get(config.BOT_TOKEN, "owner_id") or config.CLONE_OWNER_ID

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
