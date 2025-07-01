import utils
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
import video_index.encode_video
from video_index import encode_video

def load_tests(loader, tests, ignore):
    return utils.doctests(video_index.encode_video, tests)


class TestEncodeVideo(unittest.TestCase):
    @patch("subprocess.run")
    def test_encode_av1_intra_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        try:
            encode_video.encode_av1_intra(
                input_path="input.mp4",
                output_path="output.ivf",
                crf=30,
                cpu_used=4,
                tune=None,
            )
        except Exception:
            self.fail("encode_av1_intra raised Exception unexpectedly")

    @patch("subprocess.run")
    def test_encode_av1_intra_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error"
        mock_run.return_value = mock_result

        with self.assertRaises(RuntimeError):
            encode_video.encode_av1_intra(
                input_path="input.mp4",
                output_path="output.ivf",
                crf=30,
                cpu_used=4,
                tune=None,
            )

    @patch("video_index.encode_video.encode_av1_intra")
    @patch("video_index.build_index.build_index")
    def test_main_build_index(self, mock_build_index, mock_encode_av1_intra):
        test_args = [
            "encode_video.py",
            "input.mp4",
            "output.ivf",
            "--build-index",
        ]

        with patch("sys.argv", test_args):
            try:
                encode_video.main()
            except SystemExit:
                pass  # argparse calls sys.exit on success too

        mock_encode_av1_intra.assert_called_once()
        mock_build_index.assert_called_once()

if __name__ == "__main__":
    unittest.main()

