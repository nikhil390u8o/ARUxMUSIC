"""
/stats - Show bot statistics.
Main bot: shows all bots' combined stats.
Clone bot: shows only that clone's stats + its own clones.
"""

import psutil
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from ARUMUZIC.clients import bot
import config
import settings as S
import database as DB


def _is_owner(user_id: int) -> bool:
    return user_id == config.CLONE_OWNER_ID

def _is_main_owner(user_id: int) -> bool:
    return user_id == config.OWNER_ID


@bot.on_message(filters.command("stats") & filters.private)
async def stats_cmd(client, msg: Message):
    user_id = msg.from_user.id

    if not (_is_owner(user_id) or _is_main_owner(user_id)):
        return await msg.reply_text("❌ <b>Sirf owner ye command use kar sakta hai!</b>")

    m = await msg.reply_text("📊 <b>Stats fetch ho rahi hain...</b>")

    uptime = datetime.now() - config.BOT_START_TIME
    h, rem  = divmod(int(uptime.total_seconds()), 3600)
    mn, s   = divmod(rem, 60)
    uptime_str = f"{h}h {mn}m {s}s"

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    if _is_main_owner(user_id) and not config.IS_CLONE:
        # ── MAIN BOT VIEW ────────────────────────────────────────────────────
        all_clones   = S.get_all_clones()
        total_clones = len(all_clones)
        total_users  = len(DB.get_all_users_all_bots())
        total_groups = len(DB.get_all_groups_all_bots())

        # Main bot ka apna stats
        main_users  = len(DB.get_users(config.BOT_TOKEN))
        main_groups = len(DB.get_groups(config.BOT_TOKEN))

        # Clone breakdown
        clone_lines = ""
        for i, c in enumerate(all_clones, 1):
            uname  = c.get("bot_username", "unknown")
            owner  = c.get("owner_username", "unknown")
            cusers = len(DB.get_users(c.get("token", "")))
            cgrps  = len(DB.get_groups(c.get("token", "")))

            # Check if clone also has sub-clones
            sub = S.get_clones_by_owner(c.get("owner_id", 0))
            sub_txt = f" | 🔁 Sub-clones: {len(sub)}" if sub else ""

            clone_lines += (
                f"\n<b>{i}.</b> @{uname} <i>(by @{owner})</i>\n"
                f"    👥 Users: <code>{cusers}</code> | 🏠 Groups: <code>{cgrps}</code>{sub_txt}"
            )

        text = (
            "📊 <b>MAIN BOT — FULL STATS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <b>Total Clones:</b> <code>{total_clones}</code>\n"
            f"👥 <b>Total Users (all bots):</b> <code>{total_users}</code>\n"
            f"🏠 <b>Total Groups (all bots):</b> <code>{total_groups}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏠 <b>Main Bot Users:</b> <code>{main_users}</code>\n"
            f"🏠 <b>Main Bot Groups:</b> <code>{main_groups}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💻 <b>CPU:</b> <code>{cpu}%</code> | 📊 <b>RAM:</b> <code>{ram}%</code>\n"
            f"🆙 <b>Uptime:</b> <code>{uptime_str}</code>\n"
        )

        if clone_lines:
            text += f"\n━━━━━━━━━━━━━━━━━━━━\n<b>📋 Clone Breakdown:</b>{clone_lines}"

    else:
        # ── CLONE BOT VIEW ───────────────────────────────────────────────────
        my_users  = len(DB.get_users(config.BOT_TOKEN))
        my_groups = len(DB.get_groups(config.BOT_TOKEN))

        # Is clone ke owner ne aur clone kiye hain?
        sub_clones = S.get_clones_by_owner(config.CLONE_OWNER_ID)
        sub_total  = len(sub_clones)

        owner_name = S.get(config.BOT_TOKEN, "owner_username") or config.CLONE_OWNER_USERNAME or "N/A"

        text = (
            "📊 <b>BOT STATS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>Owner:</b> @{owner_name}\n"
            f"👥 <b>Users:</b> <code>{my_users}</code>\n"
            f"🏠 <b>Groups:</b> <code>{my_groups}</code>\n"
            f"🔁 <b>Sub-Clones Made:</b> <code>{sub_total}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"💻 <b>CPU:</b> <code>{cpu}%</code> | 📊 <b>RAM:</b> <code>{ram}%</code>\n"
            f"🆙 <b>Uptime:</b> <code>{uptime_str}</code>"
        )

    await m.edit_text(text)
