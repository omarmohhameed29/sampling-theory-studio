import numpy as np
from models.signal import Signal, SignalType

class Reconstructor:
    def __init__(self, sampled_signal: Signal) -> None:
        self.sampled_signal = sampled_signal

    def reconstruct(self, t: np.ndarray, f_sampling) -> Signal:
        x_vec = self.sampled_signal.x_vec
        y_vec = self.sampled_signal.y_vec

        # Whittaker–Shannon interpolation formula
        y_interp = np.zeros_like(t)
        for i, t_i in enumerate(t):
            y_interp[i] = np.sum(y_vec * np.sinc((x_vec - t_i) * f_sampling))

        return Signal(t, y_interp, SignalType.CONTINUOUS)
