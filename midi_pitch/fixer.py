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

        roll = (roll != 0).argmax(axis=0)

        note_error = roll - self.pitch.frequencies
        note_error[~mask] = 0

        logger.info('PitcherFixer: changes {} notes.'.format(np.sum(note_error != 0)))

        note_error = np.round(note_error / 12).astype('int') * 12
        self.pitch.frequencies = self.pitch.frequencies + note_error


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
        bound = int(1 / self.pitch.time_step)
        for i in range(-bound, bound):
            trim = i * self.pitch.time_step
            time_ticks = self.pitch.time_ticks + trim
            roll = self.mid.get_roll_at_time_tick(time_ticks)
            roll_mask = np.sum(roll, axis=0) > 0
            _mask = np.logical_and(roll_mask, np.isfinite(self.pitch.frequencies))
            mask_sums.append(np.sum(_mask))
        trim = (np.argmax(mask_sums) - bound) * self.pitch.time_step
        return trim

    def _auto_fix_from_error(self):
        error_sums = []

        bound = 2 * int(1 / self.pitch.time_step)
        for i in range(-bound, bound):
            trim = i * self.pitch.time_step
            time_ticks = self.pitch.time_ticks + trim
            roll = self.mid.get_roll_at_time_tick(time_ticks)
            roll_mask = np.sum(roll, axis=0) > 0
            roll = (roll != 0).argmax(axis=0)
            _mask = np.logical_and(roll_mask, np.isfinite(self.pitch.frequencies))
            _error = roll - self.pitch.frequencies
            _error[~_mask] = 0
            error_sums.append(np.sum(np.abs(_error)) / np.sum(_mask))
        trim = (np.argmin(error_sums) - bound) * self.pitch.time_step
        return trim


class RangeFixer:

    def __init__(self, mid: MIDI, pitch: Pitch):
        self.mid = mid
        self.pitch = pitch

    def auto_fix(self):
        roll = self.mid.roll

        left, right = MIDI.get_note_range(roll)

        num_remove = np.sum(self.pitch.frequencies < left) + np.sum(self.pitch.frequencies > right)

        self.pitch.frequencies[self.pitch.frequencies < left] = np.nan
        self.pitch.frequencies[self.pitch.frequencies > right] = np.nan

        roll_mask = np.sum(roll, axis=0) > 0

        conv_mask = np.ones(int(1 / self.pitch.time_step))
        roll_mask = np.convolve(roll_mask, conv_mask, mode='same')
        roll_mask = roll_mask > 0

        num_remove += np.sum(np.logical_and(np.isfinite(self.pitch.frequencies), ~roll_mask))
        logger.info('RangeFixer: remove {} notes.'.format(num_remove))
        self.pitch.frequencies[~roll_mask] = np.nan
