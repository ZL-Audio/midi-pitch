import mido
import matplotlib.pyplot as plt
import numpy as np

from collections import defaultdict


class MIDI:

    def __init__(self, midi_path: str):
        self.mid = mido.MidiFile(midi_path)
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
        roll = self.get_roll(sr)

        left, right = self.get_note_range(roll)

        roll = roll[left:right+1].astype('float')
        ax.imshow(roll, extent=(0.0, int(self.mid.length * sr) / sr, left - 0.5, right + 0.5),
                  vmin=0.0, vmax=1.0,
                  origin="lower", interpolation='nearest', aspect='auto', cmap='inferno')

    @staticmethod
    def get_note_range(roll, extend=3):
        roll_max = np.nonzero(np.any(roll > 0, axis=1))[0]
        left, right = roll_max[0], roll_max[-1]
        left = np.max([0, left - extend])
        right = right + extend
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
