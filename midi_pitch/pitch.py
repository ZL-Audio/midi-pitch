import matplotlib.pyplot as plt
import numpy as np

import parselmouth
from .midi import MIDI


class Pitch:

    def __init__(self, vocal_file: str, sr: float = 100, trim: float = 0):
        self.snd = parselmouth.Sound(vocal_file)
        self.snd = parselmouth.Sound(self.snd, sampling_frequency=self.snd.get_sampling_frequency(),
                                     start_time=-trim).convert_to_mono()
        self.sr = sr
        pitch = self.snd.to_pitch(time_step=1.0 / sr)
        self.time_ticks = pitch.xs()
        self.frequencies = pitch.selected_array['frequency']
        self.frequencies[self.frequencies == 0.0] = np.nan
        self.frequencies = MIDI.freq_to_note(self.frequencies)

    def plot(self, ax):
        ax.plot(self.time_ticks, self.frequencies, 'o', markersize=1.5)
