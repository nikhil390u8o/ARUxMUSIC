"""
Admin commands:
  /clone <bot_token>       - Clone this bot. Cloner becomes owner.
  /rmclone <bot_token>     - Kill + remove a clone (main owner only).
  /cloned                  - Kitne bots clone kiye tune.
  /setstring <session>     - Apne clone me khud ka assistant set karo.
  /setsupport <link>       - Support channel link set karo.
  /setstrtimg <img_url>    - Start image set karo.
  /setpingimg <img_url>    - Ping image set karo.
"""

import os
import sys
import signal
import subprocess

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import AccessTokenInvalid, AccessTokenExpired

from ARUMUZIC.clients import bot
import config
import settings as S

def _is_owner(user_id):
    return user_id == config.CLONE_OWNER_ID

def _is_main_owner(user_id):
    return user_id == config.OWNER_ID

# /setsupport
@bot.on_message(filters.command("setsupport") & filters.private)
async def set_support(client, msg: Message):
    if not _is_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf owner ye command use kar sakta hai!</b>")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply_text("⚠️ <b>Usage:</b> <code>/setsupport https://t.me/yourchannel</code>")
    link = parts[1].strip()
    S.set(config.BOT_TOKEN, "support_link", link)
    await msg.reply_text(f"✅ <b>Support link set!</b>\n🔗 <code>{link}</code>\n\nAb /start aur /ping me yahi dikhega.")

# /setstrtimg
@bot.on_message(filters.command("setstrtimg") & filters.private)
async def set_start_img(client, msg: Message):
    if not _is_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf owner ye command use kar sakta hai!</b>")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply_text("⚠️ <b>Usage:</b> <code>/setstrtimg https://files.catbox.moe/xxxx.jpg</code>")
    url = parts[1].strip()
    S.set(config.BOT_TOKEN, "start_img", url)
    await msg.reply_photo(photo=url, caption="✅ <b>Start image set! Ab /start pe yahi photo dikhegi.</b>")

# /setpingimg
@bot.on_message(filters.command("setpingimg") & filters.private)
async def set_ping_img(client, msg: Message):
    if not _is_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf owner ye command use kar sakta hai!</b>")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply_text("⚠️ <b>Usage:</b> <code>/setpingimg https://files.catbox.moe/xxxx.jpg</code>")
    url = parts[1].strip()
    S.set(config.BOT_TOKEN, "ping_img", url)
    await msg.reply_photo(photo=url, caption="✅ <b>Ping image set! Ab /ping pe yahi photo dikhegi.</b>")

# /setstring
@bot.on_message(filters.command("setstring") & filters.private)
async def set_string(client, msg: Message):
    if not _is_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf is bot ka owner ye command use kar sakta hai!</b>")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply_text(
            "⚠️ <b>Usage:</b> <code>/setstring YOUR_SESSION_STRING</code>\n\n"
            "📌 <b>Session string kaise banayein?</b>\n"
            "• <a href='https://replit.com/@SpEcHiDe/GenStringV2'>Replit generator</a> use karo\n\n"
            "⚠️ <i>String save hone ke baad bot restart karo taki apply ho.</i>"
        )
    session = parts[1].strip()
    S.set(config.BOT_TOKEN, "session_string", session)
    await msg.reply_text(
        "✅ <b>Session string save ho gaya!</b>\n\n"
        "🔄 <b>Ab bot ko restart karo</b> taki nayi string apply ho.\n"
        "⚠️ <i>Ye string kisi ko mat dikhana — ye tera account hai!</i>"
    )

# /clone
@bot.on_message(filters.command("clone") & filters.private)
async def clone_bot(client, msg: Message):
    if not _is_main_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf main bot ka owner /clone kar sakta hai!</b>")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply_text(
            "⚠️ <b>Usage:</b> <code>/clone 123456:ABCDefgh...</code>\n\n"
            "Apna bot token BotFather se lo aur yahan paste karo."
        )
    new_token = parts[1].strip()
    m = await msg.reply_text("🔍 <b>Token validate ho raha hai...</b>")

    try:
        from pyrogram import Client as TempClient
        tmp = TempClient(
            f"clone_chk_{new_token[:8]}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=new_token,
            in_memory=True,
        )
        await tmp.start()
        new_bot_info = await tmp.get_me()
        await tmp.stop()
    except (AccessTokenInvalid, AccessTokenExpired):
        return await m.edit_text("❌ <b>Invalid bot token! BotFather se check karo.</b>")
    except Exception as e:
        return await m.edit_text(f"❌ <b>Token check fail:</b> <code>{e}</code>")

    await m.edit_text(
        f"✅ <b>Token valid!</b>\n"
        f"🤖 <b>{new_bot_info.first_name}</b> (@{new_bot_info.username})\n\n"
        f"⚙️ Clone spawn ho raha hai..."
    )

    cloner      = msg.from_user
    cloner_id   = cloner.id
    cloner_name = cloner.username or cloner.first_name or str(cloner_id)

    # Agar pehle /setstring se session save kiya ho clone ke liye
    saved_session = S.get(new_token, "session_string") or config.SESSION_STRING

    env = os.environ.copy()
    env["BOT_TOKEN"]            = new_token
    env["CLONE_OWNER_ID"]       = str(cloner_id)
    env["CLONE_OWNER_USERNAME"] = cloner_name
    env["SESSION_STRING"]       = saved_session

    main_py = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "main.py"
    )

    try:
        proc = subprocess.Popen(
            [sys.executable, main_py],
            env=env,
            cwd=os.path.dirname(main_py),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        pid = proc.pid
    except Exception as e:
        return await m.edit_text(f"❌ <b>Clone spawn fail:</b> <code>{e}</code>")

    S.init_clone(
        token=new_token,
        owner_id=cloner_id,
        owner_username=cloner_name,
        bot_username=new_bot_info.username or "",
        pid=pid,
    )

    await m.edit_text(
        f"🎉 <b>Clone successfully deploy ho gaya!</b>\n\n"
        f"🤖 <b>Bot:</b> @{new_bot_info.username}\n"
        f"👑 <b>Owner:</b> @{cloner_name}\n"
        f"🆔 <b>PID:</b> <code>{pid}</code>\n\n"
        f"ℹ️ <b>Clone bot ke DM mein jaake customize karo:</b>\n"
        f"• <code>/setstring</code> — apna assistant add karo\n"
        f"• <code>/setsupport</code> — support link\n"
        f"• <code>/setstrtimg</code> — start image\n"
        f"• <code>/setpingimg</code> — ping image\n\n"
        f"⚠️ <i>Server restart pe clone manually restart karna padega.</i>"
    )

# /rmclone
@bot.on_message(filters.command("rmclone") & filters.private)
async def rm_clone(client, msg: Message):
    if not _is_main_owner(msg.from_user.id):
        return await msg.reply_text("❌ <b>Sirf main bot ka owner ye command use kar sakta hai!</b>")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return await msg.reply_text(
            "⚠️ <b>Usage:</b> <code>/rmclone BOT_TOKEN</code>\n\n"
            "💡 Tip: <code>/cloned</code> se sab tokens dekho."
        )
    token = parts[1].strip()
    cfg   = S.get_all(token)
    if not cfg.get("is_clone"):
        return await msg.reply_text("❌ <b>Ye token kisi registered clone ka nahi hai!</b>")

    pid          = cfg.get("pid", 0)
    bot_username = cfg.get("bot_username", "unknown")
    owner_name   = cfg.get("owner_username", "unknown")

    killed = False
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            killed = True
        except ProcessLookupError:
            pass
        except Exception as e:
            await msg.reply_text(f"⚠️ PID kill error: <code>{e}</code>")

    S.remove_clone(token)

    await msg.reply_text(
        f"🗑️ <b>Clone removed!</b>\n\n"
        f"🤖 <b>Bot:</b> @{bot_username}\n"
        f"👑 <b>Owner:</b> @{owner_name}\n"
        f"💀 <b>Process:</b> {'Killed (PID ' + str(pid) + ')' if killed else 'Already stopped / No PID'}"
    )

# /cloned
@bot.on_message(filters.command("cloned") & filters.private)
async def cloned_list(client, msg: Message):
    user_id = msg.from_user.id

    if _is_main_owner(user_id):
        clones = S.get_all_clones()
        header = "👑 <b>All Clones (Main Owner View)</b>"
    else:
        clones = S.get_clones_by_owner(user_id)
        header = "🤖 <b>Tumhare Cloned Bots</b>"

    if not clones:
        return await msg.reply_text(
            f"{header}\n\n"
            "📭 <b>Koi clone nahi hai abhi.</b>\n"
            "Use <code>/clone BOT_TOKEN</code> to create one."
        )

    lines = [f"{header}\n<b>Total: {len(clones)}</b>\n"]
    for i, c in enumerate(clones, 1):
        uname   = c.get("bot_username", "unknown")
        owner   = c.get("owner_username", "unknown")
        pid     = c.get("pid", 0)
        token   = c.get("token", "")
        short_t = token[:12] + "..." if token else "N/A"

        alive = "⚪ No PID"
        if pid:
            try:
                os.kill(pid, 0)
                alive = "🟢 Running"
            except ProcessLookupError:
                alive = "🔴 Stopped"
            except Exception:
                alive = "🟡 Unknown"

        lines.append(
            f"<b>{i}.</b> @{uname}\n"
            f"   👤 Owner: @{owner}\n"
            f"   🆔 PID: <code>{pid}</code> | {alive}\n"
            f"   🔑 Token: <code>{short_t}</code>"
        )

    await msg.reply_text("\n\n".join(lines))
