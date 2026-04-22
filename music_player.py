import os
import sys
import time
import select
import termios
import tempfile
import argparse
import io
from contextlib import redirect_stdout
from pathlib import Path

try:
    import pygame
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3
    from ascii_magic.ascii_art import AsciiArt
except ImportError as e:
    print(f"Missing dependency: {e.name}")
    print("Run: pip install pygame mutagen ascii-magic")
    sys.exit(1)

# COLOR Variable
RED    = "\033[91m"
PINK   = "\033[38;5;218m"
RESET  = "\033[0m" # Change the color to default one
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"

# Music Player will only play songs with these extensions
AUDIO_EXTS = {'.mp3', '.m4a', '.ogg', '.wav', '.flac', '.aac', '.aiff'}

# Will print slowly with delay of 0.05 (default). Can change later when calling a function
def slow_print(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)

# USED to read single character input
def getch_nonblocking():
    # READ input
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON) # NOT echo input and read one char at a time
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            ch = sys.stdin.read(1)
        else:
            ch = None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Following functions are for controlling music playback using pygame
def start_playback(path):
    pygame.mixer.music.load(str(path))
    pygame.mixer.music.play()


def pause_playback():
    pygame.mixer.music.pause()


def resume_playback():
    pygame.mixer.music.unpause()


def stop_playback():
    pygame.mixer.music.stop()


def is_playing():
    return pygame.mixer.music.get_busy()


# UI
def show_player(artist, album, track_n, total_track, paused, music_name, elapsed, duration):
    music_percent = elapsed / duration * 100 // 5 if duration > 0 else 0
    line1 = f'| {PINK}{artist if len(artist) < 14 else artist[:11] + "..."}{RESET} \
    - {album if len(album) < 14 else album[:11] + "..."} - {track_n}/{total_track} |\n' #TODO: NEED TO FIX PADDING ISSUES
    line2 = (
        f'| '
        f'{"{blue}> {reset}".format(blue=BLUE, reset=RESET) if not paused else "{red}||{reset}".format(red=RED, reset=RESET)}  '
        f'{(music_name if len(music_name) < 30 else music_name[:27] + "..."):30} |\n'
    )
    line3 = f'| [{"/" * int(music_percent):{20}}] {elapsed//60:02d}:{elapsed - (elapsed // 60 * 60):02d}/{duration//60:02d}:{duration - (duration // 60 * 60):02d} |\n'
    line4 = f'| {YELLOW}[s]{RESET}kip       {CYAN}[p]{RESET}ause       {PINK}[q]{RESET}uit  |\n'
    lines = [
        "┌────────────────────────────────────┐\n",
        line1,
        line2,
        line3,
        line4,
        "└────────────────────────────────────┘\n",
    ]
    for line in lines:
        sys.stdout.write(line)


# Get Metadata using mutagen. If any field is missing, use default values. Duration is in seconds.
def get_metadata(path):
    artist = 'Unknown Artist'
    album = 'Unknown Album'
    title = os.path.splitext(os.path.basename(path))[0]
    duration = 0.0
    try:
        audio = MutagenFile(path)
        if audio is not None:
            duration = audio.info.length
            tags = audio.tags
            if tags is not None:
                if 'TPE1' in tags:
                    artist = str(tags['TPE1'].text[0])
                if 'TALB' in tags:
                    album = str(tags['TALB'].text[0])
                if 'TIT2' in tags:
                    title = str(tags['TIT2'].text[0])
    except Exception:
        pass
    return artist, album, title, duration

# Extract cover art using mutagen. If no cover art found, return None. If found, save to temp file and return AsciiArt object and temp file path.
def extract_cover(path):
    try:
        audio = ID3(path)
        for tag in audio.values():
            if tag.FrameID == 'APIC':
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                tmp.write(tag.data)
                tmp.close()
                return AsciiArt.from_image(tmp.name), tmp.name
    except Exception:
        pass
    return None, None

# Render AsciiArt object to string. If cover_art is None, return empty string.
def render_cover(cover_art, columns=38):
    if cover_art is None:
        return ''
    buf = io.StringIO()
    with redirect_stdout(buf):
        cover_art.to_terminal(columns=columns)
    out = buf.getvalue()
    if out and not out.endswith('\n'):
        out += '\n'
    return out


def load_track(path):
    artist, album, music_name, duration = get_metadata(path)
    cover_art, tmp_path = extract_cover(path)
    cover_str = render_cover(cover_art, columns=38)
    cover_lines = cover_str.count('\n')
    # clean up temp file after rendering
    if tmp_path and os.path.exists(tmp_path):
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return artist, album, music_name, duration, cover_str, cover_lines


def parse_args():
    parser = argparse.ArgumentParser(
        prog='music-player',
        description='A terminal music player with ASCII cover art.',
    )
    parser.add_argument(
        'folder',
        nargs='?',
        default=str(Path.home() / 'Documents' / 'Music' / 'Bad Omens'),
        help='Path to music folder (default: ~/Music)',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    p = Path(args.folder).expanduser().resolve()

    if not p.exists() or not p.is_dir():
        print(f'{RED}Folder not found: {p}{RESET}')
        sys.exit(1)

    paths = sorted([
        c for c in p.iterdir()
        if c.suffix.lower() in AUDIO_EXTS
        and not c.name.startswith('.')
    ])

    if not paths:
        print(f'{RED}No audio files found in {p}{RESET}')
        sys.exit(1)

    pygame.mixer.init()

    total_track = len(paths)
    track_n = 1
    paused = False
    elapsed = 0
    first = True
    PLAYER_LINES = 6

    artist, album, music_name, duration, cover_str, cover_lines = load_track(paths[track_n - 1])
    start_playback(paths[track_n - 1])
    os.system('clear')

    try:
        while True:
            if (not paused) and ((not is_playing()) or (elapsed > duration)):
                stop_playback()
                track_n = track_n + 1 if track_n < total_track else 1
                artist, album, music_name, duration, cover_str, cover_lines = load_track(paths[track_n - 1])
                elapsed = 0
                start_playback(paths[track_n - 1])
                os.system('clear')
                first = True
                continue

            if not first:
                sys.stdout.write(f'\033[{PLAYER_LINES + cover_lines}A')

            show_player(
                artist=artist,
                album=album,
                track_n=track_n,
                total_track=total_track,
                paused=paused,
                music_name=music_name,
                elapsed=elapsed,
                duration=int(duration),
            )

            if first:
                sys.stdout.write(cover_str)
                first = False
            elif cover_lines > 0:
                sys.stdout.write(f'\033[{cover_lines}B')

            sys.stdout.flush()

            # TODO: Need to add change volume and seek and previous music functionality
            ch = getch_nonblocking()
            if ch is not None:
                ch = ch.lower()
                if ch == 'q':
                    stop_playback()
                    slow_print(f'\n\n{RED}Bye Bye :( {RESET}\n')
                    break
                elif ch == 'p':
                    paused = not paused
                    if paused:
                        pause_playback()
                    else:
                        resume_playback()
                elif ch == 's':
                    stop_playback()
                    track_n = track_n + 1 if track_n < total_track else 1
                    artist, album, music_name, duration, cover_str, cover_lines = load_track(paths[track_n - 1])
                    elapsed = 0
                    start_playback(paths[track_n - 1])
                    if paused:
                        pause_playback()
                    os.system('clear')
                    first = True
                    continue

            if not paused:
                elapsed += 1

            time.sleep(1)
    except KeyboardInterrupt:
        stop_playback()
        print(f'\n{RED}Interrupted{RESET}')
    finally:
        try:
            pygame.mixer.quit()
        except Exception:
            pass


if __name__ == '__main__':
    main()