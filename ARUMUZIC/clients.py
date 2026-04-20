from pyrogram import Client
from pytgcalls import PyTgCalls
import os
import config

# SESSION_STRING: env var se override hoga jab /setstring use hoga
_session = os.environ.get("SESSION_STRING", config.SESSION_STRING)

# Unique session name — token ke last 12 chars use karo taaki clash na ho
_token_suffix = config.BOT_TOKEN.replace(":", "_")[-12:]
_bot_session_name = f"ARUMUSIC_BOT_{_token_suffix}"
_ass_session_name = f"ARUMUSIC_ASS_{_token_suffix}"

# Bot Client
bot = Client(
    _bot_session_name,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="ARUMUZIC.plugins")
)

# Assistant Client — SESSION_STRING dynamic hai
assistant = Client(
    _ass_session_name,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=_session
)

# Music Engine
call = PyTgCalls(assistant)
