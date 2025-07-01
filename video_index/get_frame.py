# video_index/get_frame.py
import struct
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs, unquote

import requests


def parse_frame_from_url(url: str) -> Optional[int]:
    """
    Parse the frame number from a URL fragment or query parameter.
    
    Supports URLs with either a #frame=N fragment or ?frame=N query parameter.
    
    Parameters
    ----------
    url : str
        The full URL containing the frame number.
        
    Returns
    -------
    Optional[int]
        The frame number if found, else None.
    """
    parsed = urlparse(url)
    fragment = parsed.fragment
    query = parse_qs(parsed.query)
    
    # Check fragment e.g. #frame=123
    if fragment.startswith("frame="):
        try:
            return int(fragment.split("=", 1)[1])
        except ValueError:
            return None
    
    # Check query parameters e.g. ?frame=123
    if 'frame' in query:
        try:
            return int(query['frame'][0])
        except (ValueError, IndexError):
            return None
    
    return None


def fetch_frame_index_entry(index_url: str, frame_num: int) -> Tuple[int, int]:
    """
    Fetch the binary index entry (offset, length) for the given frame number.
    
    Parameters
    ----------
    index_url : str
        URL to the binary index file.
    frame_num : int
        Frame number to fetch.
        
    Returns
    -------
    Tuple[int, int]
        (offset, length) of the frame in bytes.
        
    Raises
    ------
    RuntimeError
        If unable to fetch or parse the index entry.
    """
    # Each entry is 16 bytes (2x uint64), so calculate range
    byte_start = frame_num * 16
    byte_end = byte_start + 15
    
    headers = {'Range': f'bytes={byte_start}-{byte_end}'}
    resp = requests.get(index_url, headers=headers)
    if resp.status_code != 206:
        raise RuntimeError(f"Failed to fetch index range bytes: {resp.status_code}")
    
    if len(resp.content) != 16:
        raise RuntimeError(f"Index entry size mismatch: expected 16 got {len(resp.content)}")
    
    offset, length = struct.unpack('<QQ', resp.content)
    return offset, length


def fetch_frame_data(video_url: str, offset: int, length: int) -> bytes:
    """
    Fetch the frame bytes from the video using HTTP Range requests.
    
    Parameters
    ----------
    video_url : str
        URL to the video file.
    offset : int
        Byte offset where the frame starts.
    length : int
        Length in bytes of the frame.
        
    Returns
    -------
    bytes
        The raw frame bytes.
        
    Raises
    ------
    RuntimeError
        If the request fails or returns incomplete data.
    """
    byte_start = offset
    byte_end = offset + length - 1
    headers = {'Range': f'bytes={byte_start}-{byte_end}'}
    resp = requests.get(video_url, headers=headers, stream=True)
    
    if resp.status_code != 206:
        raise RuntimeError(f"Failed to fetch frame bytes: {resp.status_code}")
    
    content = resp.content
    if len(content) != length:
        raise RuntimeError(f"Frame data size mismatch: expected {length} got {len(content)}")
    
    return content


def get_frame_from_urls(video_url: str, index_url: str, frame_num: int) -> bytes:
    """
    Get a frame's raw bytes from a video and its index URL.
   
    video_url = "https://storage.googleapis.com/my-bucket/myvideo.ivf"
    index_url = "https://storage.googleapis.com/my-bucket/myvideo.ivf.idx"
    frame_num = 123

    frame_bytes = get_frame_from_urls(video_url, index_url, frame_num)
    # You can now return these bytes directly to a user, or save to disk, etc.
 
    Parameters
    ----------
    video_url : str
        URL to the AV1 intra-only video file.
    index_url : str
        URL to the binary index file.
    frame_num : int
        The frame number to fetch.
        
    Returns
    -------
    bytes
        Raw frame bytes.
    """
    offset, length = fetch_frame_index_entry(index_url, frame_num)
    frame_bytes = fetch_frame_data(video_url, offset, length)
    return frame_bytes

