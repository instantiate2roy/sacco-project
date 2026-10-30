class DisplayError(Exception):
    """
    A list or grid can't be built, e.g. a filter refers to a column that doesn't exist.
    """
