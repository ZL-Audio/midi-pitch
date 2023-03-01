from midi_pitch import Handler
import logging
import sys
import os

logging.basicConfig(stream=sys.stdout)
logging.getLogger('midi_pitch').setLevel(logging.DEBUG)

midi_file = 'files/original.mid'
vocal_file = 'files/vocals.wav'
output_path = 'files/'
if not os.path.exists(output_path):
    os.mkdir(output_path)


def main():
    handler = Handler(midi_file=midi_file, vocal_file=vocal_file, output_path=output_path, sr=44100)
    handler.compare(trim_fix=True, f0_algo='yin', loudness=True, frame_length=1024)
    handler.render(frame_size=(640, 360), piano=True)


if __name__ == '__main__':
    main()
