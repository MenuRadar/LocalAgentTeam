from agent_team.pipeline import MenuRadarPipeline
def test_approval_precedes_github():
 n=[x.to_agent for x in MenuRadarPipeline().plan('https://example.com')]; assert n.index('human-approval')<n.index('github'); assert n[0]=='browser-use'
