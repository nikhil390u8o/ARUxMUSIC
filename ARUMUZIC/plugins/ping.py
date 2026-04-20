import time
import psutil
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ARUMUZIC.clients import bot
import config
import settings as S

START_TIME = datetime.now()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time


@bot.on_message(filters.command("ping") & ~filters.bot)
async def ping_cmd(client, message: Message):
    try:
        await message.delete()
    except:
        pass

    start_time = time.time()
    m = await message.reply_text("<code>ᴘɪɴɢɪɴɢ..</code>")

    end_time  = time.time()
    ping_ms   = round((end_time - start_time) * 1000, 2)

    bot_uptime = getattr(config, "BOT_START_TIME", START_TIME)
    uptime     = get_readable_time(int((datetime.now() - bot_uptime).total_seconds()))

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    # ── Dynamic settings ────────────────────────────────────────────────────
    PING_IMG     = S.get(config.BOT_TOKEN, "ping_img")
    support_link = S.get(config.BOT_TOKEN, "support_link")
    owner_name   = S.get(config.BOT_TOKEN, "owner_username") or config.CLONE_OWNER_USERNAME or "sxyaru"

    text = (
        "<b>🏓 ᴘᴏɴɢ! sᴛᴀᴛs ᴀʀᴇ ʜᴇʀᴇ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 <b>ʟᴀᴛᴇɴᴄʏ:</b> <code>{ping_ms} ms</code>\n"
        f"🆙 <b>ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>\n"
        f"💻 <b>ᴄᴘᴜ:</b> <code>{cpu}%</code>\n"
        f"📊 <b>ʀᴀᴍ:</b> <code>{ram}%</code>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ᴏᴡɴᴇʀ:</b> <a href='https://t.me/{owner_name}'>ᴀʀᴜ × ᴀᴘɪ [ʙᴏᴛs]</a>"
    )

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=support_link),
        InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/ll_PANDA_BBY_ll")
    ]])

    try:
        await client.send_photo(
            message.chat.id,
            photo=PING_IMG,
            caption=text,
            reply_markup=buttons
        )
        await m.delete()
    except Exception as e:
        print(f"Ping Photo Error: {e}")
        await m.edit(text, reply_markup=buttons)
