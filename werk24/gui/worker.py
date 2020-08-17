
from typing import List, Dict, Any, Callable

from PyQt5.QtCore import (QObject, QRunnable, pyqtSlot, pyqtSignal)


class W24GuiWorker(QRunnable):
    """ Small worker class to execute non-blocking calls in
    the background. Used to call the API while keeping the
    GUI responsive
    """

    def __init__(
            self,
            function: Callable,
            *args: List[Any],
            **kwargs: Dict[Any, Any]
    ) -> None:
        """ Initiate a new 'thread' that calls
        function when run() is executed

        Args:
            function: funcation to be called
        """
        super(W24GuiWorker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()  # type: ignore # There is little we can do about that
    def run(self) -> None:
        """
        Run the predefined fucntion
        """
        if self.function is not None:
            self.function(*self.args, **self.kwargs)


class W24GuiWorkerSignals(QObject):
    """ Defines the signals available from a running worker thread.
    """
    result = pyqtSignal(object)
    completion = pyqtSignal()
