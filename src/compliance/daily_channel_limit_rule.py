from .channel_rule import _ChannelRule


class DailyChannelLimitRule(_ChannelRule):
    name = "Daily channel limit"

    def check(self, action, history, case):
        if action.treatment not in self.limits:
            return self._allow()
        today = self._same_channel(action, history)
        today = today[today["contact_datetime"].dt.date == action.planned_at.date()]
        limit = self.limits[action.treatment]["max_per_day"]
        if len(today) >= limit:
            return self._block(f"{action.treatment} already used {len(today)} time(s) today (limit {limit})")
        return self._allow()
