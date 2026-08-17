"""Webhook integration module for sending agent responses to Discord webhooks."""
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
    """Send message via Discord API."""
    bot_token = SETTINGS.get("BOT_TOKEN")
    if not bot_token:
        bot_token = get_config_value("BOT_TOKEN")
    if not bot_token:
        return False

    server_id = SETTINGS.get("SERVER_ID")
    if not server_id:
        server_id = get_config_value("SERVER_ID")
    if not server_id:
        return False

    channel_id = SETTINGS.get("CHANNEL_ID")
    if not channel_id:
        channel_id = get_config_value("CHANNEL_ID")
    if not channel_id:
        return False

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json={"content": message}, timeout=10)
        return res.status_code in [200, 201]
    except requests.RequestException:
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
    """Register the Discord webhook tool and return tool configuration."""
    return {
        "tools": [discord_interaction],
        "enabled_for": ["*"],
        "identity_prefix": SETTINGS.get("RESPONSE_PREFIX_ENABLED", True),
    }
