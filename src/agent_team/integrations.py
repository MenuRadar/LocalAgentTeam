import importlib.util
from .models import AgentCapability
from .registry import AgentRegistry

def discover_integrations():
    r = AgentRegistry()
    checks = [
        ("openai-agents", "OpenAI Agents SDK", "agents", ["orchestration", "agent"]),
        ("browser-use", "Browser Use", "browser_use", ["browser", "web"]),
        ("crawl4ai", "Crawl4AI", "crawl4ai", ["crawl", "extract"]),
        ("openhands", "OpenHands SDK", "openhands", ["coding", "repository"]),
        ("pygithub", "PyGithub", "github", ["publish", "repository"]),
    ]
    for name, provider, module, caps in checks:
        ok = importlib.util.find_spec(module) is not None
        r.register(AgentCapability(name=name, provider=provider, capabilities=caps,
                                   available=ok, reason=None if ok else f"{module} is not installed"))
    return r
