import os
import inspect
from typing import List, Dict, Any

# smolagents imports are isolated purely to this factory connector file
from smolagents import CodeAgent, LiteLLMModel, Tool

# --- UNIFIED INTERFACE CLASSES ---
class LLM:
    def __init__(self, model, base_url, api_key, temperature=0.3, max_tokens=4096, **kwargs):
        # smolagents leverages LiteLLM models seamlessly via LiteLLMModel
        self.model_name = model if model.startswith("ollama/") else f"ollama/{model}"

        # Override environment configurations locally so LiteLLM client initializes properly
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = base_url

        self.native_instance = LiteLLMModel(
            model_id=self.model_name,
            api_base=base_url,
            api_key=api_key,
            temperature=float(temperature),
            max_tokens=int(max_tokens)
        )

class Agent:
    def __init__(self, role, goal, backstory, llm, tools=None, **kwargs):
        self.role = role
        self.name = role.replace(" ", "_").replace("-", "_")
        self.goal = goal
        self.backstory = backstory
        self.llm = llm

        # Parse and wrap tools array into compliant schemas
        self.native_tools = []
        raw_tools = tools or []
        for t in raw_tools:
            if isinstance(t, Tool):
                self.native_tools.append(t)
            elif hasattr(t, "_func") or callable(t):
                # Convert standard function or wrapped tool to native Tool instance
                self.native_tools.append(AdapterTool(t))

        # Initialize an explicit native CodeAgent wrapper
        self.native_instance = CodeAgent(
            tools=self.native_tools,
            model=self.llm.native_instance,
            additional_authorized_imports=["os", "requests", "json", "time", "pytest"],
            prompt_templates=None # Employs standard default system instructions
        )

class Task:
    def __init__(self, description, expected_output, agent, **kwargs):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent

class Crew:
    def __init__(self, agents, tasks, verbose=True, **kwargs):
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose

    def kickoff(self) -> str:
        """Executes the task chain sequentially passing historical data context."""
        context_history = ""
        last_result = ""

        for idx, task in enumerate(self.tasks):
            agent = task.agent

            # Construct a comprehensive execution prompt for the code agent sandbox loop
            execution_prompt = (
                f"You are acting as the system's designated {agent.role}.\n"
                f"Your core persona context:\n{agent.backstory}\n"
                f"Your overarching architectural goal: {agent.goal}\n\n"
                f"MISSION ASSIGNMENT TASK ({idx + 1}/{len(self.tasks)}):\n{task.description}\n\n"
                f"EXPECTED OUTPUT FORMAT MANDATE:\n{task.expected_output}\n\n"
            )

            if context_history:
                execution_prompt += f"PREVIOUS WORK CONTEXT AND AGENT HIGHLIGHTS:\n{context_history}\n\n"

            execution_prompt += "Execute the task using your tools and write a final return response statement."

            try:
                # Invoke the underlying smolagents local execution block loop run
                last_result = agent.native_instance.run(execution_prompt)

                # Append result history logs for subsequent agents in the pipeline
                context_history += f"\n--- Output from Step {idx + 1} ({agent.name}) ---\n{str(last_result)}\n"
            except Exception as e:
                raise RuntimeError(f"smolagents sandbox error during step {idx + 1} ({agent.name}): {str(e)}")

        return str(last_result)

# --- ADAPTERS ---
class AdapterTool(Tool):
    """Dynamically converts functions and tools into native smolagents Tool classes."""
    def __init__(self, custom_tool):
        # Discover execution method target
        self.func = getattr(custom_tool, "_func", custom_tool)

        # Read or reflect naming metadata definitions
        name = getattr(custom_tool, "name", getattr(self.func, "__name__", "custom_function"))
        description = getattr(custom_tool, "description", getattr(self.func, "__doc__", "Execute core task logic"))

        # Derive structural variable formatting schemas from function inspection
        sig = inspect.signature(self.func)
        inputs: Dict[str, Any] = {}
        for param_name, param in sig.parameters.items():
            if param_name == "self": continue
            # Map type hints to expected tool property values
            p_type = "string" if param.annotation == str else "any"
            inputs[param_name] = {"type": p_type, "description": f"Argument parameter {param_name}"}

        output_type = "string" if sig.return_annotation == str else "any"

        # Initialize parent structural properties
        super().__init__()
        self.name = name
        self.description = description
        self.inputs = inputs
        self.output_type = output_type

    def forward(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

def tool(*args, **kwargs):
    """
    Unified decorator mapping custom workspace methods to standard function stubs.
    Attaches critical descriptors utilized by the AdapterTool conversion layer.
    """
    def decorator(func):
        func.name = kwargs.get("name", func.__name__)
        func.description = kwargs.get("description", func.__doc__ or "Execute tool actions")
        func._func = func
        return func
    return decorator

# --- AGNOSTIC INTERFACE STUBS ---
class Knowledge:
    CSV = object; Docling = object; JSON = object
    Excel = object; TextFile = object; XML = object

class DuckDuckGoSearchTool(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.name = "duckduckgo_search"
        self.description = "Search the web for technical documentation and standards."
        self.inputs = {"query": {"type": "string", "description": "The search query string"}}
        self.output_type = "string"
    def forward(self, query: str) -> str:
        # Simple dynamic web scraper pass-through stub
        return f"Simulated search results for query parameter: {query}"
