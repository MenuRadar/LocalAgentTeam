from .integrations import discover_integrations

class Manager:
    def __init__(self):
        self.registry = discover_integrations()

    def capabilities(self):
        return [x.model_dump() for x in self.registry.all()]

    async def route(self, task: str, input_url: str | None = None):
        t = task.lower()
        # Prefer a real crawler for URL/menu extraction.
        if input_url and any(x in t for x in ("crawl","scrape","extract","scan","menu","source")):
            item = self.registry.get("crawl4ai")
            if item and item.available:
                return {"route":"crawl4ai","reason":"URL extraction task","available":True}
            return {"route":"crawl4ai","reason":"URL extraction requested but Crawl4AI is not installed","available":False}
        if any(x in t for x in ("browser","click","login","navigate","website")):
            item = self.registry.get("browser-use")
            if item and item.available:
                return {"route":"browser-use","reason":"browser interaction task","available":True}
            return {"route":"browser-use","reason":"browser interaction requested but Browser Use is not installed","available":False}
        if any(x in t for x in ("code","repository","github","fix","build")):
            item = self.registry.get("openhands")
            if item and item.available:
                return {"route":"openhands","reason":"coding/repository task","available":True}
            return {"route":"openhands","reason":"coding task requested but OpenHands is not installed","available":False}
        item = self.registry.get("openai-agents")
        if item and item.available:
            return {"route":"openai-agents","reason":"general orchestration task","available":True}
        return {"route":"manual","reason":"No suitable installed provider","available":False}
