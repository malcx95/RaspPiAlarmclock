import threading

class Dialog(object):
    """
    Generic dialog class.
    """

    # TODO Currently not usable

    def __init__(self, options):
        self.options = options
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()

    def show_dialog(self):
        # TODO do something
        return self._show()

    def stop(self):
        # TODO remove used buttons
        self._stop_flag.set()

    def _show(self):
        raise NotImplementedError('Show must be implemented')


class MessageDialog(Dialog):
    
    def __init__(self):
        # TODO implement
        pass

    def _show(self):
        # TODO implement
        pass
    

class QuestionDialog(self):
    """
    Yes/No/Cancel type dialog
    """

    def __init__(self):
        # TODO implement
        pass

    def _show(self):
        # TODO implement
        pass
