# LazyTunes

A small terminal music player, written in Python. The name is inspired by [LazyGit](https://github.com/jesseduffield/lazygit).

<img width="472" height="513" alt="Screenshot 2026-04-25 at 02 38 13" src="https://github.com/user-attachments/assets/33e393f1-cf5e-48ad-be3a-c9aba28cae32" />

## About

I wrote this during the internet blackout in Iran. a side project to keep myself busy while the connection was down.

A friend pushed me. told me to chill, sit down, and just start coding. So I did.

Huge thanks to Lia for that push ♥
Seriously, this wouldn’t exist without you.

Most of the code was written WITHOUT AI :) wanted this one to be all me fr. I hope you enjoy using it.

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

## TODO

- [ ] Shuffle toggle (hotkey `r`)
- [ ] Repeat current track (hotkey `l`)
- [ ] Mute toggle (hotkey `m`)
- [ ] Track list view — press a key to browse all songs, arrow keys to pick
- [ ] Package as pip installable so users can just run `lazytunes`
- [ ] Windows support
