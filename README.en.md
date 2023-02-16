[![zh](https://img.shields.io/badge/lang-zh-red.svg)](/README.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](/README.en.md)

`midi_pitch` is a library for displaying the pitch (from a vocal sound) and the midi (from a midi file) as a video with only ONE available function `handle` :kissing_heart:

```python
from midi_pitch import handle
handle(midi_path='MIDI file', 
       vocal_path='vocal file',
       output_path='output directory')
```
which will output three files in the `output_path`: `pitch.pdf`, `pitch.png`, and `pitch.mp4`. See [BV1z8411T7vH](https://www.bilibili.com/video/BV1z8411T7vH) as a demo output. For the full documentation of `handle`, please read [handler.py](/midi_pitch/handler.py).

# Requirements
- Install all python packages listed in `requirements.txt`
- Install `ffmpeg`
- Install `ImageMagick`

# Quick Start
- Change `vocal_path`、`midi_path` in `main.py` to the path of the vocal/MIDI file
- `python3 main.py`

# Recommended Workflow
- Generate high-quality vocal sound. If you come up with a piece of mixed music, I recommend using [Spleeter](https://github.com/deezer/spleeter) or [Demucs](https://github.com/facebookresearch/demucs) to separate the vocal sound
- Call `handle` and have a cup of :coffee:, change parameters if needed
- Adjust the notes in your project according to `pitch.mp4`