class ExportError(Exception):
    """
    A dashboard view can't be exported, e.g. an unsupported format or an export folder that can't be created.
    """
