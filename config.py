import os
from datetime import datetime

# --- Bot Credentials ---
API_ID   = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"

# BOT_TOKEN: env var se override hota hai jab /clone se spawn hota hai
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8596765113:AAHBcxK0z-n53S0tCRT0oAZQqec8o6cgbO4")

SESSION_STRING = "BQE-4i0AjY51k6Ute-R_moYODSyHLtkPT4i7dvLpvc_NGe5IselUcgz8oodFp2l2i1uocClQAMhiiCt5NGy8TJn9wUdSOlnp-30vebyM1RMl6lz9S1hsNtq09FJkznWG-QF6XRy4asg8_yQKeBGrSSqALOCkXuQHTInCC2O7sFaCnRw09iMe7Uu3-BjnqHLaRYKgvHxItYClNsyFEUPJHuWxRGtdLJOSYLXfyMoOi-5DowVwke3rC1vEQggQ4IxlP6lRNOshB9lnhUQGfnlw4FWVGplqYRZCD9Cq-dggGf-OkjB_p87jxL-eHwd-s1xRBz2SQQ6VZGCKqVhoSHUdc87ebLLfiAAAAAHKarFXAA"

# Main bot ka owner
OWNER_ID = 8566803656

# Clone mode: /clone se spawn hone par ye env vars set hote hain
CLONE_OWNER_ID       = int(os.environ.get("CLONE_OWNER_ID", OWNER_ID))
CLONE_OWNER_USERNAME = os.environ.get("CLONE_OWNER_USERNAME", "")
IS_CLONE             = bool(os.environ.get("CLONE_OWNER_ID"))

# JioSaavn API
API_KEY = "pePKYb9ltY"
API_URL = "http://api.nubcoder.com/info"

# --- Global Tracking ---
queues           = {}
playing_messages = {}   # {chat_id: message_id}
current_playing  = {}   # {chat_id: song_details}
BOT_START_TIME   = datetime.now()
