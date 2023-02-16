from midi_pitch import handle
import logging
import sys
import os

logging.basicConfig(stream=sys.stdout)
logging.getLogger('midi_pitch').setLevel(logging.DEBUG)

midi_path = 'files/original.mid'
vocal_path = 'files/vocals.wav'
output_path = 'files/'
os.mkdir(output_path)


def main():
    handle(midi_path=midi_path, vocal_path=vocal_path, output_path=output_path,
           trim_fix=True, trim_fix_method='match',
           pitch_fix=True,
           range_fix=True)


if __name__ == '__main__':
    main()
