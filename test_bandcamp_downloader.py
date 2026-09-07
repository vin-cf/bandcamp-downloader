import importlib.util
import os
import sys

import pytest

MODULE_PATH = os.path.join(os.path.dirname(__file__), 'bandcamp-downloader.py')

SPEC = importlib.util.spec_from_file_location('bandcamp_downloader', MODULE_PATH)
bcd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bcd)

# The exact problematic album that broke the downloader
TITLE = 'ʅ͡͡͡͡͡͡͡͡͡͡͡(̸̢̛̼̞̭͋ͅ)̸͚̰͛̔̾̀̿͒͂:̴͓̞̑̌̂̆̊͋̀:̸͎̟̯̂̓̌　҉　　　　　͡　͞　͞　͞　҉● ࿀ ●  ࿀  ●　　　҉⃝ 　　　⃝͢ ͞　　　͘　͞⃝̕ ͢　　　　̛　⃝ 　　　̸　̡　　͢⃝̧ 　͡　͡　　̀　̧　̢⃝͜ 　 　҉　　͞　͞　⃝͞ 　͞　͡⃝  ⃝҉҈҉҈҉҈҉҈҉҈҉ :̶̢͙͙͕̠̩͆(̷̮͍͚̫͚͂̍)̵̳̗̊(　̟̞̝̜̙̘̗̖҉̵̴̨̧̢̡̼̻̺̹̳̲̱̰̯̮̭̬̫̪̩̦̥'
ARTIST = '⣎⡇ꉺლ༽இ•̛)ྀ◞ ༎ຶ ༽ৣৢ؞ৢ؞ؖ ꉺლ'


def _build_filename(extension='.zip', filename_format='{artist}/{artist} - {title}'):
    safe_track_info = {
        'title': bcd.sanitize_filename(TITLE),
        'artist': bcd.sanitize_filename(ARTIST),
    }
    return filename_format.format(**safe_track_info) + extension


def test_truncate_keeps_every_component_within_255_bytes():
    truncated = bcd._truncate_path_components(_build_filename())
    for component in truncated.replace('\\', '/').split('/'):
        assert len(component.encode('utf-8')) <= 255


def test_truncate_preserves_extension():
    truncated = bcd._truncate_path_components(_build_filename())
    assert truncated.endswith('.zip')


def test_truncate_is_a_no_op_for_short_names():
    short = os.path.join('artist', 'artist - title')
    assert bcd._truncate_path_components(short) == short


def test_truncate_does_not_split_multi_byte_characters():
    truncated = bcd._truncate_path_components(_build_filename())
    truncated.encode('utf-8')  # must not raise UnicodeDecodeError


def test_truncated_filename_actually_creates_on_disk(tmp_path):
    truncated = bcd._truncate_path_components(_build_filename())
    file_path = os.path.join(str(tmp_path), truncated)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as fh:
        fh.write(b'x')
    assert os.path.exists(file_path)
