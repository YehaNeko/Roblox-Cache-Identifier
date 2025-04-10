import os
import struct

#constants
REDIRECT_CODES = {301, 302, 303, 307, 308}
MAGIC_NUMBER_ZSTD = 0xFD2FB528
MAGIC_NUMBER_VIDEO_FRAME = [0x1A, 0x45, 0xDF, 0xA3]
DEFAULT_PREVIEW_LENGTH = 48

def identify_content(filepath):
    try:
        with open(filepath, 'rb') as f:
            buffer = f.read(DEFAULT_PREVIEW_LENGTH)
            if buffer[:4] != b"RBXH":
                return "Unknown Header"

            f.seek(8)
            link_len = struct.unpack('<I', f.read(4))[0]
            f.seek(12 + link_len + 1)
            req_status_code = struct.unpack('<I', f.read(4))[0]

            if req_status_code in REDIRECT_CODES:
                return f"Redirect ({req_status_code})"
            elif req_status_code != 200:
                return f"Error ({req_status_code})"

            header_data_len = struct.unpack('<I', f.read(4))[0]
            f.seek(4, os.SEEK_CUR)
            file_size = struct.unpack('<I', f.read(4))[0]
            f.seek(8 + header_data_len, os.SEEK_CUR)

            cont = f.read(min(file_size, DEFAULT_PREVIEW_LENGTH))
            begin = cont.decode('utf-8', errors='ignore')

            if "<roblox!" in begin:
                return "RBXM"
            elif "<roblox xml" in begin:
                return "XML"
            elif "version" in begin and "\"version" not in begin:
                return f"Mesh (v{cont[:12].decode('utf-8')[8:]})"
            elif begin.startswith("{\"translations"):
                return "Translation List JSON"
            elif "{\"locale\":\"" in begin:
                return "Translation"
            elif "PNG\r\n" in begin:
                return "PNG"
            elif begin.startswith(("GIF87a", "GIF89a")):
                return "GIF"
            elif "JFIF" in begin or "Exif" in begin:
                return "JFIF"
            elif begin.startswith("RIFF") and "WEBP" in begin:
                return "WebP"
            elif begin.startswith("OggS"):
                return "OGG"
            elif begin.startswith("ID3") or (len(cont) > 2 and (cont[0] & 0xFF) == 0xFF and (cont[1] & 0xE0) == 0xE0):
                return "MP3"
            elif "KTX 11" in begin:
                return "Khronos Texture"
            elif begin.startswith("#EXTM3U"):
                return "EXTM3U"
            elif "\"name\": \"" in begin:
                return "Font List"
            elif "{\"applicationSettings" in begin:
                return "FFlags JSON"
            elif "{\"version" in begin:
                return "Client Version JSON"
            elif "GDEF" in begin or "GPOS" in begin or "GSUB" in begin:
                return "OpenType Font"
            elif len(cont) >= 4 and struct.unpack('<I', cont[:4])[0] == MAGIC_NUMBER_ZSTD:
                return "Zstandard Data"
            elif len(cont) >= 4 and bytes(cont[:4]) == bytes(MAGIC_NUMBER_VIDEO_FRAME):
                return "VideoFrame Segment"
            else:
                return "Unknown"

    except FileNotFoundError:
        return "Error: File not found"
    except struct.error:
        return "Error: Invalid binary structure"
    except Exception as e:
        return f"Error: {str(e)}"

#file_type = identify_content(r"C:\Users\markg\Desktop\FleaGUI\ffdf82a12c12ff10d21deb998f1837d1")
#print(file_type)
