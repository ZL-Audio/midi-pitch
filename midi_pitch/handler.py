import cv2
import subprocess
import numpy as np
from moviepy.editor import ImageClip, ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import matplotlib.pyplot as plt
from .midi import MIDI
from .pitch import Pitch
from .fixer import PitchFixer, TrimFixer, RangeFixer
from .parameters import CURSOR_WIDTH_R, CURSOR_POS_R, CURSOR_COLOR, CURSOR_ALPHA
from .parameters import NOTE_CHART, PIANO_COLOR_0, PIANO_COLOR_1, PIANO_HEIGHT_R, TEXT_COLOR

import logging

logger = logging.getLogger(__name__)


class Handler:
    midi_file: str
    vocal_file: str
    output_path: str

    def __init__(self, midi_file: str, vocal_file: str, output_path: str):
        logger.info('Analysis files.')
        self.midi_file = midi_file
        self.mid = None if midi_file is None else MIDI(midi_file)
        self.vocal_file  = vocal_file
        self.pitch = Pitch(vocal_file)
        self.output_path = output_path

    def compare(self, sr: float = 100, trim: float = 0,
                trim_fix: bool = False, trim_fix_method='match',
                pitch_fix: bool = True,
                range_fix: bool = True,
                fig_size: tuple = (200, 5), dpi=144):
        """
        output the comparison image
        :param sr: sampling rate
        :param trim: length of the trim at the start of the vocal sound file
        :param trim_fix: whether enable trim-fixer to automatically set the value of trim
        :param trim_fix_method: method used by trim-fixer
        :param pitch_fix: whether enable pitch-fixer to automatically fix pitch according to MIDI
        :param range_fix:whether enable range-fixer to automatically remove pitch out of range of MIDI
        :param fig_size: figure size of the `pitch.pdf`
        :param dpi: DPI of the `pitch.png`
        :return:
        """
        self.pitch = Pitch(self.vocal_file, sr=sr, trim=trim)
        if trim_fix and self.mid is not None:
            fixer = TrimFixer(self.mid, self.pitch)
            trim += fixer.auto_fix(method=trim_fix_method)
            self.pitch = Pitch(self.vocal_file, sr=sr, trim=trim)

        if pitch_fix and self.mid is not None:
            fixer = PitchFixer(self.mid, self.pitch)
            fixer.auto_fix()

        if range_fix and self.mid is not None:
            fixer = RangeFixer(self.mid, self.pitch)
            fixer.auto_fix()

        fig, ax = plt.subplots(figsize=fig_size)
        logger.info('Plot MIDI and Pitch.')
        self.mid.plot(ax)
        self.pitch.plot(ax)
        ax.set_xlim(self.pitch.snd.xmin, self.pitch.snd.xmax)
        left, right = self.mid.get_note_range(self.mid.get_roll_at_time_tick(self.pitch.time_ticks))
        ax.set_ylim(left - 0.5, right + 0.5)
        ax.axis('off')
        plt.tight_layout()
        logger.info('Save figure as PDF.')
        fig.savefig(self.output_path + 'pitch.pdf', bbox_inches='tight', pad_inches=0, transparent=True)
        plt.close(fig)
        logger.info('Convert PDF to PNG.')
        subprocess.run(['convert', '-density', str(dpi), self.output_path + 'pitch.pdf',
                        '-quality', '100', self.output_path + 'pitch.png'])

    def render(self, img_file: str = None, piano: bool = False,
               fps: int = 30, frame_size: tuple = (1280, 720),
               bitrate='4096k', audio_bitrate='512k'):
        """
        render the comparison video
        :param img_file: path of the comparison image
        :param piano: whether display the piano
        :param fps: fps of the video
        :param frame_size: resolution of the video
        :param bitrate: target bit-rate of the video
        :param audio_bitrate: target audio-rate of the video
        :return:
        """
        if img_file is None:
            img_file = self.output_path + 'pitch.png'
        logger.info('Resize figure.')
        img = cv2.imread(img_file, cv2.IMREAD_UNCHANGED)
        img = cv2.resize(img, (int(frame_size[1] / img.shape[0] * img.shape[1]), frame_size[1]))
        if piano:
            cv2.imwrite(self.output_path + 'pitch.png', img)
        else:
            cv2.imwrite(self.output_path + 'pitch.png', img[:, :, :-1])

        duration = self.pitch.snd.xmax - self.pitch.snd.xmin

        clip_list = []

        if piano:
            clip_list += self._get_piano_clip(frame_size, duration)
        clip_list.append(self._get_img_clip(img, frame_size, duration))
        clip_list.append(self._get_cursor_clip(frame_size, duration))

        audio = AudioFileClip(self.vocal_file)

        composite = CompositeVideoClip(clip_list, size=frame_size)
        composite = composite.set_audio(audio)
        composite.write_videofile(self.output_path + 'pitch.mp4',
                                  temp_audiofile=self.output_path + 'temp-audio.m4a',
                                  fps=fps, codec='libx264', bitrate=bitrate,
                                  audio=True, audio_codec='aac', audio_bitrate=audio_bitrate,
                                  logger='bar')

    def _get_cursor_clip(self, frame_size, duration) -> ColorClip:
        cursor_width = int(frame_size[0] * CURSOR_WIDTH_R)
        cursor_pos = int(frame_size[0] * CURSOR_POS_R)
        cursor = ColorClip(size=(cursor_width, frame_size[1]), color=CURSOR_COLOR, duration=duration)
        cursor = cursor.set_opacity(CURSOR_ALPHA)
        cursor = cursor.set_position((cursor_pos - cursor_width, 0))
        return cursor

    def _get_img_clip(self, img, frame_size, duration) -> ImageClip:
        image = ImageClip(self.output_path + 'pitch.png', duration=duration)
        # image = ImageClip(img, duration=duration)
        speed = img.shape[1] / duration
        image = image.set_position(lambda t: (-t * speed + frame_size[0] * CURSOR_POS_R, 0))
        return image

    def _get_piano_clip(self, frame_size, duration) -> list:
        clip_list = []
        if self.mid is None:
            background = ColorClip(size=frame_size, color=(0, 0, 0), duration=duration)
            return [background]
        left, right = self.mid.get_note_range(self.mid.get_roll_at_time_tick(self.pitch.time_ticks))
        positions = np.linspace(frame_size[1], 0, right - left + 2).astype('int')
        heights = positions[:-1] - positions[1:]
        font_size = int(np.ceil(np.max(heights * 0.5)))
        colors = np.linspace(PIANO_COLOR_0, PIANO_COLOR_1, 12).astype('int')
        for note, pos, height in zip(range(left, right + 1), positions[1:], heights):
            note_num = note % 12
            octave = (note // 12) - 2
            note_name = NOTE_CHART[note_num] + str(octave)

            color = (colors[note_num], colors[note_num], colors[note_num])
            clip = ColorClip(size=(frame_size[0], height),
                             color=color, duration=duration)
            clip = clip.set_position(pos=(0, pos))
            clip_list.append(clip)

            clip = TextClip(txt=note_name, size=(height, height), color=TEXT_COLOR,
                            fontsize=font_size, method='caption', align='West')
            clip = clip.set_duration(duration)
            clip = clip.set_position(pos=(int(font_size * 0.5), pos))
            clip_list.append(clip)

        return clip_list
