from datetime import timedelta

from .channel_rule import _ChannelRule


class WeeklyChannelLimitRule(_ChannelRule):
    name = "Weekly channel limit"

    def check(self, action, history, case):
        if action.treatment not in self.limits:
            return self._allow()
        week = self._same_channel(action, history)
        week = week[week["contact_datetime"] > action.planned_at - timedelta(days=7)]
        limit = self.limits[action.treatment]["max_per_week"]
        if len(week) >= limit:
            return self._block(f"{action.treatment} used {len(week)} times in 7 days (limit {limit})")
        return self._allow()
