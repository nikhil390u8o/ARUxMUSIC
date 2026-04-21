import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatWriteForbidden
from ARUMUZIC.clients import bot
import config
import settings as S

_pending: dict = {}

def _is_owner(uid): return uid == config.CLONE_OWNER_ID


@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_start(client, msg: Message):
    if not _is_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf owner use kar sakta hai!</b>")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👥 Users", callback_data="bc_users"),
            InlineKeyboardButton("🏠 Groups", callback_data="bc_groups"),
        ],
        [InlineKeyboardButton("📢 Both", callback_data="bc_both")],
        [InlineKeyboardButton("❌ Cancel", callback_data="bc_cancel")]
    ])
    await msg.reply_text(
        "📢 <b>Broadcast</b>\n\nKahan bhejna hai?",
        reply_markup=buttons
    )


@bot.on_callback_query(filters.regex("^bc_"))
async def broadcast_cb(client, query):
    if not _is_owner(query.from_user.id):
        return await query.answer("❌ Sirf owner!", show_alert=True)

    if query.data == "bc_cancel":
        _pending.pop(query.from_user.id, None)
        return await query.message.edit_text("❌ <b>Cancelled.</b>")

    target = {"bc_users": "users", "bc_groups": "groups", "bc_both": "both"}.get(query.data, "both")
    _pending[query.from_user.id] = target

    await query.message.edit_text(
        f"✅ <b>Target: {target}</b>\n\n"
        "Ab jo message broadcast karna hai wo <b>bhejo</b>.\n"
        "<i>(Text, Photo, Video, Audio, Document — sab supported)</i>"
    )


@bot.on_message(filters.private & ~filters.command([
    "start","ping","broadcast","clone","rmclone","cloned",
    "setstring","setusername","setsupport","setstrtimg","setpingimg","stats","skip"
]))
async def receive_bc(client, msg: Message):
    uid = msg.from_user.id
    if uid not in _pending:
        return

    target = _pending.pop(uid)
    users  = S.get_users(config.BOT_TOKEN)  if target in ("users",  "both") else []
    groups = S.get_groups(config.BOT_TOKEN) if target in ("groups", "both") else []
    targets = [(i, "u") for i in users] + [(i, "g") for i in groups]

    if not targets:
        return await msg.reply_text(
            "❌ <b>Database empty hai!</b>\n\n"
            "Koi user abhi tak /start nahi kiya ya koi group nahi add kiya.\n"
            "Users /start karenge toh automatically track honge."
        )

    status = await msg.reply_text(f"📢 <b>Broadcasting to {len(targets)}...</b>")
    ok = fail = 0

    for chat_id, _ in targets:
        try:
            await _send(client, msg, chat_id)
            ok += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)
            try:
                await _send(client, msg, chat_id)
                ok += 1
            except:
                fail += 1
        except (UserIsBlocked, InputUserDeactivated, ChatWriteForbidden):
            fail += 1
        except:
            fail += 1
        await asyncio.sleep(0.3)

    await status.edit_text(
        f"✅ <b>Broadcast Done!</b>\n\n"
        f"✅ Success: <code>{ok}</code>\n"
        f"❌ Failed: <code>{fail}</code>"
    )


async def _send(client, msg: Message, chat_id: int):
    cap = msg.caption.html if msg.caption else None
    if msg.text:
        await client.send_message(chat_id, msg.text.html)
    elif msg.photo:
        await client.send_photo(chat_id, msg.photo.file_id, caption=cap)
    elif msg.video:
        await client.send_video(chat_id, msg.video.file_id, caption=cap)
    elif msg.audio:
        await client.send_audio(chat_id, msg.audio.file_id, caption=cap)
    elif msg.document:
        await client.send_document(chat_id, msg.document.file_id, caption=cap)
    elif msg.voice:
        await client.send_voice(chat_id, msg.voice.file_id, caption=cap)
    elif msg.sticker:
        await client.send_sticker(chat_id, msg.sticker.file_id)
    else:
        await msg.forward(chat_id)
