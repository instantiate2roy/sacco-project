from .channel_rule import _ChannelRule


class MinimumGapRule(_ChannelRule):
    name = "Minimum gap"

    def check(self, action, history, case):
        if action.treatment not in self.limits:
            return self._allow()
        previous = self._same_channel(action, history)
        if previous.empty:
            return self._allow()
        gap = (action.planned_at - previous["contact_datetime"].max()).total_seconds() / 3600
        needed = self.limits[action.treatment]["min_gap_hours"]
        if gap < needed:
            return self._block(f"last {action.treatment} was {gap:.1f} hours ago (minimum {needed})")
        return self._allow()
