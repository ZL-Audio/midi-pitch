import cv2
import subprocess
from moviepy.editor import ImageClip, ColorClip, CompositeVideoClip, AudioFileClip
import matplotlib.pyplot as plt
from .midi import MIDI
from .pitch import Pitch
from .fixer import PitchFixer, TrimFixer, RangeFixer

import logging

logger = logging.getLogger(__name__)


def handle(midi_path: str, vocal_path: str, output_path: str,
           sr: float = 100, trim: float = 0,
           trim_fix: bool = False, trim_fix_method='match',
           pitch_fix: bool = True,
           range_fix: bool = False,
           fig_size: tuple = (200, 5), dpi=150,
           video_out: bool = True, fps: int = 30, frame_size: tuple = (720, 1280),
           bitrate='5000k', audio_bitrate='512k',
           cursor_pos_r: float = 0.4, cursor_width_r: float = 0.01):
    """
    handle MIDI and vocal sound, output figure and video
    :param midi_path: path of the MIDI file
    :param vocal_path: path of the vocal sound
    :param output_path: output directory
    :param sr: sampling rate
    :param trim: length of the trim at the start of the vocal sound file
    :param trim_fix: whether enable trim-fixer to automatically set the value of trim
    :param trim_fix_method: method used by trim-fixer
    :param pitch_fix: whether enable pitch-fixer to automatically fix pitch according to MIDI
    :param range_fix:whether enable range-fixer to automatically remove pitch out of range of MIDI
    :param fig_size: figure size of the `pitch.pdf`
    :param dpi: DPI of the `pitch.png`
    :param video_out: whether output the video
    :param fps: fps of the video
    :param frame_size: resolution of the video
    :param bitrate: target bit-rate of the video
    :param audio_bitrate: target audio-rate of the video
    :param cursor_pos_r: relative position of the cursor
    :param cursor_width_r: relative width of the cursor
    :return:
    """
    plt.rcParams['axes.facecolor'] = 'black'
    plt.rcParams['savefig.facecolor'] = 'black'
    logger.info('Analysis MIDI file.')
    mid = MIDI(midi_path)
    logger.info('Analysis vocal file.')
    pitch = Pitch(vocal_path, sr=sr, trim=trim)

    if trim_fix:
        fixer = TrimFixer(mid, pitch)
        trim += fixer.auto_fix(method=trim_fix_method)
        pitch = Pitch(vocal_path, sr=sr, trim=trim)

    if pitch_fix:
        fixer = PitchFixer(mid, pitch)
        fixer.auto_fix()

    if range_fix:
        fixer = RangeFixer(mid, pitch)
        fixer.auto_fix()

    fig, ax = plt.subplots(figsize=fig_size)

    logger.info('Plot MIDI and Pitch.')
    mid.plot(ax)
    pitch.plot(ax)
    ax.set_xlim(pitch.snd.xmin, pitch.snd.xmax)
    ax.axis('off')
    plt.tight_layout()
    logger.info('Save figure as PDF.')
    fig.savefig(output_path + 'pitch.pdf', bbox_inches='tight', pad_inches=0)
    logger.info('Convert PDF to PNG.')
    subprocess.run(['convert', '-density', str(dpi), output_path + 'pitch.pdf',
                    '-quality', '100', output_path + 'pitch.png'])
    plt.close(fig)

    if not video_out:
        return

    logger.info('Resize figure.')
    img = cv2.imread(output_path + 'pitch.png')
    img = cv2.resize(img, (int(frame_size[0] / img.shape[0] * img.shape[1]), frame_size[0]))
    cv2.imwrite(output_path + 'pitch.png', img)

    duration = pitch.snd.xmax - pitch.snd.xmin
    cursor_width = int(frame_size[1] * cursor_width_r)
    cursor_pos = int(frame_size[1] * cursor_pos_r)
    cursor = ColorClip(size=(cursor_width, frame_size[0]), color=(255, 255, 255), duration=duration)
    cursor = cursor.set_opacity(0.5)
    cursor = cursor.set_position((cursor_pos - cursor_width, 0))
    cursor = cursor.set_fps(30)

    image = ImageClip(output_path + 'pitch.png', duration=duration)
    speed = img.shape[1] / duration
    image = image.set_position(lambda t: (-t * speed + cursor_pos, 0))
    image = image.set_fps(30)

    audio = AudioFileClip(vocal_path)

    composite = CompositeVideoClip([image, cursor], size=(frame_size[1], frame_size[0]))
    composite = composite.set_audio(audio)
    composite.write_videofile(output_path + 'pitch.mp4', temp_audiofile=output_path + 'temp-audio.m4a',
                              fps=fps, codec='libx264', bitrate=bitrate,
                              audio=True, audio_codec='aac', audio_bitrate=audio_bitrate,
                              logger='bar')
