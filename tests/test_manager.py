from agent_team.manager import Manager

def test_manager_has_capability_registry():
    m=Manager()
    assert isinstance(m.capabilities(), list)
