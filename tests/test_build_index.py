import utils
import unittest
import os
import tempfile
import struct
import video_index.build_index
from video_index import build_index

def load_tests(loader, tests, ignore):
    return utils.doctests(video_index.build_index, tests)

class TestBuildIndex(unittest.TestCase):
    def setUp(self):
        # Create a dummy IVF file with 2 frames:
        # IVF header 32 bytes, then 2 frames each with 12-byte frame header + payload
        self.temp_ivf = tempfile.NamedTemporaryFile(delete=False)
        # IVF header: 'DKIF', version=0, header size=32, fourcc='AV01', width=640, height=480, framerate=30/1, frame count=2
        header = (
            b'DKIF' +                   # signature
            b'\x00\x00' +               # version (2 bytes)
            b'\x20\x00' +               # header size (32 bytes)
            b'AV01' +                   # fourcc
            struct.pack('<HH', 640, 480) +  # width, height
            struct.pack('<II', 30, 1) +     # framerate numerator/denominator
            struct.pack('<I', 2) +           # frame count
            b'\x00' * (32 - 4 - 2 - 2 - 4 - 4 - 4)  # padding
        )
        self.temp_ivf.write(header)
        # Frame 1: size=10 bytes, pts=1
        self.temp_ivf.write(struct.pack('<I', 10))
        self.temp_ivf.write(struct.pack('<Q', 1))
        self.temp_ivf.write(b'A' * 10)
        # Frame 2: size=20 bytes, pts=2
        self.temp_ivf.write(struct.pack('<I', 20))
        self.temp_ivf.write(struct.pack('<Q', 2))
        self.temp_ivf.write(b'B' * 20)
        self.temp_ivf.flush()
        self.temp_ivf.close()

        self.index_path = tempfile.mktemp()

    def tearDown(self):
        try:
            os.remove(self.temp_ivf.name)
        except Exception:
            pass
        try:
            os.remove(self.index_path)
        except Exception:
            pass

    def test_parse_ivf_frame_headers(self):
        frames = build_index.parse_ivf_frame_headers(self.temp_ivf.name)
        self.assertEqual(len(frames), 2)
        # Frame 1 offset should be header + 12 (32 + 12 = 44)
        self.assertEqual(frames[0][0], 44)
        self.assertEqual(frames[0][1], 10)
        # Frame 2 offset should be 44 + 12 + 10 = 66
        self.assertEqual(frames[1][0], 66)
        self.assertEqual(frames[1][1], 20)

    def test_write_and_read_index(self):
        frames = build_index.parse_ivf_frame_headers(self.temp_ivf.name)
        build_index.write_binary_index(self.index_path, frames)

        with open(self.index_path, 'rb') as f:
            content = f.read()
        self.assertEqual(len(content), 2 * 16)  # two frames * 16 bytes each

        # Unpack first entry
        offset1, length1 = struct.unpack('<QQ', content[0:16])
        self.assertEqual(offset1, frames[0][0])
        self.assertEqual(length1, frames[0][1])

        # Unpack second entry
        offset2, length2 = struct.unpack('<QQ', content[16:32])
        self.assertEqual(offset2, frames[1][0])
        self.assertEqual(length2, frames[1][1])

if __name__ == "__main__":
    unittest.main()

