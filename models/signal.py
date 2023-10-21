from enum import Enum

class SignalType(Enum):
    CONTINUOUS = 0
    DISCRETE = 1

class Signal:
    def __init__(self, x_vec, y_vec, signal_type: SignalType = SignalType.CONTINUOUS, SNR = 100) -> None:
        self.x_vec = x_vec
        self.y_vec = y_vec
        self.signal_type = signal_type
        self.SNR = SNR
        