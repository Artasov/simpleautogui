from pymsgbox import confirm


class Notify:
    @staticmethod
    def continue_or_stop(msg: str) -> bool:
        """
        Stops code execution and prompts the user to either stop execution or continue.

        :param msg: The error message to display.
        :return: True if the user chooses to continue the search, False otherwise.
        """
        result = confirm(msg, 'Confirmation', ('Continue', 'Stop'))
        return result == 'Continue'
