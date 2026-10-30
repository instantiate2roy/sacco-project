from .contact_rule import ContactRule


class PromisePendingRule(ContactRule):
    name = "Promise pending"

    def __init__(self, policy):
        self.active = policy.compliance["hold_while_ptp_pending"]

    def check(self, action, history, case):
        if self.active and case.get("ptp_pending_until") and action.planned_at.date() <= case["ptp_pending_until"]:
            return self._block(f"promise to pay due {case['ptp_pending_until']}")
        return self._allow()
