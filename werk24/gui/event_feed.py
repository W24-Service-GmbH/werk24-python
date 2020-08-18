from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QFrame
# from werk24.gui.json_editor import W24GuiJsonEditor
from werk24.gui.style import ft_headline


class QHLine(QFrame):
    def __init__(self) -> None:
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class W24GuiEventFeed(QVBoxLayout):
    """ API Event feed listing all the
    responses that we obtained from the
    API
    """

    def add_welcome(self) -> None:
        """ Add a welcome message that is shown to the
        user before they submitted the first request
        """

        qimage = QImage("assets/logo-625.png")
        pixmap = QPixmap(qimage)
        pixmap_label = QLabel()
        pixmap_label.setPixmap(pixmap)

        grid = QGridLayout()
        grid.setColumnMinimumWidth(10, 0)
        grid.setAlignment(Qt.AlignTop)
        # grid.addWidget(pixmap_label, 1, 1, 3, 3)

        grid.addWidget(QLabel(""), 0, 0)
        grid.addWidget(QLabel(""), 0, 1)
        grid.addWidget(QLabel(""), 0, 2)
        grid.addWidget(QLabel(""), 1, 0)
        grid.addWidget(pixmap_label, 1, 1)
        grid.addWidget(QLabel(""), 1, 2)
        grid.addWidget(QLabel(""), 2, 0)
        grid.addWidget(
            QLabel("Thank you for using the W24 Services.\n "
                   "STEP 1: Use the checkboxes on the left to decide "
                   "which asks you want to submit to the API.\n"
                   "STEP 2: Pick the file you want to analyse "),
            2,
            1)
        grid.addWidget(QLabel(""), 2, 2)

        frame = QFrame()
        frame.setLayout(grid)
        self.addWidget(frame)

    def clear(self) -> None:
        """ Remove all widgets in the event feed
        """
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().setParent(None)

    def add_json(
            self,
            json: str
    ) -> None:
        """ Add a JSON string to the feed

        Args:
            json (str): Json as string
        """
        text = QLabel(json)
        # json_editor = W24GuiJsonEditor()
        # json_editor.setText(json)
        self.addWidget(text)

    def add_headline(
            self,
            headline: str
    ) -> None:
        """ ADd a headline to the feed

        Args:
            headline (str): Headline as string
        """
        lb_headline = QLabel(headline)
        lb_headline.setFont(ft_headline)
        self.addWidget(lb_headline)

    def add_image(
            self,
            payload_bytes: Optional[bytes]
    ) -> None:
        """ Add an image to the feed

        Args:
            payload_bytes (Optional[bytes]): image in bytes
        """

        # if the payload is None, thre is no point
        if not payload_bytes:
            return

        # otherwise load the image
        qimage = QImage()
        qimage.loadFromData(payload_bytes)

        # rescale it
        pixmap = QPixmap(qimage)
        # pixmap = pixmap.scaled(1024, 1024, Qt.KeepAspectRatio)

        # turn it into a label
        pixmap_label = QLabel()
        pixmap_label.setPixmap(pixmap)

        # and add
        self.addWidget(pixmap_label)

    def add_line(
            self
    ) -> None:
        """ Add a simple separation line
        """
        self.addWidget(QHLine())
