class TerytNotFound(Exception):
    """
    Raises when Teryt from params is not matched with external table data
    """
    pass


class EmapaServiceNotFound(Exception):
    """
    Raises when e.g commune use different addresses system (e.g. geoportal)
    """
    pass
