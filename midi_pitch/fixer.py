import numpy as np
import matplotlib.pyplot as plt
from .midi import MIDI
from .pitch import Pitch

import logging

logger = logging.getLogger(__name__)


class PitchFixer:

    def __init__(self, mid: MIDI, pitch: Pitch):
        self.mid = mid
        self.pitch = pitch

    def auto_fix(self):
        roll = self.mid.get_roll_at_time_tick(self.pitch.time_ticks).astype('int')

        freq_mask = np.isfinite(self.pitch.frequencies)
        roll_mask = np.sum(roll, axis=0) > 0
        mask = np.logical_and(freq_mask, roll_mask)

        notes = MIDI.freq_to_note(self.pitch.frequencies)

        roll = (roll != 0).argmax(axis=0)

        note_error = roll - notes
        note_error[~mask] = 0

        logger.info('PitcherFixer: changes {} notes.'.format(np.sum(note_error != 0)))

        note_error = np.round(note_error / 12.0).astype('int') * 12
        notes = (roll - note_error).astype('int')
        freq_error = MIDI.note_to_freq(roll) - MIDI.note_to_freq(notes)
        self.pitch.frequencies = self.pitch.frequencies + freq_error


class TrimFixer:

    def __init__(self, mid: MIDI, pitch: Pitch):
        self.mid = mid
        self.pitch = pitch

    def auto_fix(self, method='error'):
        trim = 0.0
        if method == 'error':
            trim = self._auto_fix_from_error()
        elif method == 'match':
            trim = self._auto_fix_from_match()
        logger.info('TrimFixer: trim {}s.'.format(trim))
        return trim

    def _auto_fix_from_match(self):
        mask_sums = []
        roll = self.mid.get_roll_at_time_tick(self.pitch.time_ticks).astype('int')
        roll_mask = np.sum(roll, axis=0) > 0
        freq_mask = np.isfinite(self.pitch.frequencies)
        for i in range(0, int(self.pitch.sr / 3)):
            _freq_mask = np.zeros_like(freq_mask)
            _freq_mask[:len(freq_mask) - i] = freq_mask[i:]
            _mask = np.logical_and(_freq_mask, roll_mask)
            mask_sums.append(np.sum(_mask))
        return np.argmax(mask_sums) / self.pitch.sr

    def _auto_fix_from_error(self):
        error_sums = []

        roll = self.mid.get_roll_at_time_tick(self.pitch.time_ticks).astype('int')
        roll_mask = np.sum(roll, axis=0) > 0
        roll = (roll != 0).argmax(axis=0)
        freq_mask = np.isfinite(self.pitch.frequencies)
        for i in range(0, int(self.pitch.sr / 3)):
            _freq_mask = np.zeros_like(freq_mask)
            _freq_mask[:len(freq_mask) - i] = freq_mask[i:]
            _mask = np.logical_and(_freq_mask, roll_mask)

            _freq = np.zeros_like(self.pitch.frequencies)
            _freq[:len(freq_mask) - i] = self.pitch.frequencies[i:]
            _note = MIDI.freq_to_note(_freq)

            error = _note - roll
            error[~_mask] = 0
            error_sums.append(np.sum(np.square(error)) / np.sum(_mask))
        return np.argmin(error_sums) / self.pitch.sr


class RangeFixer:

    def __init__(self, mid: MIDI, pitch: Pitch):
        self.mid = mid
        self.pitch = pitch

    def auto_fix(self):
        roll = self.mid.get_roll_at_time_tick(self.pitch.time_ticks).astype('int')

        left, right = MIDI.get_note_range(roll)
        left, right = MIDI.note_to_freq(left), MIDI.note_to_freq(right)

        num_remove = np.sum(self.pitch.frequencies < left) + np.sum(self.pitch.frequencies > right)

        self.pitch.frequencies[self.pitch.frequencies < left] = np.nan
        self.pitch.frequencies[self.pitch.frequencies > right] = np.nan

        roll_mask = np.sum(roll, axis=0) > 0

        conv_mask = np.ones(int(self.pitch.sr))
        roll_mask = np.convolve(roll_mask, conv_mask, mode='same')
        roll_mask = roll_mask > 0

        num_remove += np.sum(np.logical_and(np.isfinite(self.pitch.frequencies), ~roll_mask))
        logger.info('RemoveFixer: remove {} notes.'.format(num_remove))
        self.pitch.frequencies[~roll_mask] = np.nan
