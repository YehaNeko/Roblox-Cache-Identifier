from __future__ import annotations

__all__ = ('identify_content',)

import os
import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

# Constants
REDIRECT_CODES: Final[set[int]] = {301, 302, 303, 307, 308}
MAGIC_NUMBER_ZSTD: Final[int] = 0xFD2FB528
MAGIC_NUMBER_VIDEO_FRAME: Final[list[int]] = [0x1A, 0x45, 0xDF, 0xA3]
DEFAULT_PREVIEW_LENGTH: Final[int] = 48


def identify_content(filepath: Path) -> str:
    with open(filepath, 'rb') as f:
        # Read the initial header and enough data for all checks
        buffer: bytes = f.read(12)
        initial_header = buffer[:4]

        # Check initial header
        if initial_header == b'BXBR':
            return 'BXBR'
        elif initial_header != b'RBXH':
            return 'Unknown Header'

        # Unpack link_len
        if len(buffer) < 12:
            return 'Unknown'
        link_len: int = struct.unpack('<I', buffer[8:12])[0]
        header_offset = 12 + link_len + 1

        # Seek to req_status_code
        f.seek(header_offset)
        req_status_code: int = struct.unpack('<I', f.read(4))[0]
        if req_status_code in REDIRECT_CODES:
            return f'Redirect ({req_status_code})'
        elif req_status_code != 200:
            raise ValueError(f'Invalid request status code in file: {req_status_code}')

        # Seek to content
        header_data_len: int = struct.unpack('<I', f.read(4))[0]
        f.seek(4, os.SEEK_CUR)
        file_size: int = struct.unpack('<I', f.read(4))[0]
        f.seek(8 + header_data_len, os.SEEK_CUR)

        # Read content
        content = f.read(min(file_size, DEFAULT_PREVIEW_LENGTH))
        if not content:
            return 'Unknown'

        # Detect file type
        if content.startswith(b'version'):
            v = content[8:12]
            return f'Mesh (v{v.decode('utf-8')})'

        elif content.startswith(b'\xabKTX 11'):
            return 'Khronos Texture'

        elif content.startswith(b'\x89PNG'):
            return 'PNG'

        # todo: webp not needed maybe
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

        elif (
            len(content) >= 4
            and struct.unpack('<I', content[:4])[0] == MAGIC_NUMBER_ZSTD
        ):
            return 'Zstandard Data'

        elif len(content) >= 4 and list(content[:4]) == MAGIC_NUMBER_VIDEO_FRAME:
            return 'VideoFrame Segment'

        else:
            return 'Unknown'
