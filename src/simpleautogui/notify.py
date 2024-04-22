from pymsgbox import confirm


class Notify:
    def __init__(self):
        pass

    @staticmethod
    def continueOrStop(msg: str) -> bool:
        """
        Stops code execution and prompts the user to either stop execution or continue.

        :param msg: The error message to display.
        :return: True if the user chooses to continue the search, False otherwise.
        """
        result = confirm(msg, 'Confirmation', ('Continue ', 'Stop'))
        return result == 'Continue'
