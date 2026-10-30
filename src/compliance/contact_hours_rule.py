from .contact_rule import CONTACT_CHANNELS, ContactRule


class ContactHoursRule(ContactRule):
    name = "Contact hours"

    def __init__(self, policy):
        hours = policy.compliance["contact_hours"]
        self.start, self.end, self.days = hours["start"], hours["end"], set(hours["days"])

    def check(self, action, history, case):
        if action.treatment not in CONTACT_CHANNELS:
            return self._allow()
        when = action.planned_at
        if when.strftime("%a") not in self.days:
            return self._block(f"{when:%A} is not a contact day")
        if not self.start <= when.strftime("%H:%M") < self.end:
            return self._block(f"{when:%H:%M} is outside {self.start}-{self.end}")
        return self._allow()
