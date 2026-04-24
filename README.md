# LazyTunes

A small terminal music player, written in Python. The name is inspired by [LazyGit](https://github.com/jesseduffield/lazygit).

## About

I wrote this during the internet blackout in Iran. a side project to keep myself busy while the connection was down.

A friend pushed me, basically told me to chill, sit down, and just start coding (idk if I'm allowed to say their name, so I'll leave it at a big thank you ♥). Most of the code was written WITHOUT AI :) wanted this one to be all me fr. I hope you enjoy using it.

## Requirements

- macOS or Linux (uses Unix-only terminal features — won't run on Windows) - TODO: ADD Windows version too. :)
- Python 3

## Installation

1. Put `music_player.py` and `requirements.txt` in a folder of your choice.
2. Open a terminal in that folder and run:
   ```
   pip3 install -r requirements.txt
   ```
   On macOS, if `python3` or `pip3` isn't installed yet, macOS will offer to install the Command Line Tools the first time you run the command — just click "Install".

## Usage

Put your music files (`.mp3`, `.m4a`, `.flac`, `.wav`, `.ogg`, `.aac`, `.aiff`) into your `~/Music` folder and run:

```
python3 music_player.py
```

To play from a different folder:

```
python3 music_player.py /path/to/your/folder
```

## Hotkeys

| Key | Action |
|-----|--------|
| `p` | Pause / resume |
| `s` | Skip to next track |
| `b` | Go back to previous track |
| `,` | Seek backward 5 seconds |
| `.` | Seek forward 5 seconds |
| `-` | Volume down |
| `=` | Volume up |
| `q` | Quit |
