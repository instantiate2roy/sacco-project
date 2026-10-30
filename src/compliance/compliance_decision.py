from dataclasses import dataclass, field

from .proposed_action import ProposedAction
from .rule_outcome import RuleOutcome


@dataclass(frozen=True)
class ComplianceDecision:
    action: ProposedAction
    allowed: bool
    outcomes: list[RuleOutcome] = field(default_factory=list)

    @property
    def blocked_by(self) -> str:
        """The first rule that blocked the action, or '' if it was allowed."""
        return next((o.rule for o in self.outcomes if not o.allowed), "")

    @property
    def reason(self) -> str:
        return next((o.reason for o in self.outcomes if not o.allowed), "")
