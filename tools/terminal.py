from ai_layer.orchestrator import EXECTool

def get_tools():
    """
    Returns the standard execution tool mapped by the orchestration layer.
    Allows agents to execute shell commands natively within the active framework container.
    """
    # Expose the tool safely. If the active factory does not support execution,
    # it safely returns an empty list to prevent runtime crashes.
    if EXECTool:
        return [EXECTool()]
    return []
