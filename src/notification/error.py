class NotificationError(Exception):
    """
    A message can't be written, e.g. a channel with no message template or a case that isn't in the portfolio.
    """    