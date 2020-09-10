from typing import List, Callable, Dict
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QRect
from werk24.models.measure import W24Measure


class W24GuiMeasureTable(QTableWidget):

    @classmethod
    def from_measure_list(
            cls,
            measure_list: List[W24Measure]
    ) -> 'W24GuiMeasureTable':

        # make a simple config file for the current table
        config: Dict[str, Callable] = {
            "Blurb": cls._format_measure_blurb,
            "Quantity": cls._format_measure_quantity,
            "Size": cls._format_measure_size,
            "Tolerance": cls._format_measure_tolerance,
            "Thread": cls._format_measure_thread,
            "Chamfer": cls._format_measure_chamfer,
            "Start": cls._format_measure_start,
            "Stop": cls._format_measure_stop,
            "Confidence": cls._format_measure_confidence
        }

        # make the associated table
        table_widget = W24GuiMeasureTable()
        table_widget.setColumnCount(len(config))
        table_widget.setRowCount(len(measure_list))
        table_widget.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)

        # make the table content
        table_widget.setHorizontalHeaderLabels(config.keys())
        for i, cur_measure in enumerate(measure_list):
            for j, callable_ in enumerate(config.values()):
                content = callable_(cur_measure)
                table_widget.setItem(i, j, QTableWidgetItem(content))
            table_widget.resizeColumnToContents(i)

        table_widget.setGeometry(0, 0, 200, 200)
        table_widget.resizeRowsToContents()
        return table_widget

    @staticmethod
    def _format_measure_confidence(measure: W24Measure) -> str:
        return f"{measure.confidence}"

    @staticmethod
    def _format_measure_blurb(measure: W24Measure) -> str:
        return f"{measure.label.blurb}"

    @staticmethod
    def _format_measure_quantity(measure: W24Measure) -> str:
        return f"{measure.label.quantity}"

    @staticmethod
    def _format_measure_size(measure: W24Measure) -> str:
        return f"{measure.label.size.blurb}"

    @staticmethod
    def _format_measure_tolerance(measure: W24Measure) -> str:
        return "" if measure.label.size_tolerance is None \
            else f"{measure.label.size_tolerance.blurb}"

    @staticmethod
    def _format_measure_thread(measure: W24Measure) -> str:
        return "" if measure.label.thread is None \
            else f"{measure.label.thread.blurb}"

    @staticmethod
    def _format_measure_chamfer(measure: W24Measure) -> str:
        return "" if measure.label.chamfer is None \
            else f"{measure.label.chamfer.blurb}"

    @staticmethod
    def _format_measure_start(measure: W24Measure) -> str:
        return f"{measure.line[0][0]:.4f} x {measure.line[0][1]:.4f}"

    @staticmethod
    def _format_measure_stop(measure: W24Measure) -> str:
        return f"{measure.line[1][0]:.4f} x {measure.line[1][1]:.4f}"
