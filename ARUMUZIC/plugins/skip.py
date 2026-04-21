"""
/skip - Skip current song and play next from queue.
Works in both main bot and cloned bots.
Only group admins / bot owner can use it.
"""

import asyncio
import ARUMUZIC.clients as _clients
from pyrogram import filters, enums
from pyrogram.types import Message
from ARUMUZIC.clients import bot
import config

def get_call():
    return _clients.call


async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.name in ("OWNER", "ADMINISTRATOR")
    except Exception:
        return False


@bot.on_message(filters.command("skip") & filters.group)
async def skip_cmd(client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    # Sirf admin ya bot owner skip kar sakta hai
    if not (user_id == config.CLONE_OWNER_ID or await _is_admin(client, chat_id, user_id)):
        return await msg.reply_text("❌ <b>Sirf group admins /skip use kar sakte hain!</b>")

    try:
        await msg.delete()
    except:
        pass

    # Queue check
    if chat_id not in config.queues or not config.queues[chat_id]:
        return await msg.reply_text("❌ <b>Koi song queue mein nahi hai!</b>")

    from ARUMUZIC.plugins.play import play_next

    if len(config.queues[chat_id]) > 1:
        # Next song play karo
        m = await msg.reply_text("⏭ <b>Skipping...</b>")
        try:
            await play_next(chat_id)
            await m.edit_text("⏭ <b>Next song play ho raha hai!</b>")
        except Exception as e:
            await m.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")
    else:
        # Queue mein sirf ek hi song hai — VC leave karo
        m = await msg.reply_text("⏹ <b>Queue empty! Leaving VC...</b>")
        try:
            await get_call().leave_group_call(chat_id)
            config.queues.pop(chat_id, None)
            config.current_playing.pop(chat_id, None)
            await m.edit_text("⏹ <b>Queue khatam! VC chhod diya.</b>")
        except Exception as e:
            await m.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")
