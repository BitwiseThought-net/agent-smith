import requests
from ai_layer.orchestrator import tool
from lib.utils import get_config_value

# --- PLUGIN METADATA ---
INFO = {
    "instructions": [
        "1. Go to Discord Developer Portal (https://discord.com).",
        "2. Create 'New Application' named Agent-Smith.",
        "3. Go to 'Bot' tab: Reset/Copy Token into 'BOT_TOKEN' in SETTINGS below.",
        "4. Enable 'Message Content Intent' under Privileged Gateway Intents.",
        "5. Go to 'OAuth2' -> 'URL Generator': Select scopes 'bot' and 'applications.commands'.",
        "6. Select Permissions: 'Send Messages', 'Read Message History', 'Use Slash Commands'.",
        "7. Use generated URL to invite the bot to your server.",
        "8. Enable Developer Mode in Discord (User Settings -> Advanced).",
        "9. Right-click Server for 'SERVER_ID' and target Channel for 'CHANNEL_ID'."
    ]
}

# --- PLUGIN SETTINGS ---
# Default is empty. If values are provided here, they take absolute priority over central config.
SETTINGS = {
    "BOT_TOKEN": "",
    "SERVER_ID": "",
    "CHANNEL_ID": "",
    "RESPONSE_PREFIX_ENABLED": True
}

def _send_msg(message: str) -> bool:
    """
    Centralized communication routing endpoint helper.
    Priority 1: Check local SETTINGS dictionary context first.
    Priority 2: Fall back dynamically to nested UPPERCASE DISCORD_BOT_SETTINGS maps in config.json.
    """
    # FIXED: Pull the uppercase configuration sub-dictionary object baseline
    bot_settings = get_config_value("DISCORD_BOT_SETTINGS", {})

    # 1. Resolve Bot Token
    BOT_TOKEN = SETTINGS.get("BOT_TOKEN")
    if not BOT_TOKEN:
        # FIXED: Mapped key lookups to trace the correct nested UPPERCASE variable paths
        BOT_TOKEN = bot_settings.get("BOT_TOKEN") if isinstance(bot_settings, dict) else None
    if not BOT_TOKEN:
        return False

    # 2. Resolve Server ID (Guild ID)
    SERVER_ID = SETTINGS.get("SERVER_ID")
    if not SERVER_ID:
        # FIXED: Mapped key lookups to trace the correct nested UPPERCASE variable paths
        SERVER_ID = bot_settings.get("GUILD_ID") if isinstance(bot_settings, dict) else None
    if not SERVER_ID:
        return False

    # 3. Resolve Channel ID
    CHANNEL_ID = SETTINGS.get("CHANNEL_ID")
    if not CHANNEL_ID:
        # FIXED: Mapped key lookups to trace the correct nested UPPERCASE variable paths
        CHANNEL_ID = bot_settings.get("TARGET_CHANNEL_ID") if isinstance(bot_settings, dict) else None
    if not CHANNEL_ID:
        return False


    # MANDATORY REST API ENDPOINT: Absolute scheme, explicit version, and proper slashes
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, headers=headers, json={"content": message}, timeout=10)
        return res.status_code in [200, 201]
    except Exception:
        return False

@tool("discord_interaction")
def discord_interaction(message: str):
    """Sends agent responses directly to the configured Discord channel using the Bot Token."""
    success = _send_msg(message)
    return "✅ Response successfully posted to Discord." if success else "❌ Discord API Error."

def broadcast_status(message: str) -> bool:
    """Dynamic interface endpoint executing direct message delivery."""
    return _send_msg(message)

def register():
    """Provides the tool and identity rules to the main service loader package."""
    prefix_enabled = SETTINGS.get("RESPONSE_PREFIX_ENABLED")
    if prefix_enabled is None:
        bot_settings = get_config_value("DISCORD_BOT_SETTINGS", {})
        if isinstance(bot_settings, dict):
            # FIXED: Mapped to trace uppercase key layout parameters
            prefix_enabled = bot_settings.get("RESPONSE_PREFIX_ENABLED", True)
        else:
            prefix_enabled = True

    return {
        "tools": [discord_interaction],
        "enabled_for": ["*"],
        "identity_prefix": bool(prefix_enabled)
    }
