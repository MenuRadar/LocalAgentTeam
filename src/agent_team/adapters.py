from typing import Any
import os

class OpenAIAgentsAdapter:
    async def run(self, instruction: str, *, name: str = "Local Manager", **kwargs) -> dict[str, Any]:
        try:
            from agents import Agent, Runner
        except ImportError as e:
            raise RuntimeError("OpenAI Agents SDK is not installed") from e
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not configured")
        agent = Agent(name=name, instructions=(
            "You are a local orchestration specialist. Reuse existing tools and "
            "never invent unavailable integrations. Return concise structured results."
        ))
        result = await Runner.run(agent, instruction)
        return {"provider":"openai-agents","status":"completed",
                "agent":getattr(result.last_agent,"name",name),"output":result.final_output}

class BrowserUseAdapter:
    async def run(self, instruction: str, **kwargs) -> dict[str, Any]:
        try:
            import browser_use
        except ImportError as e:
            raise RuntimeError("Browser Use is not installed") from e
        Agent = getattr(browser_use, "Agent", None)
        if Agent is None:
            raise RuntimeError("Installed Browser Use package does not expose Agent")
        llm = kwargs.get("llm")
        if llm is None:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model=kwargs.get("model", "gpt-4.1-mini"))
            except ImportError as e:
                raise RuntimeError("Install the LLM provider required by your Browser Use release") from e
        agent = Agent(task=instruction, llm=llm)
        result = await agent.run()
        return {"provider":"browser-use","status":"completed","output":str(result)}

class Crawl4AIAdapter:
    async def run(self, url: str, **kwargs) -> dict[str, Any]:
        try:
            from crawl4ai import AsyncWebCrawler
        except ImportError as e:
            raise RuntimeError("Crawl4AI is not installed") from e
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
        return {"provider":"crawl4ai","status":"completed" if getattr(result,"success",True) else "failed",
                "url":url,"markdown":getattr(result,"markdown","") or "",
                "html":getattr(result,"cleaned_html","") or "",
                "error":getattr(result,"error_message",None)}

class OpenHandsAdapter:
    async def run(self, instruction: str, **kwargs) -> dict[str, Any]:
        try:
            import openhands  # noqa: F401
        except ImportError as e:
            raise RuntimeError("OpenHands SDK is not installed") from e
        raise RuntimeError("OpenHands is installed, but this release exposes no supported client API in the adapter yet")
