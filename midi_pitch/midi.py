import mido
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from collections import defaultdict

from .parameters import EXTEND

class MIDI:

    def __init__(self, midi_file: str):
        self.mid = mido.MidiFile(midi_file)
        self.messages = []

        for msg in self.mid:
            if not msg.is_meta:
                self.messages.append(msg)

    def get_roll(self, sr: float = 100) -> np.array:
        time_ticks = np.linspace(0.0, int(self.mid.length * sr) / sr, int(self.mid.length * sr) + 1)
        return self.get_roll_at_time_tick(time_ticks)

    def get_roll_at_time_tick(self, time_ticks: np.array) -> np.array:
        keys = np.zeros(128, dtype='bool')
        roll = np.zeros((128, time_ticks.shape[0]), dtype='uint8')
        time_pos = 0.0
        roll_pos = 0
        for msg in self.messages:
            time_pos += msg.time
            while roll_pos < len(time_ticks) and time_ticks[roll_pos] < time_pos:
                roll[:, roll_pos] = keys[:]
                roll_pos += 1
            self.msg_change_keys(msg, keys)
        return roll

    def plot(self, ax: plt.Axes, sr: float = 100):
        n_colors = 256
        color_array = plt.get_cmap('inferno')(range(n_colors))
        color_array[:, -1] = np.linspace(0.0, 1.0, n_colors)
        map_object = LinearSegmentedColormap.from_list(name='rainbow_alpha', colors=color_array)

        roll = self.get_roll(sr)

        left, right = self.get_note_range(roll)

        roll = roll[left:right + 1].astype('float')
        ax.imshow(roll, extent=(0.0, int(self.mid.length * sr) / sr, left - 0.5, right + 0.5),
                  vmin=0.0, vmax=1.0,
                  origin="lower", interpolation='nearest', aspect='auto', cmap=map_object)

    @staticmethod
    def get_note_range(roll):
        roll_max = np.nonzero(np.any(roll > 0, axis=1))[0]
        left, right = roll_max[0], roll_max[-1]
        left = left - EXTEND
        right = right + EXTEND
        return left, right

    @staticmethod
    def msg_change_keys(msg, keys):
        if msg.type == 'note_on' and msg.velocity > 0:
            keys[msg.note] = True
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            keys[msg.note] = False

    @staticmethod
    def note_to_freq(note_number):
        return 440.0 * (np.power(2, (note_number - 69) / 12.0))

    @staticmethod
    def freq_to_note(freq):
        return np.log2(freq / 440) * 12 + 69
