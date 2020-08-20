from typing import List, Callable, Dict
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QRect
from werk24.models.gdt import W24GDT


class W24GuiGdtTable(QTableWidget):

    @classmethod
    def from_gdt_list(
            cls,
            measure_list: List[W24GDT]
    ) -> 'W24GuiGdtTable':

        # make a simple config file for the current table
        config: Dict[str, Callable] = {
            "Polygon": cls._format_gdt_polygon,
            "Blurb": cls._format_gdt_blurb,
        }

        # make the associated table
        table_widget = W24GuiGdtTable()
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
    def _format_gdt_blurb(gdt: W24GDT) -> str:
        return f"{gdt.frame.blurb}"

    @staticmethod
    def _format_gdt_polygon(gdt: W24GDT) -> str:
        return " - ".join([
            f"{pt[0]:.4f} x {pt[1]:.4f}"
            for pt in gdt.bounding_polygon])
