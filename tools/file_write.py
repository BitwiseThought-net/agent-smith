from ai_layer.orchestrator import FileWriterTool

def get_tools():
    """
    Returns the FileWriterTool to allow agents to write or update local files.
    """
    return [FileWriterTool()]
