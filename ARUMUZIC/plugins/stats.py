import psutil
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from ARUMUZIC.clients import bot
import config
import settings as S


def _is_owner(uid): return uid == config.CLONE_OWNER_ID
def _is_main(uid):  return uid == config.OWNER_ID


@bot.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client, msg: Message):
    uid = msg.from_user.id
    if not (_is_owner(uid) or _is_main(uid)):
        return await msg.reply_text("❌ <b>Sirf owner ye command use kar sakta hai!</b>")

    m = await msg.reply_text("📊 <b>Fetching stats...</b>")

    up  = datetime.now() - config.BOT_START_TIME
    h, r = divmod(int(up.total_seconds()), 3600)
    mn, s = divmod(r, 60)
    uptime = f"{h}h {mn}m {s}s"
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    if _is_main(uid) and not config.IS_CLONE:
        clones   = S.get_all_clones()
        u_total  = len(S.get_all_users_all_bots())
        g_total  = len(S.get_all_groups_all_bots())
        u_main   = len(S.get_users(config.BOT_TOKEN))
        g_main   = len(S.get_groups(config.BOT_TOKEN))

        text = (
            "📊 <b>MAIN BOT — FULL STATS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Total Clones:</b> <code>{len(clones)}</code>\n"
            f"👥 <b>Total Users (all bots):</b> <code>{u_total}</code>\n"
            f"🏠 <b>Total Groups (all bots):</b> <code>{g_total}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>Main Bot Users:</b> <code>{u_main}</code>\n"
            f"🏠 <b>Main Bot Groups:</b> <code>{g_main}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💻 <b>CPU:</b> <code>{cpu}%</code> | 📊 <b>RAM:</b> <code>{ram}%</code>\n"
            f"🆙 <b>Uptime:</b> <code>{uptime}</code>"
        )
        if clones:
            text += "\n\n━━━━━━━━━━━━━━━━━━━━\n<b>📋 Clone Breakdown:</b>"
            for i, c in enumerate(clones, 1):
                cu = len(S.get_users(c.get("token", "")))
                cg = len(S.get_groups(c.get("token", "")))
                text += (
                    f"\n<b>{i}.</b> @{c.get('bot_username','?')} "
                    f"<i>(by @{c.get('owner_username','?')})</i>\n"
                    f"    👥 <code>{cu}</code> users | 🏠 <code>{cg}</code> groups"
                )
    else:
        u_my = len(S.get_users(config.BOT_TOKEN))
        g_my = len(S.get_groups(config.BOT_TOKEN))
        sub  = S.get_clones_by_owner(config.CLONE_OWNER_ID)
        own  = S.get(config.BOT_TOKEN, "owner_username") or config.CLONE_OWNER_USERNAME or "N/A"

        text = (
            "📊 <b>BOT STATS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> @{own}\n"
            f"👥 <b>Users:</b> <code>{u_my}</code>\n"
            f"🏠 <b>Groups:</b> <code>{g_my}</code>\n"
            f"🔁 <b>Sub-Clones:</b> <code>{len(sub)}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💻 <b>CPU:</b> <code>{cpu}%</code> | 📊 <b>RAM:</b> <code>{ram}%</code>\n"
            f"🆙 <b>Uptime:</b> <code>{uptime}</code>"
        )

    await m.edit_text(text)
