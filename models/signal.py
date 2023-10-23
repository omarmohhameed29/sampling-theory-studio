from enum import Enum
from scipy.fft import fft, fftfreq
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
        fft_y = fft(self.y_vec)
        frequencies = fftfreq(len(self.y_vec), d=(self.x_vec[1] - self.x_vec[0]))
        index = np.argmax(np.abs(fft_y))
        fmax = int(6.28 * np.abs(frequencies[index]))
        return fmax