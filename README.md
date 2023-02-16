[![zh](https://img.shields.io/badge/lang-zh-red.svg)](/README.md)
[![en](https://img.shields.io/badge/lang-en-yellow.svg)](/README.en.md)

`midi_pitch` 是一个制作人声音高线和 MIDI 对比视频的库。仅需四行就可以完成 :kissing_heart:

```python
from handle import Handler
handler = Handler(midi_file='MIDI 文件', vocal_file='人声文件', output_path='输出目录')
handler.compare()
handler.render()
```
会在`输出目录`产生三个文件: `pitch.pdf`、`pitch.png`和 `pitch.mp4`。可以在 [BV1z8411T7vH](https://www.bilibili.com/video/BV1z8411T7vH) 观看样例输出。如果需要`Handler`的完整使用方法，请阅读 [handler.py](/midi_pitch/handler.py) 的注释。

# 要求
- 安装`requirements.txt`中列出的所有库
- 安装`ffmpeg`
- 安装`ImageMagick`

# 快速开始
- 更改`main.py`中的`vocal_file`、`midi_file`为相应的文件位置
- `python3 main.py`

# 推荐步骤
- 生成高质量的人声文件。如果您只有缩混后的声音片段，推荐使用 [Spleeter](https://github.com/deezer/spleeter) 或 [Demucs](https://github.com/facebookresearch/demucs) 分离人声。
- 调用`Handler.compare`检查输出的对比图片`pitch.png`，如果需要调整参数
- 调用`Handler.render`并喝:tea:等一会
- 根据`pitch.mp4`调整项目中的音符