class WindowByTitleNotFound(Exception):
    """Exception raised when a window cannot be found by title."""
    pass


class IncorrectWindowInitialization(Exception):
    pass


class WindowSuchHwndDoesNotExist(Exception):
    pass


class DisplayMonitorEnumerationError(Exception):
    def __init__(self, message="Error while enumerating display monitors"):
        self.message = message
        super().__init__(self.message)
