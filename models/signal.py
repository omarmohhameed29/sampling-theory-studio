from enum import Enum
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import numpy as np

class SignalType(Enum):
    CONTINUOUS = 0
    DISCRETE = 1

class Signal:
    def __init__(self, x_vec, y_vec, signal_type: SignalType = SignalType.CONTINUOUS, SNR = 100) -> None:
        self.x_vec = x_vec
        self.y_vec = y_vec
        self.signal_type = signal_type
        self.SNR = SNR

    def get_max_freq(self):
         fs = 1 / (self.x_vec[1] - self.x_vec[0])
         yf = np.fft.fft(self.y_vec)
         xf = np.fft.fftfreq(len(self.y_vec), 1/fs)
         max_freq_index = np.argmax(np.abs(yf))
         max_freq = xf[max_freq_index]
         return int(np.abs(max_freq))
    
    def get_max_freq_open_signal(self):
        fs = 1/(self.x_vec[1] - self.x_vec[0])
        fmax = fs/2
        return int(fmax)