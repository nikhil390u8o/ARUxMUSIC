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
