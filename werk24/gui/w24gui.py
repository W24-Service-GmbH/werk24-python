import os
import asyncio
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

from werk24._version import __version__
from werk24.cli.techread import _get_drawing
from werk24.exceptions import RequestTooLargeException
from werk24.gui import event_illustrator
from werk24.gui.measure_table import W24GuiMeasureTable
from werk24.gui.event_feed import W24GuiEventFeed
from werk24.gui.style import ft_headline
from werk24.gui.worker import W24GuiWorker, W24GuiWorkerSignals
from werk24.models.ask import (W24AskCanvasThumbnail, W24AskPageThumbnail,
                               W24AskSectionalThumbnail, W24AskSheetThumbnail,
                               W24AskVariantGDTs, W24AskVariantMeasures)
from werk24.models.measure import W24Measure
from werk24.models.gdt import W24GDT
from werk24.gui.gdt_table import W24GuiGdtTable
from werk24.models.techread import (W24TechreadMessage,
                                    W24TechreadMessageSubtypeError,
                                    W24TechreadMessageSubtypeProgress,
                                    W24TechreadMessageType)
from werk24.techread_client import Hook, LicenseError, W24TechreadClient

try:
    from PyQt5.QtCore import QSize, QState, Qt, QThreadPool
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import (
        QApplication,
        QCheckBox,
        QFileDialog,
        QFrame,
        QGridLayout,
        QLabel,
        QLayout,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSpacerItem,
        QVBoxLayout,
        QWidget)
except ImportError:
    print("Using the W24GUI requires the installation of PyQt5."
          "The installer take care of this, if you call "
          "`pip install werk24[gui]`")
    sys.exit(0)


try:
    # get more meaningful segmentation fault messages
    import faulthandler
    faulthandler.enable()
except ImportError:
    pass

EXTENSIONS_SUPPORTED = ["JPG", "JPEG", "PDF", "PNG", "TIF", "TIFF"]
""" List of all the supported file extensions. """
# TODO: mid-term we want to obtain this from the API ... support will grow

# Set the windows details
try:
    import ctypes
    myappid = f"werk24.techread.gui.{__version__}"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# This will fail with either an attribute error or an import error
# depending on the operating system we are dealing with
except (AttributeError, ImportError):
    pass


class W24Gui(QMainWindow):
    """ Main GUI Class handling all the interaction
    with the user
    """

    def __init__(self) -> None:
        super().__init__()

        # start the the threadpool and the associated
        # signals to ensure that we can communciate
        # with the workers
        self.threadpool = QThreadPool()
        self.signals = W24GuiWorkerSignals()
        self.signals.result.connect(self._handle_result_signal)
        self.signals.completion.connect(self._handle_completion_signal)

        # make a list of all the asks
        # that the user can request
        self.ask_page_thumbnail = False
        self.ask_sheet_thumbnail = False
        self.ask_canvas_thumbnail = False
        self.ask_sectional_thumbnail = False
        self.ask_variant_measures = False
        self.ask_variant_gdts = False

        # make a store for sectionsals
        self.sectional_thumbnails: Dict[str, Optional[bytes]] = {}

        # and indiate the indicidual parts
        # of the GUI
        self._init_left_grid()
        self._init_right_grid()
        self._init_ui()

        # finally initiate the client
        self.init_client()

    def init_client(self) -> None:
        """ Initiate the TechreadClient from the
        environment variables.

        TODO: if we are not able to do this, we might want to
        TODO give the user a second chance an chose a  license file
        """
        try:
            self.client = W24TechreadClient.make_from_env()

            # Update the Status bar to reflect the current username
            username = self.client.username
            self.statusBar().showMessage(f"Logged in as {username}")

        # If a license error occured, let the user know.
        except LicenseError as exception:
            self._warn(f"LICENSE ERROR: {exception}")
            sys.exit()

    def _init_left_grid(self) -> None:
        """ Initiate the left grid which contains all the ASKS and
        allows the user to start the process
        """

        # STEP 1 FILENAME
        self.lb_input_file = QLabel("Input File")
        self.lb_input_file.setFont(ft_headline)

        # select the file
        self.bt_input_file = QPushButton("Select File and start")
        self.bt_input_file.clicked.connect(self.pick_input_file)

        # STEP 2: ASKS
        self.sp_asks = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.lb_asks = QLabel("Asks")
        self.lb_asks.setFont(ft_headline)

        # ASK PAGE THUMBNAIL
        self.cb_ask_page_thumbnail = QCheckBox('Page Thumbnail', self)
        self.cb_ask_page_thumbnail.stateChanged.connect(
            self._change_ask_page_thumbnail)
        self.cb_ask_page_thumbnail.toggle()

        # ASK SHEET THUMBNAIL
        self.cb_ask_sheet_thumbnail = QCheckBox('Sheet Thumbnail', self)
        self.cb_ask_sheet_thumbnail.stateChanged.connect(
            self._change_ask_sheet_thumbnail)

        # ASK CANVAS THUMBNAIL
        self.cb_ask_canvas_thumbnail = QCheckBox('Canvas Thumbnail', self)
        self.cb_ask_canvas_thumbnail.stateChanged.connect(
            self._change_ask_canvas_thumbnail)

        # ASK SECTIONAL THUMBNAIL
        self.cb_ask_sectional_thumbnail = QCheckBox(
            'Sectional Thumbnail', self)
        self.cb_ask_sectional_thumbnail.stateChanged.connect(
            self._change_ask_sectional_thumbnail)

        # ASK VARIANT MEASURES
        self.cb_ask_variant_measures = QCheckBox(
            'Variant Measures', self)
        self.cb_ask_variant_measures.stateChanged.connect(
            self._change_ask_variant_measures)

        # ASK VARIANT GDTS
        self.cb_ask_variant_gdts = QCheckBox(
            'Variant GD&Ts', self)
        self.cb_ask_variant_gdts.stateChanged.connect(
            self._change_ask_variant_gdts)

        # STEP 2: ASKS
        self.sp_start = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Make the left grid with all the checkboxes that allow
        # the user to decide what feedback they want to obtain
        self.left_grid = QVBoxLayout()
        self.left_grid.addWidget(self.lb_asks)
        self.left_grid.addWidget(self.cb_ask_page_thumbnail)
        self.left_grid.addWidget(self.cb_ask_sheet_thumbnail)
        self.left_grid.addWidget(self.cb_ask_canvas_thumbnail)
        self.left_grid.addWidget(self.cb_ask_sectional_thumbnail)
        self.left_grid.addWidget(self.cb_ask_variant_measures)
        self.left_grid.addWidget(self.cb_ask_variant_gdts)
        self.left_grid.addItem(self.sp_asks)
        self.left_grid.addWidget(self.lb_input_file)
        self.left_grid.addWidget(self.bt_input_file)
        self.left_grid.setSizeConstraint(QLayout.SetFixedSize)

        self.left_grid.setAlignment(
            Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        # Create a frame out f the left grid
        self.left_frame = QFrame()
        self.left_frame.setLayout(self.left_grid)

    def _init_right_grid(self) -> None:
        """ Initiate teh right grid that collects all
        the API responses
        """

        # make the right grid. This will be empty at
        # the start but fill up with data once we get
        # the responses
        self.api_feed = W24GuiEventFeed()

        # turn the right grid into a frame
        self.right_frame = QFrame()
        self.right_frame.resize(550, 550)
        self.right_frame.setLayout(self.api_feed)

        self.right_scroll = QScrollArea()
        self.right_scroll.setWidget(self.right_frame)
        self.right_scroll.setWidgetResizable(True)
        self.api_feed.add_welcome()

    def _init_ui(self) -> None:
        """ Initiate the main part of the GUI
        """

        # Main Grid
        self.main_grid = QGridLayout()
        self.main_grid.setColumnMinimumWidth(10, 0)
        self.main_grid.setAlignment(Qt.AlignTop)
        self.main_grid.addWidget(self.left_frame)
        self.main_grid.addWidget(self.right_scroll)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_grid)

        # Main Interface
        self.setGeometry(300, 200, 850, 450)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle('Werk24')
        self._set_window_icons()
        self.show()

    def _set_window_icons(self) -> None:
        """ Set the window icons
        """
        path_cur = os.path.dirname(os.path.abspath(__file__))
        path_img = os.path.join(path_cur, "..", "assets", "images")

        app_icon = QIcon()
        for width in [16, 24, 32, 48, 256]:
            icon_path = os.path.join(path_img, f"favicon-{width}x{width}.png")
            app_icon.addFile(icon_path, QSize(width, width))
        self.setWindowIcon(app_icon)

    def _change_ask_page_thumbnail(self, state: QState) -> None:
        self.ask_page_thumbnail = bool(state)

    def _change_ask_sheet_thumbnail(self, state: QState) -> None:
        self.ask_sheet_thumbnail = bool(state)

    def _change_ask_canvas_thumbnail(self, state: QState) -> None:
        self.ask_canvas_thumbnail = bool(state)

    def _change_ask_sectional_thumbnail(self, state: QState) -> None:
        self.ask_sectional_thumbnail = bool(state)

    def _change_ask_variant_measures(self, state: QState) -> None:
        self.ask_variant_measures = bool(state)

    def _change_ask_variant_gdts(self, state: QState) -> None:
        self.ask_variant_gdts = bool(state)

    def pick_input_file(self) -> None:
        """ Let the user chose an input file and
        start the techread process
        """

        # make a list of the supporte file extensions
        # that the user can select
        extensions = " ".join([
            f"*.{ft.lower()}"
            for ft in EXTENSIONS_SUPPORTED])

        # open the file dialog
        # NOTE: the user can only select one file!
        input_file = QFileDialog.getOpenFileName(
            self,
            'Select drawing',
            '',
            f"Technical Drawings ({extensions})")

        # ignore the picked file if it empty (e.g., when the user
        # did not end up picking a file)
        if len(input_file) < 2 or input_file[0] == '':
            return

        # disable the button to make it less likely that they
        # user starts a second parallel request
        self.bt_input_file.setEnabled(False)

        # reset the local stores
        self.sectional_thumbnails = {}

        # clear the feed and give some information that
        # we now have started processing the file in
        # question
        self.api_feed.clear()
        self.api_feed.add_line()
        self.api_feed.add_headline(f"Reading file '{input_file[0]}'")

        # otherwise we want to update the filename and start
        # the techread request
        hooks = self._make_hooks()
        worker = W24GuiWorker(
            self._start_techread_request,
            input_file[0],
            hooks)
        self.threadpool.start(worker)

    def _start_techread_request(
            self,
            input_file: str,
            hooks: List[Hook]
    ) -> None:
        """ Just a small handler to make the code more readable.
        The Client itself works in an asyncronic fashion, which
        somewhat collides with single-task workers.

        Args:
            input_file (str): Path of the input file
            hooks (List[Hook]): List of all the hooks to
                call when data becomdes availabel
        """
    
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._start_techread_request_async(input_file, hooks))
        try:
            loop.close()
        except RunTimeError:
            pass

    async def _start_techread_request_async(
            self,
            input_file: str,
            hooks: List[Hook]
    ) -> None:
        """ Star the techread request by sending the input file
        to the client. The responses will be handled by the
        associated hooks

        Args:
            input_file (str): Path of the input file
            hooks (List[Hook]): List of all the hooks to
                call when data becomdes availabel
        """

        # then start the session
        async with self.client as session:

            # and make the request
            try:
                drawing_bytes = _get_drawing(input_file)
                await session.read_drawing_with_hooks(drawing_bytes, hooks)

            except FileNotFoundError:
                self._warn("File was not found")

            except RequestTooLargeException:
                self._warn(
                    "Request was too large to be processed. " +
                    "Please check the documentation for current limits.")
                

        # finaly tell the system that the request is done
        self.signals.completion.emit()

    @staticmethod
    def _warn(message: str) -> None:
        """ Create a small warning pop up 1990s-style

        Args:
            message (str): Warning message
        """

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

    def _handle_completion_signal(
            self
    ) -> None:

        # reactivate the input button
        self.bt_input_file.setEnabled(True)

    @staticmethod
    def _handle_result_signal(
            signal: Tuple[Callable, W24TechreadMessage]
    ) -> None:
        """ Once we obtain a single, we want to collect the
        result and change the state of the GUI. The method
        waits for the signal and then executes the function
        in this thread.

        Args:
            signal (Tuple[Callable, W24TechreadMessage]):
                Signal with Callable and Message
        """
        function, message = signal
        function(message)

    def _make_hooks(self) -> List[Hook]:
        """ Make the hooks depending on the asks that
        the user has selected.

        Returns:
            List[Hook]: List of hooks with associated
                asks and functions
        """

        # tell the api what asks you are interested in,
        # and define what to do when you receive the result
        hooks = []

        config = [
            {
                'condition': self.ask_page_thumbnail,
                'ask': W24AskPageThumbnail(),
                'function': self._receive_ask_page_thumbnail
            },
            {
                'condition': self.ask_sheet_thumbnail,
                'ask': W24AskSheetThumbnail(),
                'function': self._receive_ask_sheet_thumbnail
            },
            {
                'condition': self.ask_canvas_thumbnail,
                'ask': W24AskCanvasThumbnail(),
                'function': self._receive_ask_canvas_thumbnail
            },
            {
                'condition': self.ask_sectional_thumbnail,
                'ask': W24AskSectionalThumbnail(),
                'function': self._receive_ask_sectional_thumbnail
            },
            {
                'condition': self.ask_variant_measures,
                'ask': W24AskVariantMeasures(),
                'function': self._receive_ask_variant_measures
            },
            {
                'condition': self.ask_variant_gdts,
                'ask': W24AskVariantGDTs(),
                'function': self._receive_ask_variant_gdts
            },
        ]

        # make a short closure to call the correct
        # collector functions
        def make_signal_emitter(item: Dict[str, Any]) -> Callable:
            def func(message: W24TechreadMessage) -> None:
                self.signals.result.emit((item['function'], message))
            return func

        # start with all the hooks that we have from
        # the config
        hooks = [
            Hook(ask=item['ask'], function=make_signal_emitter(item))
            for item in config
            if item['condition']]

        # add a general hook to deal with internal errors
        hooks += [
            Hook(
                message_type=W24TechreadMessageType.ERROR,
                message_subtype=W24TechreadMessageSubtypeError.INTERNAL,
                function=self._receive_error)]

        # add a gneral hook to deal with PROGRESS messages
        hooks += [
            Hook(
                message_type=W24TechreadMessageType.PROGRESS,
                message_subtype=W24TechreadMessageSubtypeProgress.STARTED,
                function=self._receive_progress_started)]

        return hooks

    def _receive_ask_page_thumbnail(
            self,
            message: W24TechreadMessage
    ) -> None:
        """Handle incoming Page Thumbnails

        Args:
            message (W24TechreadMessage): Message with the
                Page Thumbnail
        """
        self.api_feed.add_headline("Page Thumbnail")
        self.api_feed.add_image(message.payload_bytes)
        message.payload_bytes = b"--- binary --"
        self.api_feed.add_json(message.json())
        self.api_feed.add_line()

    def _receive_ask_sheet_thumbnail(
            self,
            message: W24TechreadMessage
    ) -> None:
        """Handle incoming Sheet Thumbnails

        Args:
            message (W24TechreadMessage): Message with the
                Sheet Thumbnail
        """
        self.api_feed.add_headline("Sheet Thumbnail")
        self.api_feed.add_image(message.payload_bytes)
        message.payload_bytes = b"--- binary --"
        self.api_feed.add_json(message.json())
        self.api_feed.add_line()

    def _receive_ask_canvas_thumbnail(
            self,
            message: W24TechreadMessage
    ) -> None:
        """Handle incoming Canvas Thumbnails

        Args:
            message (W24TechreadMessage): Message with the
                Canvas Thumbnail
        """
        self.api_feed.add_headline("Canvas Thumbnail")
        self.api_feed.add_image(message.payload_bytes)
        message.payload_bytes = b"--- binary --"
        self.api_feed.add_json(message.json())
        self.api_feed.add_line()

    def _receive_ask_sectional_thumbnail(
            self,
            message: W24TechreadMessage
    ) -> None:
        """Handle incoming Sectional Thumbnails

        Args:
            message (W24TechreadMessage): Message with the
                Sectional Thumbnail
        """
        self.api_feed.add_headline("Sectional Thumbnail")
        self.api_feed.add_image(message.payload_bytes)

        # store the sectional locally so that we can
        # reuse the image when drawing the measures
        # and gd&ts
        if message.payload_dict is None:
            return

        # write it into the local store
        sectional_id = message.payload_dict.get('sectional_id')
        if sectional_id is not None:
            self.sectional_thumbnails[sectional_id] = message.payload_bytes

        # after we stored it..., censor and print
        message.payload_bytes = b"--- binary --"
        self.api_feed.add_json(message.json())
        self.api_feed.add_line()

    def _receive_ask_variant_measures(
            self,
            message: W24TechreadMessage
    ) -> None:
        """Handle incoming Variant Measures

        Args:
            message (W24TechreadMessage): Message with the
                Variant Measures
        """
        self.api_feed.add_headline("Variant Measures")
        self.api_feed.add_json(message.json())

        # check whether we have an stored version of the sectional
        if message.payload_dict is None:
            return

        sectional_id = message.payload_dict.get('sectional_id')
        if sectional_id is None:
            return

        # now get the measure list from the payload and stop
        # the execution if the payload is None
        measure_list_raw = message.payload_dict.get('measures')
        if measure_list_raw is None or not measure_list_raw:
            return

        # if we have a payload, translate it into usable objects
        measure_list = [W24Measure.parse_obj(m) for m in measure_list_raw]

        # if we really have sectional_bytes and measures, illustrate
        # the results
        sectional_bytes = self.sectional_thumbnails.get(sectional_id)
        if sectional_bytes is not None:
            sectional_bytes_w_measures = event_illustrator\
                .illustrate_sectional_measures(sectional_bytes, measure_list)
            self.api_feed.add_image(sectional_bytes_w_measures)

        # add the table for the measures
        measure_table = W24GuiMeasureTable.from_measure_list(measure_list)
        self.api_feed.add_table(measure_table)
        self.api_feed.add_line()

    def _receive_ask_variant_gdts(
            self,
            message: W24TechreadMessage
    ) -> None:
        """ Handle incoming Variant GD&Ts

        Args:
            message (W24TechreadMessage): Message with the
                Variant GD&Ts
        """
        self.api_feed.add_headline("Variant GD&Ts")
        self.api_feed.add_json(message.json())

        # check whether we have an stored version of the sectional
        if message.payload_dict is None:
            return

        sectional_id = message.payload_dict.get('sectional_id')
        if sectional_id is None:
            return

        # now get the measure list from the payload and stop
        # the execution if the payload is None
        gdt_list_raw = message.payload_dict.get('gdts')
        if gdt_list_raw is None or not gdt_list_raw:
            return

        # if we have a payload, translate it into usable objects
        gdt_list = [W24GDT.parse_obj(m) for m in gdt_list_raw]
        sectional_bytes = self.sectional_thumbnails.get(sectional_id)
        if sectional_bytes is not None:
            sectional_bytes_w_measures = event_illustrator.\
                illustrate_sectional_gdts(
                    sectional_bytes, gdt_list)
            self.api_feed.add_image(sectional_bytes_w_measures)

        # add the table for the measures
        measure_table = W24GuiGdtTable.from_gdt_list(gdt_list)
        self.api_feed.add_table(measure_table)
        self.api_feed.add_line()

    def _receive_error(
            self,
            message: W24TechreadMessage
    ) -> None:
        """ Handle Incomeing errors

        Args:
            message (W24TechreadMessage): Message with the
                Error message
        """
        self.api_feed.add_headline("ERROR")
        self.api_feed.add_json(message.json())
        self.api_feed.add_line()

    def _receive_progress_started(
            self,
            message: W24TechreadMessage
    ) -> None:
        """ Handle Incomeing errors

        Args:
            message (W24TechreadMessage): Message with the
                Progress Message
        """
        self.api_feed.add_headline("Progress")
        self.api_feed.add_json(message.json())
        self.api_feed.add_line()


def main() -> None:
    app = QApplication(sys.argv)

    # Dear Garbadge collector,
    # We are truely grateful for your work.
    # Please do not collect this object though.
    # We still need it.
    # Sincerely yours,
    # Dr. Jay
    _ = W24Gui()

    # run
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
