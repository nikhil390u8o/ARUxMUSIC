import os
from datetime import datetime

# --- Bot Credentials ---
API_ID   = 33603336
API_HASH = "c9683a8ec3b886c18219f650fc8ed429"

# BOT_TOKEN: env var se override hota hai jab /clone se spawn hota hai
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8596765113:AAGlK4eW_0Qxlt6hfD_ElFcwronZivnNM6w")

SESSION_STRING = "BQE-4i0APCNg7Qe44uWYI_J9nczGmB_q-JxizDZeAqmFq7nnTfuWVCmRtg6WuQKWn6BD4kkLWpUquwPwxM9IFVZMzxRUck51sdWKQUSHxu4N7hNdw8qWHJsKSTIpzZAgla8SrRLKJVpOTbeN0GgNAeaffdHPJ_rFQNHbxKIcoPWZqoGnNwPYPIad3Ir4KGWDFXGL7sbje8SYiDeYEmEjuNzRScxIqqxMaTREk4LLutGI688RC2TS59_YCFbZ0Polo_sHt3gyVKSF29aUiSbUQ2QwR1ZLlXvdTri5YIAqS2IuC3T7mFgbRvFVKU2MbEaW83eOuXU5SuO8tEgUMLeCUL8VDNia_gAAAAHKarFXAA"
# Main bot ka owner
OWNER_ID = 7450385463

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
