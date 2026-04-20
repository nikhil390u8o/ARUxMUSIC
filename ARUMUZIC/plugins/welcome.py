import random
import asyncio
from ARUMUZIC.clients import bot 
from pyrogram import filters, enums
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton

# --- Random Welcome Images ---
WELCOME_IMAGES = [
    "https://files.catbox.moe/nacfzm.jpg",
    "https://files.catbox.moe/x4lzbx.jpg",
    "https://files.catbox.moe/g6cmb2.jpg",
    "https://files.catbox.moe/3hxb96.jpg",
    "https://files.catbox.moe/3h3vqz.jpg",
    "https://files.catbox.moe/yah7a9.jpg"
]

WELCOME_TEXT = """🌸✨ ──────────────────── ✨🌸  
🎊 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ɢʀᴏᴜᴘ</b> 🎊  
  
🌹 <b>ɴᴀᴍᴇ</b> ➤ {name}  
🆔 <b>ᴜsᴇʀ ɪᴅ</b> ➤ <code>{user_id}</code>  
🏠 <b>ɢʀᴏᴜᴘ</b> ➤ {chat_title}  
  
💕 <b>ᴡᴇ'ʀᴇ sᴏ ʜᴀᴘᴘʏ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!</b>  
✨ <b>ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ sʜᴀʀᴇ ᴀɴᴅ ᴇɴᴊᴏʏ!</b>  
⚡ <b>ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴇxᴘᴇʀɪᴇɴᴄᴇ ᴡɪᴛʜ ᴛʜɪs ʙᴏᴛ</b>  
  
💝 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ ➤</b> <a href="https://t.me/sxyaru">˹ᴀʀᴜ × ᴀᴘɪ˼ × [ʙᴏᴛs]</a>  
🌸✨ ──────────────────── ✨🌸  
"""

# NEW METHOD: Chat Member Updated logic
@bot.on_chat_member_updated(filters.group)
async def welcome_updated_logic(client, update: ChatMemberUpdated):
    # Check karo agar naya member sach mein JOIN hua hai
    if update.old_chat_member and update.old_chat_member.status != enums.ChatMemberStatus.LEFT:
        return
    if update.new_chat_member.status != enums.ChatMemberStatus.MEMBER:
        return

    # Bot khud join kare toh welcome skip
    if update.new_chat_member.user.is_self:
        return

    try:
        user = update.new_chat_member.user
        name = user.first_name or "User"
        user_id = user.id
        chat_title = update.chat.title
        
        photo = random.choice(WELCOME_IMAGES)
        
        caption = WELCOME_TEXT.format(
            name=name, 
            user_id=user_id, 
            chat_title=chat_title
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url="https://t.me/sxyaru"),
                InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="https://t.me/ll_PANDA_BBY_ll")
            ]
        ])

        # Photo send karna
        wel_msg = await bot.send_photo(
            chat_id=update.chat.id,
            photo=photo,
            caption=caption,
            reply_markup=buttons
        )

        # 60 Seconds baad auto-delete
        await asyncio.sleep(60)
        try:
            await wel_msg.delete()
        except:
            pass

    except Exception as e:
        print(f"[WELCOME ERROR] {e}")
