import os
import subprocess
from ai_layer.orchestrator import tool
from lib.utils import get_config_value

@tool("safe_terminal_exec")
def safe_terminal_exec(command: str) -> str:
    # Centralized Configurations: Pull workspace and timeout properties
    safe_dir = get_config_value("SAFE_OUTPUT_DIR", "/app/output")
    exec_timeout = int(get_config_value("TOOL_EXEC_TIMEOUT", 30))

    # Security Check: Only allow clean, verified execution commands
    allowed_prefixes = ["python ", "pytest ", "python3 "]
    if not any(command.startswith(p) for p in allowed_prefixes):
        return "❌ Security Violation: Only 'python' and 'pytest' execution patterns are permitted."

    # Security Check: Prevent path traversal breakouts inside tool args
    if ".." in command:
        return "❌ Security Violation: Path traversal operations inside command definitions are forbidden."

    if not os.path.exists(safe_dir):
        try:
            os.makedirs(safe_dir)
        except Exception as e:
            return f"❌ System Error: Failed to initialize sandbox workspace path: {str(e)}"

    try:
        # Run the validation script strictly using the dynamic safe_dir as the working directory root
        result = subprocess.run(
            command,
            shell=True,
            cwd=safe_dir,
            capture_output=True,
            text=True,
            timeout=exec_timeout
        )
        output = result.stdout if result.stdout else ""
        errors = result.stderr if result.stderr else ""
        return f"--- Sandbox Execution Output ---\n{output}\n--- Errors/Warnings ---\n{errors}"
    except subprocess.TimeoutExpired:
        return f"❌ Execution Failed: Command execution timed out after {exec_timeout} seconds."
    except Exception as e:
        return f"❌ Execution Failed: Shell system loop error: {str(e)}"

def get_tools():
    return [safe_terminal_exec]
