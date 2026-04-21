import asyncio
from pyrogram import filters, enums
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChatAdminRequired, PeerIdInvalid
from ARUMUZIC.clients import bot
import config


async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR
        )
    except Exception:
        return False


@bot.on_message(filters.command("tagall") & filters.group)
async def tagall(client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    # Admin check
    is_admin = await _is_admin(client, chat_id, user_id)
    is_owner = (user_id == config.CLONE_OWNER_ID)

    if not (is_admin or is_owner):
        return await msg.reply_text("❌ <b>Sirf group admins /tagall use kar sakte hain!</b>")

    parts = msg.text.split(maxsplit=1)
    custom_msg = parts[1].strip() if len(parts) > 1 else "📢 <b>Everyone!</b>"

    status_msg = await msg.reply_text("⏳ <b>Members fetch ho rahe hain...</b>")

    members = []
    try:
        async for member in client.get_chat_members(chat_id):
            try:
                user = member.user
                if user is None:
                    continue
                if user.is_bot:
                    continue
                if user.is_deleted:
                    continue
                members.append(user)
            except Exception:
                continue
    except ChatAdminRequired:
        return await status_msg.edit_text(
            "❌ <b>Bot ko group admin banana padega!</b>\n"
            "Members fetch karne ke liye admin rights chahiye."
        )
    except Exception as e:
        return await status_msg.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")

    if not members:
        return await status_msg.edit_text("❌ <b>Koi member nahi mila!</b>")

    total = len(members)
    await status_msg.edit_text(f"📢 <b>Tagging {total} members...</b>")

    try:
        await msg.delete()
    except:
        pass

    CHUNK = 5
    for i in range(0, total, CHUNK):
        chunk = members[i:i + CHUNK]

        tags = " ".join(
            f"<a href='tg://user?id={u.id}'>{u.first_name or 'User'}</a>"
            for u in chunk
        )

        text = f"{custom_msg}\n\n{tags}" if i == 0 else tags

        try:
            await client.send_message(chat_id, text)
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)
            try:
                await client.send_message(chat_id, text)
            except:
                pass
        except Exception:
            pass

        await asyncio.sleep(1)

    await status_msg.edit_text(f"✅ <b>Done! {total} members tag ho gaye.</b>")
