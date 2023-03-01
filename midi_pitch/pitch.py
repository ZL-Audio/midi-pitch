import matplotlib.pyplot as plt
import numpy as np

import librosa
from .midi import MIDI
from .parameters import LOUDNESS_HEIGHT_R, LOUDNESS_ALPHA

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
        self.loudness = np.array([])

    def analysis(self, frame_length: int = 2048, f0_algo='yin', loudness=False):
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
        if loudness:
            logger.info('Analyze vocal loudness.')
            self.loudness = self._get_loudness(frame_length=frame_length)

    @property
    def duration(self) -> float:
        return librosa.get_duration(y=self.snd, sr=self.sr)

    @property
    def time_step(self) -> float:
        return self.duration / self.frequencies.shape[0]

    def plot(self, ax, loudness: bool = False, left=None, right=None):
        ax.plot(self.time_ticks, self.frequencies, 'o', markersize=1.5)
        if loudness:
            if left is None or right is None:
                left, right = np.nanmin(self.frequencies), np.nanmax(self.frequencies)
            else:
                left, right = left - 0.5, right + 0.5
            loudness = np.copy(self.loudness)
            loudness = loudness / (np.max(loudness) - np.min(loudness)) * (right - left) * LOUDNESS_HEIGHT_R + left
            ax.fill_between(self.time_ticks, 0, loudness, alpha=LOUDNESS_ALPHA)

    def _get_loudness(self, frame_length: int):
        # https://stackoverflow.com/questions/64913424/how-to-compute-loudness-from-audio-signal
        n_fft = frame_length
        hop_length = n_fft // 4
        spec_mag = np.abs(librosa.stft(y=self.snd, n_fft=n_fft, hop_length=hop_length))
        spec_db = librosa.amplitude_to_db(spec_mag)

        freqs = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)
        freqs = np.maximum(freqs, np.finfo(freqs.dtype).resolution)
        a_weights = librosa.A_weighting(freqs)
        a_weights = np.expand_dims(a_weights, axis=1)

        spec_dba = spec_db + a_weights

        loudness = np.squeeze(librosa.feature.rms(S=librosa.db_to_amplitude(spec_dba), frame_length=frame_length))
        return loudness
