import random
import asyncio
from ARUMUZIC.clients import bot
from pyrogram import Client, filters, enums
from pyrogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
import config
import settings as S

WELCOME_IMAGES = [
    "https://files.catbox.moe/nacfzm.jpg",
    "https://files.catbox.moe/x4lzbx.jpg",
    "https://files.catbox.moe/g6cmb2.jpg",
    "https://files.catbox.moe/3hxb96.jpg",
]

WELCOME_TEXT = """🌸✨ ──────────────────── ✨🌸
🎊 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏᴜʀ ɢʀᴏᴜᴘ</b> 🎊

🌹 <b>ɴᴀᴍᴇ</b> ➤ {name}
🆔 <b>ᴜsᴇʀ ɪᴅ</b> ➤ <code>{user_id}</code>
🏠 <b>ɢʀᴏᴜᴘ</b> ➤ {chat_title}

💕 <b>ᴡᴇ'ʀᴇ sᴏ ʜᴀᴘᴘʏ ᴛᴏ ʜᴀᴠᴇ ʏᴏᴜ ʜᴇʀᴇ!</b>
🌸✨ ──────────────────── ✨🌸
"""


# ─── Welcome ──────────────────────────────────────────────────────────────────

@Client.on_chat_member_updated(filters.group)
async def welcome_handler(client, update: ChatMemberUpdated):
    try:
        old = update.old_chat_member
        new = update.new_chat_member

        if old and old.status not in (
            enums.ChatMemberStatus.LEFT,
            enums.ChatMemberStatus.BANNED
        ):
            return
        if new.status != enums.ChatMemberStatus.MEMBER:
            return
        if new.user.is_self or new.user.is_bot:
            return

        user       = new.user
        name       = user.first_name or "User"
        user_id    = user.id
        chat_title = update.chat.title

        # Track
        S.add_user(config.BOT_TOKEN, user_id)
        S.add_group(config.BOT_TOKEN, update.chat.id)

        # Invite detection
        if update.from_user and update.from_user.id != user_id:
            inv  = update.from_user
            text = (
                f"<a href='tg://user?id={inv.id}'>{inv.first_name or 'User'}</a> "
                f"ɴᴇ ɪɴᴠɪᴛᴇ ᴋɪʏᴀ: "
                f"<a href='tg://user?id={user_id}'>{name}</a>"
            )
            inv_msg = await client.send_message(update.chat.id, text)
            await asyncio.sleep(30)
            try: await inv_msg.delete()
            except: pass

        # Welcome
        support_link = S.get(config.BOT_TOKEN, "support_link")
        owner_name   = S.get(config.BOT_TOKEN, "owner_username") or "sxyaru"
        photo        = random.choice(WELCOME_IMAGES)
        caption      = WELCOME_TEXT.format(name=name, user_id=user_id, chat_title=chat_title)

        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("• ᴄʜᴀɴɴᴇʟ •", url=support_link),
            InlineKeyboardButton(f"• @{owner_name} •", url=f"https://t.me/{owner_name}")
        ]])

        wel = await client.send_photo(
            update.chat.id, photo=photo, caption=caption, reply_markup=buttons
        )
        await asyncio.sleep(60)
        try: await wel.delete()
        except: pass

    except Exception as e:
        print(f"[WELCOME ERROR] {e}")


# ─── VC Invite (service messages) ────────────────────────────────────────────

@Client.on_message(filters.group)
async def vc_service_handler(client, msg):
    try:
        # VC invite
        vc_inv = getattr(msg, "video_chat_participants_invited", None)
        if vc_inv:
            inviter = msg.from_user
            if not inviter:
                return
            inv_name = inviter.first_name or "User"
            users    = getattr(vc_inv, "users", []) or []
            for u in users:
                if not u: continue
                text = (
                    f"<a href='tg://user?id={inviter.id}'>{inv_name}</a> "
                    f"ɴᴇ ɪɴᴠɪᴛᴇ ᴋɪʏᴀ: "
                    f"<a href='tg://user?id={u.id}'>{u.first_name or 'User'}</a> "
                    f"ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴘᴇ 🎙️"
                )
                n = await client.send_message(msg.chat.id, text)
                await asyncio.sleep(30)
                try: await n.delete()
                except: pass
            return

        # VC started
        if getattr(msg, "video_chat_started", None):
            user = msg.from_user
            if user and not user.is_bot:
                text = (
                    f"🎙️ <a href='tg://user?id={user.id}'>{user.first_name or 'User'}</a> "
                    f"<b>ᴠᴄ ᴘᴇ ᴊᴏɪɴ ʜᴏ ɢᴀʏᴀ!</b>"
                )
                n = await client.send_message(msg.chat.id, text)
                await asyncio.sleep(20)
                try: await n.delete()
                except: pass

    except Exception as e:
        print(f"[VC ERROR] {e}")
