"""
/tagall {message} - Tag all group members with a message.
Works in both main bot and cloned bots.
Only group admins / owner can use it.
"""

import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChatAdminRequired, UserNotParticipant
from ARUMUZIC.clients import bot
import config


def _is_owner(user_id: int) -> bool:
    return user_id == config.CLONE_OWNER_ID


async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ("OWNER", "ADMINISTRATOR")
    except Exception:
        return False


@bot.on_message(filters.command("tagall") & filters.group)
async def tagall(client, msg: Message):
    user_id = msg.from_user.id

    # Sirf admin ya owner use kar sakta hai
    if not (_is_owner(user_id) or await _is_admin(client, msg.chat.id, user_id)):
        return await msg.reply_text("❌ <b>Sirf group admins /tagall use kar sakte hain!</b>")

    # Custom message
    parts = msg.text.split(maxsplit=1)
    custom_msg = parts[1].strip() if len(parts) > 1 else "📢 <b>Everyone!</b>"

    # Members fetch karo
    status_msg = await msg.reply_text("⏳ <b>Members fetch ho rahe hain...</b>")

    members = []
    try:
        async for member in client.get_chat_members(msg.chat.id):
            # Bots aur deleted accounts skip
            if member.user.is_bot or member.user.is_deleted:
                continue
            members.append(member.user)
    except ChatAdminRequired:
        return await status_msg.edit_text(
            "❌ <b>Bot ko admin banana padega members fetch karne ke liye!</b>"
        )
    except Exception as e:
        return await status_msg.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")

    if not members:
        return await status_msg.edit_text("❌ <b>Koi member nahi mila!</b>")

    await status_msg.edit_text(
        f"📢 <b>Tagging {len(members)} members...</b>"
    )

    # 5-5 ke chunks mein tag karo (flood se bachne ke liye)
    CHUNK = 5
    for i in range(0, len(members), CHUNK):
        chunk = members[i:i + CHUNK]
        tags  = " ".join(
            f"<a href='tg://user?id={u.id}'>{u.first_name}</a>"
            for u in chunk
        )

        # First chunk ke saath message, baaki ke saath sirf tags
        if i == 0:
            text = f"{custom_msg}\n\n{tags}"
        else:
            text = tags

        try:
            await client.send_message(msg.chat.id, text)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
            await client.send_message(msg.chat.id, text)
        except Exception:
            pass

        await asyncio.sleep(0.8)  # Rate limit se bachne ke liye

    await status_msg.edit_text(
        f"✅ <b>Done! {len(members)} members tag ho gaye.</b>"
    )
