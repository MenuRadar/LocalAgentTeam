from agent_team.qa import check_completeness

def test_completeness_blocks_mismatch():
    report=check_completeness(212,178)
    assert not report.passed
    assert "BLOCKED" in report.message

def test_completeness_passes():
    assert check_completeness(212,212).passed
