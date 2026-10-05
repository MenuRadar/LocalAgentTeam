from .integrations import discover_integrations

class Manager:
    def __init__(self):
        self.registry = discover_integrations()

    def capabilities(self):
        return [x.model_dump() for x in self.registry.all()]

    async def route(self, task: str, input_url: str | None = None):
        t = task.lower()
        if input_url and any(x in t for x in ("crawl","scrape","extract","scan","menu")):
            return {"route":"crawl4ai","reason":"URL extraction task"}
        if any(x in t for x in ("browser","click","login","navigate")):
            return {"route":"browser-use","reason":"browser interaction task"}
        if any(x in t for x in ("code","repository","github","fix","build")):
            return {"route":"openhands","reason":"coding/repository task"}
        item = self.registry.get("openai-agents")
        if item and item.available:
            return {"route":"openai-agents","reason":"general orchestration task"}
        return {"route":"manual","reason":"No suitable installed provider"}
