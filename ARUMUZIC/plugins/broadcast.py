"""
/broadcast - Broadcast any message (text/photo/video/audio/document) to users or groups.
Only bot owner can use this.
Works in both private and groups (via reply).
Main bot: can broadcast across all its users/groups.
Clone bot: broadcasts to its own users/groups.
"""

import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatWriteForbidden
from ARUMUZIC.clients import bot
import config
import database as DB


def _is_owner(user_id: int) -> bool:
    return user_id == config.CLONE_OWNER_ID


# ─── Step 1: /broadcast — choose target ──────────────────────────────────────

@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(client, msg: Message):
    if not _is_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf owner ye command use kar sakta hai!</b>")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Users", callback_data="bc_users"),
            InlineKeyboardButton("🏠 Groups", callback_data="bc_groups"),
        ],
        [
            InlineKeyboardButton("📢 Both (Users + Groups)", callback_data="bc_both"),
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data="bc_cancel")
        ]
    ])

    await msg.reply_text(
        "📢 <b>Broadcast Setup</b>\n\n"
        "Pehle message reply karo jise broadcast karna hai,\n"
        "ya is command ke baad seedha message bhejo.\n\n"
        "<b>Kahan broadcast karna hai?</b>",
        reply_markup=buttons
    )


# ─── Step 2: Callback — target select ────────────────────────────────────────

@bot.on_callback_query(filters.regex("^bc_"))
async def broadcast_cb(client, query):
    if not _is_owner(query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)

    data = query.data

    if data == "bc_cancel":
        await query.message.edit_text("❌ <b>Broadcast cancelled.</b>")
        return

    target_map = {
        "bc_users":  "users",
        "bc_groups": "groups",
        "bc_both":   "both",
    }
    target = target_map.get(data, "both")

    await query.message.edit_text(
        f"✅ <b>Target set: <code>{target}</code></b>\n\n"
        f"Ab jo message broadcast karna hai wo <b>reply karke bhejo</b>.\n"
        f"(Text, Photo, Video, Audio, Document — sab supported hai)\n\n"
        f"<i>Next message tumhara broadcast message maana jaayega.</i>",
    )

    # Store target in a simple dict keyed by user_id
    _pending_broadcast[query.from_user.id] = target


# ─── Pending broadcasts store ─────────────────────────────────────────────────
_pending_broadcast: dict = {}


# ─── Step 3: Receive broadcast message ───────────────────────────────────────

@bot.on_message(filters.private & ~filters.command([
    "start", "ping", "broadcast", "clone", "rmclone", "cloned",
    "setstring", "setusername", "setsupport", "setstrtimg", "setpingimg", "stats"
]))
async def receive_broadcast_msg(client, msg: Message):
    user_id = msg.from_user.id
    if user_id not in _pending_broadcast:
        return

    target = _pending_broadcast.pop(user_id)

    users  = DB.get_users(config.BOT_TOKEN)  if target in ("users",  "both") else []
    groups = DB.get_groups(config.BOT_TOKEN) if target in ("groups", "both") else []

    all_targets = [(uid, "user") for uid in users] + [(gid, "group") for gid in groups]
    total = len(all_targets)

    if total == 0:
        return await msg.reply_text("❌ <b>Koi user/group nahi mila database mein!</b>")

    status = await msg.reply_text(
        f"📢 <b>Broadcast shuru ho raha hai...</b>\n"
        f"📨 <b>Total targets:</b> <code>{total}</code>"
    )

    success = 0
    failed  = 0

    for chat_id, kind in all_targets:
        try:
            await _forward_message(client, msg, chat_id)
            success += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)
            try:
                await _forward_message(client, msg, chat_id)
                success += 1
            except Exception:
                failed += 1
        except (UserIsBlocked, InputUserDeactivated, ChatWriteForbidden):
            failed += 1
        except Exception:
            failed += 1

        await asyncio.sleep(0.3)

    await status.edit_text(
        f"✅ <b>Broadcast complete!</b>\n\n"
        f"📨 <b>Total:</b> <code>{total}</code>\n"
        f"✅ <b>Success:</b> <code>{success}</code>\n"
        f"❌ <b>Failed:</b> <code>{failed}</code>"
    )


async def _forward_message(client, msg: Message, chat_id: int):
    """Forward any type of message to a chat."""
    if msg.text:
        await client.send_message(chat_id, msg.text.html)
    elif msg.photo:
        await client.send_photo(
            chat_id,
            msg.photo.file_id,
            caption=msg.caption.html if msg.caption else None
        )
    elif msg.video:
        await client.send_video(
            chat_id,
            msg.video.file_id,
            caption=msg.caption.html if msg.caption else None
        )
    elif msg.audio:
        await client.send_audio(
            chat_id,
            msg.audio.file_id,
            caption=msg.caption.html if msg.caption else None
        )
    elif msg.document:
        await client.send_document(
            chat_id,
            msg.document.file_id,
            caption=msg.caption.html if msg.caption else None
        )
    elif msg.voice:
        await client.send_voice(
            chat_id,
            msg.voice.file_id,
            caption=msg.caption.html if msg.caption else None
        )
    elif msg.sticker:
        await client.send_sticker(chat_id, msg.sticker.file_id)
    elif msg.animation:
        await client.send_animation(
            chat_id,
            msg.animation.file_id,
            caption=msg.caption.html if msg.caption else None
        )
    else:
        await msg.forward(chat_id)
