from lib.logger import log_text

def broadcast_status(message: str) -> bool:
    """Standard fallback route printing status payloads cleanly to system logs."""
    log_text("📋 Logging response data token cleanly to stdout console streams:")
    print(f"\n{message}\n")
    return True
