# video_index/build_index.py
import struct
from typing import List, Tuple

def parse_ivf_frame_headers(ivf_path: str) -> List[Tuple[int, int]]:
    """
    Parses the IVF file to extract frame offsets and lengths.

    Parameters
    ----------
    ivf_path : str
        Path to the IVF video file.

    Returns
    -------
    List[Tuple[int, int]]
        A list of tuples where each tuple is (offset, length) of a frame in bytes.
        Offset is the absolute byte position in the file where the frame data starts,
        length is the size of the frame in bytes.
    """
    frame_positions = []

    with open(ivf_path, 'rb') as f:
        # IVF header is 32 bytes
        header = f.read(32)
        if len(header) != 32 or header[0:4] != b'DKIF':
            raise ValueError("Not a valid IVF file")

        offset = 32  # start of first frame

        while True:
            # Each frame header is 12 bytes:
            # 4 bytes frame size (little-endian)
            # 8 bytes presentation timestamp (ignored here)
            frame_header = f.read(12)
            if len(frame_header) < 12:
                break  # EOF

            frame_size = struct.unpack('<I', frame_header[0:4])[0]

            frame_positions.append((offset + 12, frame_size))

            # Seek over frame payload to next frame header
            f.seek(frame_size, 1)
            offset += 12 + frame_size

    return frame_positions


def write_binary_index(index_path: str, frame_positions: List[Tuple[int, int]]) -> None:
    """
    Write the frame positions to a fixed-width binary index file.

    Parameters
    ----------
    index_path : str
        Path to write the index file.
    frame_positions : List[Tuple[int, int]]
        List of (offset, length) for each frame.
    """
    with open(index_path, 'wb') as f:
        for offset, length in frame_positions:
            # Pack as two little-endian uint64 (16 bytes per frame)
            f.write(struct.pack('<QQ', offset, length))


def build_index(ivf_path: str, index_path: str) -> None:
    """
    Parse IVF video and build the 128-bit frame index file.

    Parameters
    ----------
    ivf_path : str
        Path to the IVF video file.
    index_path : str
        Path where to save the binary index file.
    """
    frame_positions = parse_ivf_frame_headers(ivf_path)
    write_binary_index(index_path, frame_positions)

