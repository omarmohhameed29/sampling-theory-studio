import os
import sys

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg

from models.signal import Signal
from models.sampler import Sampler
from models.reconstructor import Reconstructor

from helpers.get_signal_from_file import get_signal_from_file
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
        self.sampled_signal: Signal
        self.sampling_curve = None
        self.reconstruct_curve = None
        self.f_sampling = int(MAX_F_SAMPLING/2)
        self.sampling_freq_slider.setMinimum(0)
        self.sampling_freq_slider.setMaximum(MAX_F_SAMPLING)
        self.original_signal_graph.setXRange(0, 1)
        self.reconstructed_signal_graph.setXRange(0, 1)
        
        # Connecting UI controls to events
        self._initialize_signals_slots()


    def _initialize_signals_slots(self):
       # Menu items - File
       self.actionOpen_Signal.triggered.connect(self._open_signal_file)
       self.sampling_freq_slider.valueChanged.connect(self._on_slider_change)

    def _open_signal_file(self):
        # self.signal: Signal = get_signal_from_file(self)

        # Create a cos wave signal for testing
        sin_freq_hz = 20
        t = np.linspace(0, 1, 1000)
        y = np.cos(2 * np.pi * sin_freq_hz * t)
        self.signal = Signal(t, y)

        # Render the CONTINUOUS signal
        pen_c = pg.mkPen(color=(255, 255, 255))
        self.original_signal_graph.plot(self.signal.x_vec, self.signal.y_vec, pen=pen_c)

        self._render_signal()

    def _on_slider_change(self, value): 
        self.f_sampling = value
        self._render_signal()

    def _render_signal(self):
        self._resample()
        self._reconstruct()

    def _resample(self) -> None:
        self.sampler = Sampler(self.signal)
        if self.sampling_curve is not None:
            self.original_signal_graph.removeItem(self.sampling_curve)
        
        if self.f_sampling > 0:
            self.sampled_signal = self.sampler.sample(self.f_sampling)
            # Render the sampled points on origianl signal
            self.sampling_curve = self.original_signal_graph.plot(
                self.sampled_signal.x_vec, 
                self.sampled_signal.y_vec, 
                pen=None, symbol='x', 
                symbolPen=None, 
                symbolBrush=pg.mkBrush(255, 0, 0, 255)
          )

        self.sampling_freq_label.setText(f"{self.f_sampling}HZ")
        self.sampling_freq_label.repaint()
        self.sampling_freq_slider.setValue(self.f_sampling)
        self.sampling_freq_slider.repaint()


    def _reconstruct(self):
        # Reconstruct Signal
        reconstructor = Reconstructor(self.sampled_signal)
        t = np.linspace(self.signal.x_vec[0], self.signal.x_vec[-1], 1000)
        reconstructed_signal = reconstructor.reconstruct(t, self.f_sampling)

        # Render the RECONSTRUCTED signal
        pen_r = pg.mkPen(color=(0, 255, 0))
        if self.reconstruct_curve is not None:
            self.reconstructed_signal_graph.removeItem(self.reconstruct_curve)
        self.reconstruct_curve = self.reconstructed_signal_graph.plot(reconstructed_signal.x_vec, reconstructed_signal.y_vec, pen=pen_r)


        
            

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
