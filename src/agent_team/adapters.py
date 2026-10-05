from typing import Any

class BrowserUseAdapter:
    async def run(self,instruction:str,**kwargs)->dict[str,Any]:
        try: import browser_use
        except ImportError as e: raise RuntimeError("Browser Use is not installed") from e
        return {"provider":"browser-use","instruction":instruction,"status":"adapter-ready"}

class Crawl4AIAdapter:
    async def run(self,url:str,**kwargs)->dict[str,Any]:
        try: import crawl4ai
        except ImportError as e: raise RuntimeError("Crawl4AI is not installed") from e
        return {"provider":"crawl4ai","url":url,"status":"adapter-ready"}

class OpenHandsAdapter:
    async def run(self,instruction:str,**kwargs)->dict[str,Any]:
        try: import openhands
        except ImportError as e: raise RuntimeError("OpenHands SDK is not installed") from e
        return {"provider":"openhands","instruction":instruction,"status":"adapter-ready"}
