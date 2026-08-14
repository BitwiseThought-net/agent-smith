import os
from ai_layer.orchestrator import tool
from lib.utils import get_config_value

@tool("file_write_safe")
def file_write_safe(filename: str, content: str) -> str:
    # Centralized Configuration: Dynamically look up the target output directory
    safe_dir = get_config_value("SAFE_OUTPUT_DIR", "/app/output")

    # Security Constraint: Block path traversal tricks completely
    if ".." in filename or filename.startswith("/"):
        return "❌ Security Violation: Path traversal or absolute paths are forbidden. Provide a relative filename only."

    # Validate that the configured target sandbox folder physically exists on the filesystem
    if not os.path.exists(safe_dir):
        try:
            os.makedirs(safe_dir)
        except Exception as e:
            return f"❌ System Error: Failed to initialize sandbox workspace path: {str(e)}"

    # Construct the absolute path bound strictly within the workspace
    target_path = os.path.join(safe_dir, filename)

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Success: File successfully written to sandbox workspace path: {filename}"
    except Exception as e:
        return f"❌ File Write Error: Failed to execute operation: {str(e)}"

def get_tools():
    return [file_write_safe]
