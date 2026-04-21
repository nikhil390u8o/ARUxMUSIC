import random
import asyncio
from ARUMUZIC.clients import bot, call
from pyrogram import filters, enums
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import Update
import config
import settings as S

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

# ─── Welcome + Invite Detection ──────────────────────────────────────────────

@bot.on_chat_member_updated(filters.group)
async def welcome_updated_logic(client, update: ChatMemberUpdated):
    # Sirf naye members ke liye
    if update.old_chat_member and update.old_chat_member.status != enums.ChatMemberStatus.LEFT:
        return
    if update.new_chat_member.status != enums.ChatMemberStatus.MEMBER:
        return
    if update.new_chat_member.user.is_self:
        return

    try:
        user      = update.new_chat_member.user
        name      = user.first_name or "User"
        user_id   = user.id
        chat_title = update.chat.title

        # ── Invite detection ─────────────────────────────────────────────────
        # update.from_user = jisne invite kiya
        # update.new_chat_member.user = jisko invite kiya
        if update.from_user and update.from_user.id != user_id:
            inviter      = update.from_user
            inviter_name = inviter.first_name or "User"
            invited_name = name

            invite_text = (
                f"<a href='tg://user?id={inviter.id}'>{inviter_name}</a> "
                f"ɴᴇ ɪɴᴠɪᴛᴇ ᴋɪʏᴀ: "
                f"<a href='tg://user?id={user_id}'>{invited_name}</a>"
            )
            inv_msg = await bot.send_message(update.chat.id, invite_text)
            await asyncio.sleep(30)
            try:
                await inv_msg.delete()
            except:
                pass

        # ── Welcome message ──────────────────────────────────────────────────
        photo   = random.choice(WELCOME_IMAGES)
        caption = WELCOME_TEXT.format(
            name=name,
            user_id=user_id,
            chat_title=chat_title
        )

        support_link = S.get(config.BOT_TOKEN, "support_link")
        owner_name   = S.get(config.BOT_TOKEN, "owner_username") or "sxyaru"

        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url=support_link),
            InlineKeyboardButton(f"• @{owner_name} •", url=f"https://t.me/{owner_name}")
        ]])

        wel_msg = await bot.send_photo(
            chat_id=update.chat.id,
            photo=photo,
            caption=caption,
            reply_markup=buttons
        )

        await asyncio.sleep(60)
        try:
            await wel_msg.delete()
        except:
            pass

    except Exception as e:
        print(f"[WELCOME ERROR] {e}")


# ─── VC Join Notification ─────────────────────────────────────────────────────

@call.on_participants_change()
async def vc_join_handler(_, update: Update):
    try:
        # Sirf join events
        if not hasattr(update, "participants"):
            return

        for participant in update.participants:
            if not getattr(participant, "just_joined", False):
                continue

            user_id   = participant.user_id
            chat_id   = update.chat_id

            # Bot khud join kare to skip
            me = await bot.get_me()
            if user_id == me.id:
                continue

            try:
                user = await bot.get_users(user_id)
                uname = user.first_name or "User"
            except:
                uname = f"User {user_id}"

            vc_text = (
                f"🎙️ <a href='tg://user?id={user_id}'>{uname}</a> "
                f"<b>ᴠᴄ ᴘᴇ ᴊᴏɪɴ ʜᴏ ɢᴀʏᴀ!</b>"
            )

            msg = await bot.send_message(chat_id, vc_text)
            await asyncio.sleep(20)
            try:
                await msg.delete()
            except:
                pass

    except Exception as e:
        print(f"[VC JOIN ERROR] {e}")


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
