"""
Simple JSON-based database to track users and chats per bot token.
"""
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "bot_database.json")


def _load() -> dict:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save(data: dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _token_data(data: dict, token: str) -> dict:
    if token not in data:
        data[token] = {"users": [], "groups": []}
    return data[token]


def add_user(token: str, user_id: int):
    data = _load()
    td = _token_data(data, token)
    if user_id not in td["users"]:
        td["users"].append(user_id)
        _save(data)


def add_group(token: str, chat_id: int):
    data = _load()
    td = _token_data(data, token)
    if chat_id not in td["groups"]:
        td["groups"].append(chat_id)
        _save(data)


def get_users(token: str) -> list:
    data = _load()
    return data.get(token, {}).get("users", [])


def get_groups(token: str) -> list:
    data = _load()
    return data.get(token, {}).get("groups", [])


def get_all_users_all_bots() -> list:
    """All unique users across all bot tokens."""
    data = _load()
    seen = set()
    for td in data.values():
        for uid in td.get("users", []):
            seen.add(uid)
    return list(seen)


def get_all_groups_all_bots() -> list:
    """All unique groups across all bot tokens."""
    data = _load()
    seen = set()
    for td in data.values():
        for gid in td.get("groups", []):
            seen.add(gid)
    return list(seen)
