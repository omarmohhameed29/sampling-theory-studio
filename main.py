import os
import sys
import copy
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSlot
import pyqtgraph as pg
import math
from models.signal import Signal
from models.sampler import Sampler
from models.reconstructor import Reconstructor
from create_signal import CreateSignalWindow

from helpers.get_signal_from_file import get_signal_from_file
import numpy as np

mainwindow_ui_file_path = os.path.join(os.path.dirname(__file__), 'views', 'mainwindow.ui')
uiclass, baseclass = pg.Qt.loadUiType(mainwindow_ui_file_path)

MAX_F_SAMPLING = 1000


class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Sampling Theory Studio")

        self._reset()

        # Connecting UI controls to events
        self.error_signal_graph.setYRange(0,5)
        self._initialize_signals_slots()

    def _initialize_signals_slots(self):
        # Menu items - File
        self.actionOpen_Signal.triggered.connect(self._open_signal_file)
        self.sampling_freq_slider.valueChanged.connect(self._on_freq_slider_change)
        self.snr_slider.valueChanged.connect(self._on_snr_slider_change)
        self.actionComposer.triggered.connect(self.open_composer)
        self.clear_button.clicked.connect(self._clear_signal)
        self.clear_button.hide()
        self.actionClear_signal.triggered.connect(self._clear_signal)
        self.freq_plus_button.clicked.connect(self._add_freq_unit)
        self.freq_minus_button.clicked.connect(self._sub_freq_unit)
        self.actionExit.triggered.connect(self._close_app)
        self.actionControls_Panel.triggered.connect(self.hide_controls)
        # self.fmax_button.clicked.connect(self._double_fsampling)
        self.x1_fm_button.clicked.connect(lambda _ : self._setFsToMultiplesFm(1))
        self.x2_fm_button.clicked.connect(lambda _ : self._setFsToMultiplesFm(2))
        self.x3_fm_button.clicked.connect(lambda _ : self._setFsToMultiplesFm(3))
        self.x4_fm_button.clicked.connect(lambda _ : self._setFsToMultiplesFm(4))

    def hide_controls(self):
         if self.frame.isHidden():
            self.frame.show()
         else:
            self.frame.hide()
    def _close_app(self) -> None:
        QApplication.quit()

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
        self._reset()
        # Render the CONTINUOUS signal
        pen_c = pg.mkPen(color=(255, 255, 255))
        self.original_signal_graph.plot(signal.x_vec, signal.y_vec, pen=pen_c)

        self.signal = signal
        self.original_signal = copy.deepcopy(self.signal)
        # self.f_sampling = 2 * self.signal.get_max_freq()
        x_range_lower = 0
        x_range_upper = self.original_signal.x_vec[-1]/25
        self.original_signal_graph.setXRange(x_range_lower, x_range_upper)
        self.reconstructed_signal_graph.setXRange(x_range_lower, x_range_upper)
        self.error_signal_graph.setXRange(x_range_lower, x_range_upper)

        self.original_signal_graph.setYRange(np.min(self.original_signal.y_vec), np.max(self.original_signal.y_vec))
        # self.original_signal_graph.setYRange(-1.5,1.5)
        

        self._render_signal()

    @pyqtSlot()
    def close_create_signal_window(self):
        # Close the create_signal window
        self.create_signal_window.close()

    def _open_signal_file(self):
        try:
            self._reset()
            self.imported = True
            self.signal: Signal = get_signal_from_file(self)
            self.original_signal = copy.deepcopy(self.signal)
            # Render the CONTINUOUS signal
            pen_c = pg.mkPen(color=(255, 255, 255))
            self.original_signal_graph.plot(self.signal.x_vec, self.signal.y_vec, pen=pen_c)

            # Set viewport limits
            self.original_signal_graph.setXRange(0,2.8)
            self.reconstructed_signal_graph.setXRange(0,2.8)
            self.error_signal_graph.setXRange(0,2.8)
            self.original_signal_graph.setYRange(-1,-0.1)
            self.reconstructed_signal_graph.setYRange(-1,-0.1)
            # self.f_sampling = 2 * self.signal.get_max_freq()
            # self.f_sampling = self.signal.get_max_freq_open_signal()
            self._render_signal()
        except Exception as e:
            pass


    def _on_freq_slider_change(self, value):
        if self.num_of_signals > 0:
            self.f_sampling = value
            self._render_signal()

    def _render_signal(self):
        self.num_of_signals += 1
        self._resample()
        self._reconstruct()
        self._display_error_signal()

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
        # SNR = Psig / Pnoise

        # Calculate instantaneous power

        # check that the passed vectors are in numpy array
        try:
            instantaneous_power = self.signal.y_vec ** 2
        except:
            self.signal.y_vec = np.array(self.signal.y_vec)
            self.signal.x_vec = np.array(self.signal.x_vec)
            instantaneous_power = self.signal.y_vec ** 2

        # Calculate average power
        average_power = np.mean(instantaneous_power)

        SNR = self.signal.SNR

        average_noise = average_power * SNR
        noise = np.random.normal(0, average_noise, len(self.signal.y_vec))

        # update the original signal not the already noised one
        self.signal.y_vec = self.original_signal.y_vec + noise

    def _on_snr_slider_change(self, value):
        value /= 10

        if self.num_of_signals > 0:
            try:

               self.signal.SNR = value
            except:
                pass   
            self.snr_label.setText(str(value))
            self.add_gaussian_noise()

            # render the new graph
            self.original_signal_graph.clear()
            pen_c = pg.mkPen(color=(255, 255, 255))
            self.original_signal_graph.plot(self.signal.x_vec, self.signal.y_vec, pen=pen_c)
            self._render_signal()

    

    def _reset(self) -> None:
        self.signal = None

        # Re-initialize UI state
        self.sampled_signal: Signal
        self.reconstructed_signal: Signal
        self.error_signal: Signal
        self.sampling_curve = None
        self.reconstruct_curve = None
        self.error_curve = None
        self.f_sampling = 150  # Initial f_sampling, can't be = zero (VIMP) to avoid logical and mathematical errors.
        self.sampling_freq_slider.setMinimum(0)
        self.sampling_freq_slider.setMaximum(MAX_F_SAMPLING)
        self.sampling_freq_slider.setValue(0)
        self.snr_slider.setMinimum(0)
        self.snr_slider.setMaximum(10)
        self.snr_slider.setValue(0)
        self.num_of_signals = 0
        self.noised = False
        self.imported = False

        # Clear graphs
        self.original_signal_graph.clear()
        self.reconstructed_signal_graph.clear()
        self.error_signal_graph.clear()

    def _clear_signal(self) -> None:
        self._reset()

    def _add_freq_unit(self) -> None:
        if self.f_sampling + 1 <= MAX_F_SAMPLING:
            self.f_sampling += 1
            self._on_freq_slider_change(self.f_sampling)

    def _sub_freq_unit(self) -> None:
        if self.f_sampling - 1 >= 0:
            self.f_sampling -= 1
            self._on_freq_slider_change(self.f_sampling)
    
    def _setFsToMultiplesFm(self, multiple) -> None:
        if self.imported:
            if self.signal.get_max_freq_open_signal() * multiple > MAX_F_SAMPLING:
                self.f_sampling = MAX_F_SAMPLING
            else:
                self.f_sampling = self.signal.get_max_freq_open_signal() * multiple
        else:
            if self.signal.get_max_freq() * multiple > MAX_F_SAMPLING:
                self.f_sampling = MAX_F_SAMPLING
            else:
                self.f_sampling = self.signal.get_max_freq() * multiple
        self._on_freq_slider_change(self.f_sampling)
        self._render_signal()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
