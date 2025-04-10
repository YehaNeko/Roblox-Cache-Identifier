class ByteReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
    
    def read_string(self, length):
        result = self.data[self.pos:self.pos + length].decode('utf-8', errors='ignore')
        self.pos += length
        return result
    
    def read_uint32(self):
        result = int.from_bytes(self.data[self.pos:self.pos + 4], 'little')
        self.pos += 4
        return result
    
    def read_bytes(self, length):
        result = self.data[self.pos:self.pos + length]
        self.pos += length
        return result
    
    def skip(self, length):
        self.pos += length

def identify_content(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        reader = ByteReader(data)
        ident = reader.read_string(4)
        if ident != "RBXH":
            return "Unknown Header"
        
        reader.skip(4)
        link_len = reader.read_uint32()
        reader.read_string(link_len)
        reader.skip(1)
        req_status_code = reader.read_uint32()
        
        if req_status_code in {301, 302, 303, 307, 308}:
            return f"Redirect ({req_status_code})"
        elif req_status_code != 200:
            return f"Error ({req_status_code})"
        
        header_data_len = reader.read_uint32()
        reader.skip(4)
        file_size = reader.read_uint32()
        reader.skip(8 + header_data_len)
        cont = reader.read_bytes(file_size)
        
        begin = cont[:min(48, len(cont))].decode('utf-8', errors='ignore')
        magic = int.from_bytes(cont[:4], 'little') if len(cont) >= 4 else 0
        
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
        elif begin.startswith("GIF87a") or begin.startswith("GIF89a"):
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
        elif magic == 0xFD2FB528:
            return "Zstandard Data"
        elif len(cont) >= 4 and cont[0] == 0x1A and cont[1] == 0x45 and cont[2] == 0xDF and cont[3] == 0xA3:
            return "VideoFrame Segment"
        else:
            return "Unknown"
    except Exception as e:
        return f"Error: {str(e)}"

type = identify_content(r"path")
print(type)