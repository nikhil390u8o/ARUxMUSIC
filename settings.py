import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "bot_settings.json")

# ─── Default fallback values ───────────────────────────────────────────────
DEFAULTS = {
    "support_link": "https://t.me/sxyaru",
    "start_img":    "https://files.catbox.moe/uyum1c.jpg",
    "ping_img":     "https://files.catbox.moe/nacfzm.jpg",
    "owner_username": "sxyaru",
    "owner_id":     None,   # filled at runtime from env / config
}

# ─── Internal helpers ──────────────────────────────────────────────────────

def _load() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save(data: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── Public API ────────────────────────────────────────────────────────────

def get(token: str, key: str, default=None):
    """Get a setting for a specific bot token."""
    data = _load()
    bot_cfg = data.get(token, {})
    if key in bot_cfg:
        return bot_cfg[key]
    if default is not None:
        return default
    return DEFAULTS.get(key)

def set(token: str, key: str, value):
    """Save a setting for a specific bot token."""
    data = _load()
    if token not in data:
        data[token] = {}
    data[token][key] = value
    _save(data)

def get_all(token: str) -> dict:
    """Return merged settings (stored overrides on top of DEFAULTS)."""
    data = _load()
    merged = dict(DEFAULTS)
    merged.update(data.get(token, {}))
    return merged

def init_clone(token: str, owner_id: int, owner_username: str,
               bot_username: str = "", pid: int = 0):
    """Called once when a new clone is first set up."""
    data = _load()
    if token not in data:
        data[token] = {}
    data[token].setdefault("owner_id", owner_id)
    data[token].setdefault("owner_username", owner_username)
    data[token].setdefault("bot_username", bot_username)
    data[token]["pid"] = pid
    data[token]["is_clone"] = True
    _save(data)

def update_pid(token: str, pid: int):
    """Update running PID of a clone."""
    data = _load()
    if token in data:
        data[token]["pid"] = pid
        _save(data)

def remove_clone(token: str):
    """Remove a clone's settings entirely."""
    data = _load()
    if token in data:
        del data[token]
        _save(data)

def get_clones_by_owner(owner_id: int) -> list:
    """Return list of clone dicts belonging to given owner."""
    data = _load()
    result = []
    for token, cfg in data.items():
        if cfg.get("is_clone") and cfg.get("owner_id") == owner_id:
            result.append({"token": token, **cfg})
    return result

def get_all_clones() -> list:
    """Return all registered clones."""
    data = _load()
    result = []
    for token, cfg in data.items():
        if cfg.get("is_clone"):
            result.append({"token": token, **cfg})
    return result


# ═══════════════════════════════════════════════════════
# DATABASE FUNCTIONS — users/groups track karne ke liye
# ═══════════════════════════════════════════════════════

DB_KEY = "__db__"

def _db_load() -> dict:
    data = _load()
    if DB_KEY not in data:
        data[DB_KEY] = {}
    return data

def _db_save(data: dict):
    _save(data)

def add_user(token: str, user_id: int):
    data = _db_load()
    db   = data.setdefault(DB_KEY, {})
    tok  = db.setdefault(token, {"users": [], "groups": []})
    if user_id not in tok["users"]:
        tok["users"].append(user_id)
        _save(data)

def add_group(token: str, chat_id: int):
    data = _db_load()
    db   = data.setdefault(DB_KEY, {})
    tok  = db.setdefault(token, {"users": [], "groups": []})
    if chat_id not in tok["groups"]:
        tok["groups"].append(chat_id)
        _save(data)

def get_users(token: str) -> list:
    data = _load()
    return data.get(DB_KEY, {}).get(token, {}).get("users", [])

def get_groups(token: str) -> list:
    data = _load()
    return data.get(DB_KEY, {}).get(token, {}).get("groups", [])

def get_all_users_all_bots() -> list:
    data  = _load()
    seen  = set()
    for td in data.get(DB_KEY, {}).values():
        for uid in td.get("users", []):
            seen.add(uid)
    return list(seen)

def get_all_groups_all_bots() -> list:
    data = _load()
    seen = set()
    for td in data.get(DB_KEY, {}).values():
        for gid in td.get("groups", []):
            seen.add(gid)
    return list(seen)
