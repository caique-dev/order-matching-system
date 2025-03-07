class Utilities:
    output_icon = '>> '

    @staticmethod
    def toggle_out_icon():
        """
        Change the output message icon according the trades state  
        """
        Utilities.output_icon = '>> ' if ('==' in Utilities.output_icon) else ('== ')

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
    def print_message(msg: str):
        """
        Prints a message in a standardized way.
        """
        print(Utilities.output_icon + msg)
