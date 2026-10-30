from .contact_rule import CONTACT_CHANNELS, ContactRule


class DailyContactCapRule(ContactRule):
    name = "Daily contact cap"

    def __init__(self, policy):
        self.cap = policy.compliance["max_contacts_per_day"]

    def check(self, action, history, case):
        if action.treatment not in CONTACT_CHANNELS:
            return self._allow()
        today = history[history["contact_datetime"].dt.date == action.planned_at.date()]
        if len(today) >= self.cap:
            return self._block(f"customer already contacted {len(today)} time(s) today (cap {self.cap})")
        return self._allow()
