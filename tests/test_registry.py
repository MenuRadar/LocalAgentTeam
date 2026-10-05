from agent_team.registry import AgentRegistry
from agent_team.models import AgentCapability
def test_only_available_integrations_are_selected():
 r=AgentRegistry(); r.register(AgentCapability(name='x',provider='X',capabilities=['crawl'],available=True)); r.register(AgentCapability(name='y',provider='Y',capabilities=['crawl'],available=False)); assert [x.name for x in r.available_for('crawl')]==['x']
