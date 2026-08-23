import os
import json
from pathlib import Path
from typing import Any

# Cache path locations relative to standard execution directories
CONFIG_FILE_PATH = Path("config.json")


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Centralized configuration manager.
    Priority 1: config.json (checked dynamically to allow on-the-fly updates)
    Priority 2: system environment / .env wrapper variables via os.getenv
    Priority 3: local default parameter fallback value
    """
    # Priority 1: Check inside config.json if the file physically exists on host
    if CONFIG_FILE_PATH.exists():
        try:
            with open(CONFIG_FILE_PATH, "r") as f:
                config_data = json.load(f)
                # Safely return value if key exists and is not explicitly null
                if config_data and key in config_data and config_data[key] is not None:
                    return config_data[key]
        except (json.JSONDecodeError, IOError):
            # Gracefully ignore malformed json states during live writing changes
            pass

    # Priority 2: Fallback to reading the system environment
    # This is the ONLY legal place in the application where os.getenv is executed
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    # Priority 3: Fallback to the default parameter value
    return default


def update_heartbeat():
    """Writes a literal UNIX timestamp to the health-check heart monitor file."""
    import time

    try:
        with open("/tmp/heartbeat", "w") as f:
            f.write(str(int(time.time())))
    except IOError:
        pass


def set_mission_timeout(seconds: int):
    """Sets a hard execution limit timer baseline on the system runtime process."""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(
            "🚨 Critical Failure: System mission execution hard limit timed out."
        )

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)


def clear_mission_timeout():
    """Clears the active execution limit timer baseline safely."""
    import signal

    signal.alarm(0)


def get_active_plugins() -> dict:
    """Safely retrieves active JSON/legacy system feature toggles."""
    plugins_file = Path("plugins/plugins.json")
    if plugins_file.exists():
        try:
            with open(plugins_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def ensure_sandbox_dir(safe_dir: str):
    """
    Ensures a sandbox workspace directory exists on disk, creating it if
    missing. Shared by tools that need a writable sandbox root (file writes,
    terminal execution) so the create-and-report-failure logic lives in one
    place instead of being duplicated across each tool module.

    Returns None on success, or a formatted error string on failure - the
    caller is expected to return that string directly to short-circuit.
    """
    if not os.path.exists(safe_dir):
        try:
            os.makedirs(safe_dir)
        except Exception as e:
            return f"❌ System Error: Failed to initialize sandbox workspace path: {str(e)}"
    return None
