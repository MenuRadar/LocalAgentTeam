from dataclasses import dataclass

@dataclass
class CompletenessReport:
    passed: bool
    expected: int
    actual: int
    message: str

def check_completeness(expected: int, actual: int) -> CompletenessReport:
    passed = expected == actual
    message = (f"Completeness OK: {actual}/{expected} items." if passed else
               f"BLOCKED: source contains {expected} items but output contains {actual}. Do not publish.")
    return CompletenessReport(passed, expected, actual, message)
