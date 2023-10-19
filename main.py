import os
import sys

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg


mainwindow_ui_file_path = os.path.join(os.path.dirname(__file__), 'views', 'mainwindow.ui')
uiclass, baseclass = pg.Qt.loadUiType(mainwindow_ui_file_path)

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Sampling Theory Studio")

        # Connecting UI controls to events
        self._initialize_signals_slots()


    def _initialize_signals_slots(self):
       ...


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
