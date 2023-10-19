import os
import sys

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg

from models.signal import Signal
from models.sampler import Sampler

from helpers.get_signal_from_file import get_signal_from_file


import csv
import numpy as np

mainwindow_ui_file_path = os.path.join(os.path.dirname(__file__), 'views', 'mainwindow.ui')
uiclass, baseclass = pg.Qt.loadUiType(mainwindow_ui_file_path)

# TODO: Change this later
MAX_F_SAMPLING = 500

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Sampling Theory Studio")

        # Initialize UI state
        self.sampling_curve = None
        self.sampling_freq_slider.setMinimum(0)
        self.sampling_freq_slider.setMaximum(MAX_F_SAMPLING)
        
        # Connecting UI controls to events
        self._initialize_signals_slots()


    def _initialize_signals_slots(self):
       # Menu items - File
       self.actionOpen_Signal.triggered.connect(self._open_signal_file)
       self.sampling_freq_slider.valueChanged.connect(self._resample)

    def _open_signal_file(self):
        signal: Signal = get_signal_from_file(self)
        
        self.original_signal_graph.setXRange(0, 1)

        # Render the CONTINUOUS signal
        pen_c = pg.mkPen(color=(255, 255, 255))
        self.original_signal_graph.plot(signal.x_vec, signal.y_vec, pen=pen_c)

        # Render the DISCRETE signal
        self.sampler = Sampler(signal)
        self._resample(MAX_F_SAMPLING)

    def _resample(self, f_sampling) -> None:
        if self.sampling_curve is not None:
            self.original_signal_graph.removeItem(self.sampling_curve)

        if f_sampling > 0:
          sampled_signal = self.sampler.sample(f_sampling)
          self.sampling_curve = self.original_signal_graph.plot(
              sampled_signal.x_vec, 
              sampled_signal.y_vec, 
              pen=None, symbol='x', 
              symbolPen=None, 
              symbolBrush=pg.mkBrush(255, 0, 0, 255)
          )

        self.sampling_freq_label.setText(f"{f_sampling}HZ")
        self.sampling_freq_label.repaint()
        self.sampling_freq_slider.setValue(f_sampling)
        self.sampling_freq_slider.repaint()

        
            

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
