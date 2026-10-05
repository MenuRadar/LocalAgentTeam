# LocalAgentTeam

LocalAgentTeam is a local orchestration/interface layer — not a replacement for the agents already available.

## Core rule

Discover and reuse existing capable tools first. Never build a duplicate agent when an existing provider can perform the capability.

## Reused providers
- OpenAI Agents SDK — manager-style agent orchestration.
- Browser Use — browser automation.
- Crawl4AI — web crawling and extraction.
- OpenHands — coding/repository work when a supported SDK client is available.
- PyGithub / GitHub API — repository publishing.
- psutil + SQLite — local resource and state management.

## Local interface

Install and run:

    powershell -ExecutionPolicy Bypass -File scripts/install.ps1
    python -m agent_team.main doctor
    python -m agent_team.main web

Then open http://127.0.0.1:8787.

The current UI provides provider detection, task routing, Crawl4AI execution, OpenAI Agents execution, and MenuRadar pipeline planning.

## MenuRadar flow

USER -> MANAGER/ROUTER -> existing providers -> structured handoff -> CONTENT/SEO -> QA -> HUMAN APPROVAL -> GitHub Publisher -> homepage/sitemap/verification

Completeness is a hard publishing gate. If a source has 212 menu items and output has 178, the task is BLOCKED and must not publish.

## Safety defaults
- Human approval required.
- Auto-publish disabled.
- Source prose is not copied verbatim.
- Missing integrations are reported, not fabricated.
- Resource limits prevent starting work when the machine is under pressure.

## Environment

    OPENAI_API_KEY=
    GITHUB_TOKEN=
    GITHUB_REPO=MenuRadar/MenuRadar.github.io

Install all optional adapters with:

    pip install -e .[all]

Browser Use and Crawl4AI may require their own browser/system setup; follow their upstream installation requirements.

## Development

    pytest -q

GitHub Actions runs the tests on pushes and pull requests.