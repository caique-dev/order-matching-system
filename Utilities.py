class Utilities:
    @staticmethod
    def print_error(msg: str):
        """
        Prints a error message in a standardized way.
        """
        Utilities.print_message('Error: ' + msg)

    @staticmethod
    def get_input(msg: str = ''):
        """
        Prints a message in a standardized way to get the user input.
        """
        if not (msg):
            return input('<< ' + msg)

        return input('<< ' + msg + ': ')

    @staticmethod
    def print_message(trades_state: bool, msg: str):
        """
        Prints a message in a standardized way.
        """
        msg_icon = '>> ' if trades_state else '== '
        print(msg_icon + msg)
