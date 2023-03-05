[![zh](https://img.shields.io/badge/lang-zh-red.svg)](/README.md)
[![en](https://img.shields.io/badge/lang-en-yellow.svg)](/README.en.md)

`midi_pitch` is a library for displaying the pitch (from a vocal sound) and the midi (from a midi file) as a video with four lines :kissing_heart:

```python
from midi_pitch import Handler
handler = Handler(midi_file=midi_file, vocal_file=vocal_file, output_path=output_path)
handler.compare()
handler.render()
```
which will output three files in the `output_path`: `pitch.pdf`, `pitch.png`, and `pitch.mp4`. See [BV1z8411T7vH](https://www.bilibili.com/video/BV1z8411T7vH) as a demo output. For the full documentation of `Handler`, please read [handler.py](/midi_pitch/handler.py).

# Requirements
- Install all python packages listed in `requirements.txt`
- Install `ffmpeg`
- Install `ImageMagick`

# Quick Start
- Change `vocal_file`、`midi_file` in `main.py` to the path of the vocal/MIDI file
- `python3 main.py`

or

- Open [midi_pitch on Google Colab](https://colab.research.google.com/drive/1ylPzetjMGYI_Vz55YKPZkwEddHoVUWv9?usp=sharing) to use it without installing anything.

# Recommended Workflow
- Generate high-quality vocal sound. If you come up with a piece of mixed music, I recommend using [Spleeter](https://github.com/deezer/spleeter) or [Demucs](https://github.com/facebookresearch/demucs) to separate the vocal sound
- Call `Handler.compare` and check the comparison image `pitch.png`, change parameters if needed
- Call `Handler.render` and have a cup of :coffee:
- Adjust the notes in your project according to `pitch.mp4`
