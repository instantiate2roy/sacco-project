class ModelError(Exception):
    """
    A risk model can't be trained, used or loaded, e.g. it hasn't been trained yet.
    """