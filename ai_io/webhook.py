import requests
from ai_layer.orchestrator import tool
from lib.utils import get_config_value

# --- PLUGIN METADATA ---
INFO = {
    "instructions": [
        "1. Go to Discord Developer Portal (https://discord.com).",
        "2. Create 'New Application' named Agent-Smith.",
        "3. Go to 'Bot' tab: Reset/Copy Token into 'bot_token' in SETTINGS below.",
        "4. Enable 'Message Content Intent' under Privileged Gateway Intents.",
        "5. Go to 'OAuth2' -> 'URL Generator': Select scopes 'bot' and 'applications.commands'.",
        "6. Select Permissions: 'Send Messages', 'Read Message History', 'Use Slash Commands'.",
        "7. Use generated URL to invite the bot to your server.",
        "8. Enable Developer Mode in Discord (User Settings -> Advanced).",
        "9. Right-click Server for 'server_id' and target Channel for 'channel_id'.",
    ]
}

SETTINGS = {
    "BOT_TOKEN": "",
    "SERVER_ID": "",
    "CHANNEL_ID": "",
    "RESPONSE_PREFIX_ENABLED": True,
}


def _send_msg(message: str) -> bool:
    BOT_TOKEN = SETTINGS.get("BOT_TOKEN")
    if not BOT_TOKEN:
        BOT_TOKEN = get_config_value("BOT_TOKEN")
    if not BOT_TOKEN:
        return False

    SERVER_ID = SETTINGS.get("SERVER_ID")
    if not SERVER_ID:
        SERVER_ID = get_config_value("SERVER_ID")
    if not SERVER_ID:
        return False

    CHANNEL_ID = SETTINGS.get("CHANNEL_ID")
    if not CHANNEL_ID:
        CHANNEL_ID = get_config_value("CHANNEL_ID")
    if not CHANNEL_ID:
        return False

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}
    try:
        res = requests.post(url, headers=headers, json={"content": message}, timeout=10)
        return res.status_code in [200, 201]
    except Exception:
        return False


@tool("discord_interaction")
def discord_interaction(message: str):
    """Sends agent responses directly to the configured Discord channel using the Bot Token."""
    success = _send_msg(message)
    return (
        "✅ Response successfully posted to Discord."
        if success
        else "❌ Discord API Error."
    )


def broadcast_status(message: str) -> bool:
    """Dynamic interface endpoint executing direct message delivery."""
    return _send_msg(message)


def register():
    return {
        "tools": [discord_interaction],
        "enabled_for": ["*"],
        "identity_prefix": SETTINGS.get("RESPONSE_PREFIX_ENABLED", True),
    }
