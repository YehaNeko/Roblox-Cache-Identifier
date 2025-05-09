from __future__ import annotations

__all__ = ('identify_content', 'mp_identify')

import os
import struct
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


# Constants
ROBLOX_CACHE_PATH: Final[Path] = Path('~/AppData/Local/Temp/Roblox/http').expanduser()


# Parser constants
REDIRECT_CODES: Final[set[int]] = {301, 302, 303, 307, 308}
MAGIC_NUMBER_ZSTD: Final[int] = 0xFD2FB528
MAGIC_NUMBER_VIDEO_FRAME: Final[list[int]] = [0x1A, 0x45, 0xDF, 0xA3]
DEFAULT_PREVIEW_LENGTH: Final[int] = 48


def identify_content(filepath: Path) -> str:
    with filepath.open('rb') as f:
        # Read the initial header and enough data for all checks
        buffer: bytes = f.read(1400)

    initial_header = buffer[:4]

    # Check initial header
    if initial_header == b'BXBR':
        return 'BXBR'
    elif initial_header != b'RBXH':
        return 'Unknown Header'

    # Unpack link_len
    if len(buffer) < 12:
        return 'Unknown (Short)'
    link_len: int = struct.unpack('<I', buffer[8:12])[0]
    header_offset = 12 + link_len + 1

    # Seek to req_status_code
    req_status_code: int = struct.unpack(
        '<I', buffer[header_offset : header_offset + 4]
    )[0]
    if req_status_code in REDIRECT_CODES:
        return f'Redirect ({req_status_code})'
    elif req_status_code != 200:
        raise ValueError(f'Invalid request status code in file: {req_status_code}')

    # Seek to content
    header_data_offset = header_offset + 4
    header_data_len: int = struct.unpack(
        '<I', buffer[header_data_offset : header_data_offset + 4]
    )[0]

    file_size_offset = header_data_offset + 8
    file_size: int = struct.unpack(
        '<I', buffer[file_size_offset : file_size_offset + 4]
    )[0]

    # Read content
    content_offset = file_size_offset + 12 + header_data_len
    content = buffer[
        content_offset : content_offset + min(DEFAULT_PREVIEW_LENGTH, file_size)
    ]
    if not content:
        return 'Unknown (Empty)'

    # Detect file type
    if content.startswith(b'version'):
        v = content[8:12]
        return f'Mesh (v{v.decode('utf-8')})'

    elif content.startswith(b'\xabKTX 11'):
        return 'Khronos Texture'

    elif content.startswith(b'\x89PNG'):
        return 'PNG'

    elif content.startswith(b'RIFF') and b'WEBP' in content:
        return 'WebP'

    elif content.startswith(b'<roblox!'):
        return 'RBXM'

    elif content.startswith(b'OggS'):
        return 'OGG'

    elif content.startswith(b'<roblox xml'):
        return 'XML'

    elif content.startswith((b'GIF87a', b'GIF89a')):
        return 'GIF'

    elif b'JFIF' in content or b'Exif' in content:
        return 'JFIF'

    elif content.startswith((b'ID3', b'\xff\xe0')):
        return 'MP3'

    elif content.startswith(b'#EXTM3U'):
        return 'EXTM3U'

    elif content.startswith(b'{"translations"'):
        return 'Translation List JSON'

    elif b'{"locale":"' in content:
        return 'Translation'

    elif b'"name": "' in content:
        return 'Font List'

    elif b'{"applicationSettings' in content:
        return 'FFlags JSON'

    elif b'{"version' in content:
        return 'Client Version JSON'

    elif b'GDEF' in content or b'GPOS' in content or b'GSUB' in content:
        return 'OpenType Font'

    elif len(content) >= 4 and struct.unpack('<I', content[:4])[0] == MAGIC_NUMBER_ZSTD:
        return 'Zstandard Data'

    elif len(content) >= 4 and list(content[:4]) == MAGIC_NUMBER_VIDEO_FRAME:
        return 'VideoFrame Segment'

    else:
        return 'Unknown'


def mp_identify() -> list[str]:
    with ProcessPoolExecutor(max_workers=os.process_cpu_count()) as e:
        results = list(
            e.map(identify_content, ROBLOX_CACHE_PATH.iterdir(), chunksize=500)
        )
        return results
