import random
import asyncio
from ARUMUZIC.clients import bot
from pyrogram import filters, enums
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
import config
import settings as S

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

# ─── Welcome + Group Invite Detection ────────────────────────────────────────

@bot.on_chat_member_updated(filters.group)
async def welcome_handler(client, update: ChatMemberUpdated):
    if update.old_chat_member and update.old_chat_member.status != enums.ChatMemberStatus.LEFT:
        return
    if update.new_chat_member.status != enums.ChatMemberStatus.MEMBER:
        return
    if update.new_chat_member.user.is_self:
        return

    try:
        user       = update.new_chat_member.user
        name       = user.first_name or "User"
        user_id    = user.id
        chat_title = update.chat.title

        # Group invite detection (jab koi member ko add kare)
        if update.from_user and update.from_user.id != user_id:
            inviter      = update.from_user
            inviter_name = inviter.first_name or "User"
            text = (
                f"<a href='tg://user?id={inviter.id}'>{inviter_name}</a> "
                f"ɴᴇ ɪɴᴠɪᴛᴇ ᴋɪʏᴀ: "
                f"<a href='tg://user?id={user_id}'>{name}</a>"
            )
            inv_msg = await bot.send_message(update.chat.id, text)
            await asyncio.sleep(30)
            try:
                await inv_msg.delete()
            except:
                pass

        # Welcome message
        photo        = random.choice(WELCOME_IMAGES)
        caption      = WELCOME_TEXT.format(name=name, user_id=user_id, chat_title=chat_title)
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


# ─── VC Invite + Join Detection ───────────────────────────────────────────────

@bot.on_message(filters.group)
async def vc_service_handler(client, msg):
    try:
        # VC mein invite kiya kisi ko
        vc_invite = getattr(msg, "video_chat_participants_invited", None)
        if vc_invite:
            inviter = msg.from_user
            if inviter:
                inviter_name = inviter.first_name or "User"
                users = getattr(vc_invite, "users", []) or []
                for user in users:
                    invited_name = user.first_name or "User"
                    text = (
                        f"<a href='tg://user?id={inviter.id}'>{inviter_name}</a> "
                        f"ɴᴇ ɪɴᴠɪᴛᴇ ᴋɪʏᴀ: "
                        f"<a href='tg://user?id={user.id}'>{invited_name}</a> "
                        f"ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴘᴇ 🎙️"
                    )
                    notif = await bot.send_message(msg.chat.id, text)
                    await asyncio.sleep(30)
                    try:
                        await notif.delete()
                    except:
                        pass
            return

        # VC start/join
        vc_started = getattr(msg, "video_chat_started", None)
        if vc_started:
            user = msg.from_user
            if user and not user.is_bot:
                uname = user.first_name or "User"
                text = (
                    f"🎙️ <a href='tg://user?id={user.id}'>{uname}</a> "
                    f"<b>ᴠᴄ ᴘᴇ ᴊᴏɪɴ ʜᴏ ɢᴀʏᴀ!</b>"
                )
                notif = await bot.send_message(msg.chat.id, text)
                await asyncio.sleep(20)
                try:
                    await notif.delete()
                except:
                    pass

    except Exception as e:
        print(f"[VC SERVICE ERROR] {e}")
