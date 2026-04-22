import os
import time
import sys
import select
import termios
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path
from mutagen import File
from mutagen.id3 import ID3
from ascii_magic.ascii_art import AsciiArt

os.system('clear')

# COLOR Variable
RED    = "\033[91m"
PINK   = "\033[38;5;218m"
RESET  = "\033[0m" # Change the color to default one
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"

# Will print slowly with delay of 0.05 (default). Can change later when calling a function
def slow_print(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)

def getch_nonblocking():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)
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

def show_player(artist, album, track_n, total_track, paused, music_name, loading_pct, elapsed, duration):
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

def get_metadata(path):
    artist = 'Unknown Artist'
    album = 'Unknown Album'
    title = os.path.splitext(os.path.basename(path))[0]
    duration = 0.0
    try:
        audio = File(path)
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

def extract_cover(path):
    try:
        audio = ID3(path)
        for tag in audio.values():
            if tag.FrameID == 'APIC':
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                tmp.write(tag.data)
                tmp.close()
                return AsciiArt.from_image(tmp.name)
    except Exception:
        pass
    return None

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
    cover_art = extract_cover(path)
    cover_str = render_cover(cover_art, columns=38)
    cover_lines = cover_str.count('\n')
    return artist, album, music_name, duration, cover_str, cover_lines

def main():
    p = Path('/Users/bardia/Documents/Music/Bad Omens')
    paths = []
    for child in p.iterdir():
        paths.append(child)
    total_track = len(paths)
    track_n = 1

    artist, album, music_name, duration, cover_str, cover_lines = load_track(paths[track_n - 1])
    paused = False
    elapsed = 0
    first = True
    PLAYER_LINES = 6

    os.system('clear')

    while True:
        if elapsed > duration:
            if track_n < total_track:
                track_n += 1
            else:
                track_n = 1
            artist, album, music_name, duration, cover_str, cover_lines = load_track(paths[track_n - 1])
            elapsed = 0
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
            loading_pct=0,
            elapsed=elapsed,
            duration=int(duration)
        )

        if first:
            sys.stdout.write(cover_str)
            first = False
        elif cover_lines > 0:
            sys.stdout.write(f'\033[{cover_lines}B')

        sys.stdout.flush()

        ch = getch_nonblocking()
        if ch is not None:
            ch = ch.lower()
            if ch == 'q':
                slow_print(f'\n\n{RED}Bye Bye :( {RESET}\n')
                break
            elif ch == 'p':
                paused = not paused
            elif ch == 's':
                if track_n < total_track:
                    track_n += 1
                else:
                    track_n = 1
                artist, album, music_name, duration, cover_str, cover_lines = load_track(paths[track_n - 1])
                elapsed = 0
                os.system('clear')
                first = True
                continue

        if not paused:
            elapsed += 1

        time.sleep(1)

if __name__ == "__main__":
    main()