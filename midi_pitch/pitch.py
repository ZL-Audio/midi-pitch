import matplotlib.pyplot as plt
import numpy as np

import librosa
from .midi import MIDI

import logging

logger = logging.getLogger(__name__)


class Pitch:

    def __init__(self, vocal_file: str, trim: float = 0, sr: float = 22050):
        logger.info('Read vocal file.')
        self.trim = trim
        self.snd, self.sr = librosa.load(vocal_file, sr=sr, offset=trim)
        self.frequencies = np.array([])
        self.time_ticks = np.array([])
        self.mask = np.array([])

    def analysis(self, frame_length: int = 2048, f0_algo='yin'):
        logger.info('Analyze vocal frequencies with {}.'.format(f0_algo))
        if f0_algo == 'yin':
            self.frequencies = librosa.yin(y=self.snd, sr=self.sr, frame_length=frame_length,
                                           fmin=librosa.note_to_hz('C2'),
                                           fmax=librosa.note_to_hz('C7'))
        else:
            self.frequencies, _, _ = librosa.pyin(y=self.snd, sr=self.sr, frame_length=frame_length,
                                                  fmin=librosa.note_to_hz('C2'),
                                                  fmax=librosa.note_to_hz('C7'),
                                                  fill_na=np.nan)
        self.frequencies = MIDI.freq_to_note(self.frequencies)
        self.time_ticks = librosa.times_like(self.frequencies, sr=self.sr, hop_length=frame_length // 4)

    @property
    def duration(self) -> float:
        return librosa.get_duration(y=self.snd, sr=self.sr)

    @property
    def time_step(self) -> float:
        return self.duration / self.frequencies.shape[0]

    def plot(self, ax):
        ax.plot(self.time_ticks, self.frequencies, 'o', markersize=1.5)
