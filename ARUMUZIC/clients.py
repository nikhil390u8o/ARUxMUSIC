from pyrogram import Client
from pytgcalls import PyTgCalls
import os
import config

# SESSION_STRING: env var se override hoga jab /setstring use hoga
_session = os.environ.get("SESSION_STRING", config.SESSION_STRING)

# Bot Client
bot = Client(
    "ARUMUSIC_BOT",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="ARUMUZIC.plugins")
)

# Assistant Client — SESSION_STRING dynamic hai
assistant = Client(
    "ARUMUSIC_ASS",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=_session
)

# Music Engine
call = PyTgCalls(assistant)
