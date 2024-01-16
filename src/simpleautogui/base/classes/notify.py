class Notify:
    def __init__(self):
        pass

    @staticmethod
    def confirm(msg: str) -> bool:
        """
        Displays an error dialog and asks the user whether to continue after this error.

        :param msg: The error message to display.
        :return: True if the user chooses to continue the search, False otherwise.
        """
        from pymsgbox import confirm
        result = confirm(msg, 'Confirmation', ('Continue ', 'Stop'))
        return result == 'Continue'
