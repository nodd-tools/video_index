import utils
import unittest
from unittest.mock import patch, MagicMock
import struct
import video_index.get_frame
from video_index.get_frame import (
    parse_frame_from_url,
    fetch_frame_index_entry,
    fetch_frame_data,
    get_frame_from_urls,
)

def load_tests(loader, tests, ignore):
    return utils.doctests(video_index.get_frame, tests)


class TestGetFrame(unittest.TestCase):
    def test_parse_frame_from_url_fragment(self):
        url = "https://example.com/video.ivf#frame=123"
        frame = parse_frame_from_url(url)
        self.assertEqual(frame, 123)

    def test_parse_frame_from_url_query(self):
        url = "https://example.com/video.ivf?frame=456"
        frame = parse_frame_from_url(url)
        self.assertEqual(frame, 456)

    def test_parse_frame_from_url_none(self):
        url = "https://example.com/video.ivf"
        frame = parse_frame_from_url(url)
        self.assertIsNone(frame)

    @patch("video_index.get_frame.requests.get")
    def test_fetch_frame_index_entry(self, mock_get):
        # Mock 16 bytes of binary data for offset=1000, length=500
        mock_response = MagicMock()
        mock_response.status_code = 206
        mock_response.content = struct.pack('<QQ', 1000, 500)
        mock_get.return_value = mock_response

        offset, length = fetch_frame_index_entry("http://fakeindex", 5)
        self.assertEqual(offset, 1000)
        self.assertEqual(length, 500)

    @patch("video_index.get_frame.requests.get")
    def test_fetch_frame_data(self, mock_get):
        frame_bytes = b"frame_data"
        mock_response = MagicMock()
        mock_response.status_code = 206
        mock_response.content = frame_bytes
        mock_get.return_value = mock_response

        data = fetch_frame_data("http://fakevideo", 1000, len(frame_bytes))
        self.assertEqual(data, frame_bytes)

    @patch("video_index.get_frame.requests.get")
    def test_get_frame_from_urls(self, mock_get):
        # Mock index response for frame offset and length
        mock_index_resp = MagicMock()
        mock_index_resp.status_code = 206
        mock_index_resp.content = struct.pack('<QQ', 1000, 9)

        # Mock frame data response
        mock_frame_resp = MagicMock()
        mock_frame_resp.status_code = 206
        mock_frame_resp.content = b"frame_data"

        # requests.get will be called twice: once for index, once for frame data
        mock_get.side_effect = [mock_index_resp, mock_frame_resp]

        frame_bytes = get_frame_from_urls("http://video", "http://index", 7)
        self.assertEqual(frame_bytes, b"frame_data")

if __name__ == "__main__":
    unittest.main()

