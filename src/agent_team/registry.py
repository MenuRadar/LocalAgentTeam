from .models import AgentCapability

class AgentRegistry:
    """Registry of available integrations. It never invents unavailable agents."""
    def __init__(self):
        self._items: dict[str, AgentCapability] = {}

    def register(self, item: AgentCapability) -> None:
        self._items[item.name] = item

    def get(self, name: str) -> AgentCapability | None:
        return self._items.get(name)

    def available_for(self, capability: str) -> list[AgentCapability]:
        return [x for x in self._items.values() if x.available and capability in x.capabilities]

    def all(self) -> list[AgentCapability]:
        return list(self._items.values())
