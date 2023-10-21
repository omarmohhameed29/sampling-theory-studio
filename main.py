import os
import sys

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSlot
import pyqtgraph as pg

from models.signal import Signal
from models.sampler import Sampler
from models.reconstructor import Reconstructor
from create_signal import CreateSignalWindow

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
        self.reconstructed_signal: Signal
        self.error_signal: Signal
        self.sampling_curve = None
        self.reconstruct_curve = None
        self.error_curve = None
        self.f_sampling = 150 # Initial f_sampling, can't be = zero (VIMP) to avoid logical and mathematical errors.
        self.sampling_freq_slider.setMinimum(0)
        self.sampling_freq_slider.setMaximum(MAX_F_SAMPLING)
        self.num_of_signals = 0 # Calculate number of graphs to prevent slider error when no graph displayed
        # self.original_signal_graph.setXRange(0, 1)
        # self.reconstructed_signal_graph.setXRange(0, 1)

        # Connecting UI controls to events
        self._initialize_signals_slots()

    def _initialize_signals_slots(self):
        # Menu items - File
        self.actionOpen_Signal.triggered.connect(self._open_signal_file)
        self.sampling_freq_slider.valueChanged.connect(self._on_slider_change)
        self.actionComposer.triggered.connect(self.open_composer)


    def open_composer(self):
        # Initialize the create_signal_window attribute
        self.create_signal_window = CreateSignalWindow()

        # Connect the signal_saved signal from the create_signal window to the render_composer_signal method
        self.create_signal_window.signal_saved.connect(self.render_composer_signal)

        # Connect the window_closed signal from the create_signal window to the close_create_signal_window method
        self.create_signal_window.window_closed.connect(self.close_create_signal_window)

        # Show the create_signal window
        self.create_signal_window.show()
        self.num_of_signals += 1

    @pyqtSlot(Signal)
    def render_composer_signal(self, signal):
        # Render the CONTINUOUS signal
        pen_c = pg.mkPen(color=(255, 255, 255))
        self.original_signal_graph.plot(signal.x_vec, signal.y_vec, pen=pen_c)

        self.signal = signal

        # self._render_signal()  ---> This is causing an error
    @pyqtSlot()
    def close_create_signal_window(self):
        # Close the create_signal window
        self.create_signal_window.close()


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
        if self.num_of_signals > 0:
            self.f_sampling = value
            self._render_signal()

    def _render_signal(self):
        self.num_of_signals += 1
        self._resample()
        self._reconstruct()
        # self._display_error_signal()

    def _resample(self) -> None:
        self.sampler = Sampler(self.signal)
        if self.sampling_curve is not None:
            self.original_signal_graph.removeItem(self.sampling_curve)

        if self.f_sampling > 0:
            self.sampled_signal = self.sampler.sample(self.f_sampling)
            # Render the sampled points on original signal
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
        self.reconstructed_signal = reconstructor.reconstruct(t, self.f_sampling)

        # Render the RECONSTRUCTED signal
        pen_r = pg.mkPen(color=(0, 255, 0))
        if self.reconstruct_curve is not None:
            self.reconstructed_signal_graph.removeItem(self.reconstruct_curve)
        self.reconstruct_curve = self.reconstructed_signal_graph.plot(self.reconstructed_signal.x_vec,
                                                                      self.reconstructed_signal.y_vec, pen=pen_r)

    def _display_error_signal(self):
        # calculate difference between original signal and reconstructed signal
        y_vec_error = np.abs(self.signal.y_vec - self.reconstructed_signal.y_vec)

        # Render error signal
        pen_b = pg.mkPen(color=(0, 0, 255))
        if self.error_curve is not None:
            self.error_signal_graph.removeItem(self.error_curve)
        self.error_curve = self.error_signal_graph.plot(self.signal.x_vec, y_vec_error, pen=pen_b)

    def add_gaussian_noise(self):
        # todo Noise should be inserted by the user as SNR then calculate its amplitude
        noise_amplitude = 0.1  # Adjust this value to control the noise level
        noise = np.random.normal(0, noise_amplitude, len(self.signal.x_vec))

        # Add Noise to original signal
        self.signal.y_vec += noise

        # Render signal after Noise addition
        self._render_signal()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
