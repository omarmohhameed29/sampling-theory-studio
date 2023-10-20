import os
import sys

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import pyqtgraph as pg
from numpy import sin, cos, pi
import numpy as np

mainwindow_ui_file_path = os.path.join(os.path.dirname(__file__), 'views', 'create_signal_window.ui')
uiclass, baseclass = pg.Qt.loadUiType(mainwindow_ui_file_path)

# TODO: Change this later
MAX_F_SAMPLING = 500

class CreateSignalWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Create Signal")
        self.x = [i/10 for i in range(-10000, 10000)]
        self.y = []

        self.frequency = 1
        self.frequency_unit = 1

        self.amplitude = 1
        self.amplitude_unit = 10**(-6)

        self.phase = 0;

        # Connecting UI controls to events
        self._initialize_signals_slots()
        self.frequency_comboBox.addItem('Hz')
        self.frequency_comboBox.addItem('kHz')
        self.frequency_comboBox.addItem('MHz')

        self.amplitude_comboBox.addItem('m')
        self.amplitude_comboBox.addItem('mm')
        self.amplitude_comboBox.addItem('µm')

        self.frequency_slider.setMinimum(1)
        self.frequency_slider.setMaximum(1000)

        self.amplitude_slider.setMinimum(1)
        self.amplitude_slider.setMaximum(1000)

        self.phase_slider.setMinimum(-180)
        self.phase_slider.setMaximum(180)

        self.signal_graph.setXRange(-180,180)
        self._update_plot()


    def _initialize_signals_slots(self):
       self.frequency_slider.valueChanged.connect(self._on_freq_slider_change)
       self.amplitude_slider.valueChanged.connect(self._on_amp_slider_change)
       self.phase_slider.valueChanged.connect(self._on_phase_slider_change)

       self.frequency_comboBox.currentTextChanged.connect(self._on_freq_combobox_change)
       self.amplitude_comboBox.currentTextChanged.connect(self._on_amp_combobox_change)
       

  
    def _on_freq_slider_change(self, value):
        self.frequency = value
        self.frequency_value.setText(str(value) + ' '+ self.frequency_comboBox.currentText())
        self._update_plot()

    def _on_amp_slider_change(self, value):
        self.amplitude = value
        self.amplitude_value.setText(str(value) + ' '+ self.amplitude_comboBox.currentText())
        self._update_plot()

    def _on_phase_slider_change(self, value):
        self.phase = value
        self.phase_value.setText(str(value) + '°')
        self._update_plot()

    def _on_freq_combobox_change(self, value):
        if value == 'Hz':
            self.frequency_unit = 1
        elif value == 'kHz':
            self.frequency_unit = 10**3
        elif value == 'MHz':
            self.frequency_unit = 10**6
        self.frequency_value.setText(str(self.frequency) + ' '+ value) 
        self._update_plot()

    def _on_amp_combobox_change(self, value):
        if value == 'µm':
            self.amplitude_unit = 10**(-6)
        elif value == 'mm':
            self.amplitude_unit = 10**(-3)
        elif value == 'm':
            self.amplitude_unit = 1
        self.amplitude_value.setText(str(self.amplitude) + ' '+ value)  
        self._update_plot()

    def _update_plot(self):
        self._generate_list()
        self.signal_graph.clear()
        self.signal_graph.plot(self.x,self.y)   

    def _generate_list(self):
        self.y.clear()
        for i in self.x:
            self.y.append(self.amplitude * self.amplitude_unit * sin(self.frequency * self.frequency_unit *(i - self.phase) * (pi/180)))
def main():
    app = QApplication(sys.argv)
    window = CreateSignalWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
