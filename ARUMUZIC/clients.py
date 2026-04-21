from pyrogram import Client
from pytgcalls import PyTgCalls
import os
import config
import settings as S

def _get_session():
    # Settings se pehle check karo, phir env var, phir config
    saved = S.get(config.BOT_TOKEN, "session_string")
    if saved:
        return saved
    return os.environ.get("SESSION_STRING", config.SESSION_STRING)

_token_suffix     = config.BOT_TOKEN.replace(":", "_")[-12:]
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

# Assistant Client
assistant = Client(
    _ass_session_name,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=_get_session()
)

# Music Engine
call = PyTgCalls(assistant)


async def reload_assistant(new_session: str):
    """
    /setstring ke baad bina restart ke nayi session string apply karo.
    """
    global assistant, call

    # Purana assistant aur call band karo
    try:
        await call.stop()
    except Exception:
        pass
    try:
        await assistant.stop()
    except Exception:
        pass

    # Nayi objects banao
    assistant = Client(
        _ass_session_name,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=new_session
    )
    call = PyTgCalls(assistant)

    # Start karo
    await assistant.start()
    await call.start()

    # play.py bhi call use karta hai — uska reference update karo
    try:
        import ARUMUZIC.plugins.play as play_module
        play_module.call = call
        play_module.assistant = assistant
    except Exception:
        pass
