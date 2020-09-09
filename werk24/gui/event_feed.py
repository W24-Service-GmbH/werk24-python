import os
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (QFrame, QGridLayout, QLabel, QTableWidget,
                             QVBoxLayout)
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
        path_cur = os.path.dirname(os.path.abspath(__file__))
        path_logo = os.path.join(
            path_cur,
            "..",
            "assets",
            "images",
            "logo-625.png")

        qimage = QImage(path_logo)
        pixmap = QPixmap(qimage)
        pixmap_label = QLabel()
        pixmap_label.setPixmap(pixmap)

        grid = QVBoxLayout()
        grid.addWidget(pixmap_label)
        grid.addWidget(
            QLabel("Thank you for using W24 Services.\n"
                   "STEP 1: Use the checkboxes on the left to decide "
                   "which asks you want to submit to the API.\n"
                   "STEP 2: Pick the file you want to analyse"))
        self.addStretch(1)

        frame = QFrame()
        frame.setLayout(grid)
        self.addWidget(frame)

    def clear(self) -> None:
        """ Remove all widgets in the event feed
        """
        # for i in reversed(range(self.count())):
        #     try:
        #         print(type(self.itemAt(i).widget()))
        #         #self.itemAt(i).widget().setParent(None)
        #         self.removeWidget(self.itemAt(i).widget())
        #     except AttributeError:
        #         pass
        # print("AS")
        pass

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

    def add_table(
            self,
            table: QTableWidget
    ) -> None:
        """ Add a table to the feed.
        This would probably be a result table for the measures,
        the gd&ts or any future features

        Args:
            table (QTableWidget): Table in question
        """
        self.addWidget(table)

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
