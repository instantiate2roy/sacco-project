from dataclasses import dataclass


@dataclass(frozen=True)
class RuleOutcome:
    rule: str
    allowed: bool
    reason: str = ""
