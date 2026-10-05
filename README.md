# LocalAgentTeam

A local orchestration layer that **combines existing agent/tool ecosystems instead of rebuilding them**.

## Core principle

This project does not try to replace Browser Use, Crawl4AI, OpenAI Agents SDK, OpenHands, or GitHub. It provides a thin local interface that discovers capabilities, routes work to the appropriate existing tool/agent, passes structured handoffs between them, and applies approval/resource policies.

### Reused components
- **OpenAI Agents SDK** — orchestration/model-agent runtime when installed.
- **Browser Use** — browser automation.
- **Crawl4AI** — crawling and extraction.
- **OpenHands SDK** — coding/repository tasks when installed.
- **PyGithub / GitHub API** — publishing and repository operations.
- **psutil** — local CPU/RAM guard.
- **SQLite** — durable task state; no external database required.

The adapters are intentionally optional: the application can start and inspect capabilities even if one integration is not installed.

## Architecture

`USER -> MANAGER -> CAPABILITY REGISTRY -> EXISTING TOOL/AGENT -> HANDOFF -> QA/APPROVAL -> PUBLISHER`

For MenuRadar:

`source URL -> browser/crawler -> structured data -> content/SEO -> QA -> approval -> GitHub -> homepage/sitemap`

The system stops publishing if a completeness check fails (for example, source has 212 menu items but output contains 178).

## Quick start (Windows)

1. Install Python 3.11+.
2. Run `powershell -ExecutionPolicy Bypass -File scripts/install.ps1`.
3. Copy `.env.example` to `.env` and add only the keys you actually use.
4. Run `powershell -ExecutionPolicy Bypass -File scripts/start.ps1`.

Default policy is safe: approval is required and auto-publish is disabled.

## Optional integrations

Install the packages you need. The core registry never fabricates a missing integration.

```powershell
pip install openai-agents browser-use crawl4ai psutil pydantic pydantic-settings pyyaml aiosqlite httpx python-dotenv
# Optional coding integration:
pip install openhands-sdk
```

Browser Use/Crawl4AI may have additional system/browser requirements; their own upstream installation process remains authoritative.

## Commands

```powershell
python -m agent_team.main doctor
python -m agent_team.main run --type crawl --input-url "https://example.com"
python -m agent_team.main run --type menuradar --input-url "https://menupricetoday.com/us/brands/kfc"
```

## Safety

- No automatic publishing by default.
- No destructive shell/repository actions without explicit policy approval.
- Source facts are preserved but source prose is not copied verbatim.
- Each task gets an isolated workspace.
- CPU/RAM limits prevent launching more work when the machine is under pressure.
- Existing capable integrations are preferred over creating duplicate agents.

## Development

`pytest` runs the local unit tests. GitHub Actions runs the same test suite on pushes/PRs.
