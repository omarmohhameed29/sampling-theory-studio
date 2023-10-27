import os
import sys

# from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal
import pyqtgraph as pg
from numpy import sin, cos, pi
import numpy as np
import math
from PyQt6.QtCore import Qt

from models.signal import Signal

mainwindow_ui_file_path = os.path.join(os.path.dirname(__file__), 'views', 'create_signal_window.ui')
uiclass, baseclass = pg.Qt.loadUiType(mainwindow_ui_file_path)

# TODO: Change this later
MAX_F_SAMPLING = 500

class CreateSignalWindow(uiclass, baseclass):
    signal_saved = pyqtSignal(Signal)
    window_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Composer - Create Signal")

        self.cosine_frequency = 1
        self.x = np.array([])
        self.y = np.array([])
        # self.components_x = []
        # self.components_y = []

        self.cosine_amplitude = 1
        self.cosine_amplitude_unit = 1
        self.cosine_phase = 0

        self.functions = []
        self.components_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.components_list.customContextMenuRequested.connect(self.showContextMenu)


        # Connecting UI controls to events
        self._initialize_signals_slots()

        self.cosine_amplitude_comboBox.addItem('m')
        self.cosine_amplitude_comboBox.addItem('mm')
        self.cosine_amplitude_comboBox.addItem('µm')


        self.cosine_frequency_slider.setMinimum(1)
        self.cosine_frequency_slider.setMaximum(250)

        self.cosine_amplitude_slider.setMinimum(1)
        self.cosine_amplitude_slider.setMaximum(1000)

        self.cosine_phase_slider.setMinimum(-180)
        self.cosine_phase_slider.setMaximum(180)

        self.signal_graph.setXRange(0,10)
        self.signal_graph.setYRange(-1,1)
        self._update_plot()


    def _initialize_signals_slots(self):
       self.cosine_frequency_slider.valueChanged.connect(self._on_cosine_freq_slider_change)
       self.cosine_amplitude_slider.valueChanged.connect(self._on_cosine_amp_slider_change)
       self.cosine_phase_slider.valueChanged.connect(self._on_cosine_phase_slider_change)

       self.cosine_amplitude_comboBox.currentTextChanged.connect(self._on_cosine_amp_combobox_change)

       self.add_component_button.clicked.connect(self.add_signal_component)
       self.save_signal_button.clicked.connect(self.save_signal)
       self.clear_button.clicked.connect(self.clear_components) 
       self.clear_button.hide()
       self.actionClear_All.triggered.connect(self.clear_components)
       

    
    def _on_cosine_freq_slider_change(self, value):
        self.cosine_frequency = value
        self.cosine_frequency_value.setText(str(value) + ' Hz')
        self._update_plot()

    def _on_cosine_amp_slider_change(self, value):
        self.cosine_amplitude = value
        self.cosine_amplitude_value.setText(str(value) + ' '+ self.cosine_amplitude_comboBox.currentText())
        self._update_plot()

    def _on_cosine_phase_slider_change(self, value):
        self.cosine_phase = value
        self.cosine_phase_value.setText(str(value) + '°')
        self._update_plot()

    def _on_cosine_amp_combobox_change(self, value):
        if value == 'µm':
            self.cosine_amplitude_unit = 10**(-6)
        elif value == 'mm':
            self.cosine_amplitude_unit = 10**(-3)
        elif value == 'm':
            self.cosine_amplitude_unit = 1
        self.cosine_amplitude_value.setText(str(self.cosine_amplitude) + ' '+ value)  
        self._update_plot()

    def _update_plot(self):
        equation = self._generate_list()
        self.signal_graph.clear()
        list_y = []
        for x in self.x:
           y = 0
           y+=equation(x)
           for eq in self.functions:
               y+= eq(x)
           list_y.append(y)    
        self.signal_graph.plot(self.x,list_y) 
        # self.functions.pop()   

    def _generate_list(self):
        self.x = np.linspace(0, math.ceil(1000 / (2 * self.cosine_frequency)), 1000)
        self.y = self.cosine_amplitude * self.cosine_amplitude_unit * cos(self.cosine_frequency *self.x - (self.cosine_phase * pi/180))
        equation = lambda x, amp=self.cosine_amplitude, unit=self.cosine_amplitude_unit, freq=self.cosine_frequency, phase=self.cosine_phase: amp * unit * math.cos(freq * x - (phase * math.pi/180)) 
        return equation
        # self.functions.append(eqution)



    def save_signal(self):
        # Create a Signal object from the input data
        if len(self.functions) < 1:
            msg_box = QMessageBox() 
            # msg_box.setIcon(QMessageBox.warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("You have to add components first.")
            msg_box.exec()
            return
        list_y = []
        for x in self.x:
           y = 0
           for eq in self.functions:
               y+= eq(x)
           list_y.append(y)    
        t = self.x
        y = list_y
        signal = Signal(t, y)
        
        # Emit the signal_saved signal with the Signal object as the argument
        self.signal_saved.emit(signal)
        
        self.window_closed.emit()

    def clear_components(self):
        self.components_list.clear()
        self.signal_graph.clear()
        self.x = np.array([])
        self.y = np.array([])
        self.functions.clear()
        self.cosine_frequency = 1
        self.cosine_amplitude = 1
        self.cosine_phase = 0
        self.cosine_frequency_slider.setValue(1)
        self.cosine_amplitude_slider.setValue(1)
        self.cosine_phase_slider.setValue(0)
        self.cosine_frequency_value.setText(str(1) + ' Hz')
        self.cosine_amplitude_value.setText(str(1) + ' '+ self.cosine_amplitude_comboBox.currentText())
        self.cosine_phase_value.setText(str(0) + '°')
        self.signal_graph.setXRange(0,10)
        self.signal_graph.setYRange(-1,1)
        self._update_plot()

    def add_signal_component(self):
        #writing item to the list
        if(self.cosine_amplitude > 1 or self.cosine_amplitude_unit != 1):
            if(self.cosine_phase > 0):
                item = QListWidgetItem(f"{self.cosine_amplitude * self.cosine_amplitude_unit} Cos( 2Π ({self.cosine_frequency}) t - {self.cosine_phase} °)")
            elif self.cosine_phase < 0:
                item = QListWidgetItem(f"{self.cosine_amplitude * self.cosine_amplitude_unit} Cos( 2Π ({self.cosine_frequency}) t + {abs(self.cosine_phase)} °)")
            else:
                item = QListWidgetItem(f"{self.cosine_amplitude * self.cosine_amplitude_unit} Cos( 2Π ({self.cosine_frequency}) t )")
        else:
            if(self.cosine_phase > 0):
                item = QListWidgetItem(f"Cos( 2Π ({self.cosine_frequency}) t - {self.cosine_phase} °)")
            elif self.cosine_phase < 0:
                item = QListWidgetItem(f"Cos( 2Π ({self.cosine_frequency}) t + {abs(self.cosine_phase)} ° )")
            else:
                item = QListWidgetItem(f"Cos( 2Π ({self.cosine_frequency}) t )")
        

        self.components_list.addItem(item)

        #changing the plot
        self.x = np.linspace(0, math.ceil(1000 / (2 * self.cosine_frequency)), 1000)
        self.y = self.cosine_amplitude * self.cosine_amplitude_unit * cos(self.cosine_frequency *self.x - (self.cosine_phase * pi/180))     
        equation = lambda x, amp=self.cosine_amplitude, unit=self.cosine_amplitude_unit, freq=self.cosine_frequency, phase=self.cosine_phase: amp * unit * math.cos(freq * x - (phase * math.pi/180)) 
        self.functions.append(equation)
        self._update_plot()

    def showContextMenu(self, pos):
         selected_item = self.components_list.itemAt(pos)

         if selected_item:
            selected_index = self.components_list.row(selected_item)
            context_menu = QMenu(self)
            action1 = context_menu.addAction("Remove Component")
            action = context_menu.exec(QCursor.pos())
            if action == action1:
                self.remove_component(selected_index)  

    def remove_component(self, index):
        self.functions.pop(index)
        self.components_list.takeItem(index)
        self._update_plot()
def main():
    app = QApplication(sys.argv)
    window = CreateSignalWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
