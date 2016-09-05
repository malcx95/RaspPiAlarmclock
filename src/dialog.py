import threading

OK_OPTION = 'OK'
YES_OPTION = 'Yes'
NO_OPTION = 'No'
CANCEL_OPTION = 'Cancel'

class Dialog(object):
    """
    Generic dialog class.
    """

    # TODO Currently not usable

    def __init__(self, message, options):
        self.options = options
        self.message = message
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()

    def show_dialog(self):
        """
        Shows the dialog and returns the result.
        """
        # TODO do something
        return self._show()

    def stop(self):
        # TODO remove used buttons
        self._stop_flag.set()

    def _show(self):
        raise NotImplementedError('Show must be implemented')


class MessageDialog(Dialog):
    
    def __init__(self, message):
        super(self.__class__, self).__init__(message, [OK_OPTION])

    def _show(self):
        # TODO implement
        pass
    

class QuestionDialog(self):
    """
    Yes/No/Cancel type dialog
    """
    OK_CANCEL = 0
    YES_NO = 1
    YES_NO_CANCEL = 2

    def __init__(self, question, option_type):
        if option_type == OK_CANCEL:
            options = [OK_OPTION, CANCEL_OPTION]
        elif option_type == YES_NO:
            options = [YES_OPTION, NO_OPTION]
        elif option_type == YES_NO_CANCEL:
            options = [YES_OPTION, NO_OPTION, CANCEL_OPTION]
        else:
            raise ValueError
        super(self.__class__, self).__init__(question, options)

    def _show(self):
        # TODO implement
        pass
