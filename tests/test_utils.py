import utils
import unittest
import video_index.utils
from video_index.utils import int_to_bytes_le, bytes_to_int_le

class TestUtils(unittest.TestCase):
    def test_int_to_bytes_le_and_back(self):
        values = [0, 1, 255, 256, 65535, 2**32 - 1, 2**63 - 1]
        lengths = [1, 2, 4, 8]

        for val in values:
            for length in lengths:
                if val < 2**(8 * length):
                    b = int_to_bytes_le(val, length)
                    self.assertEqual(len(b), length)
                    val2 = bytes_to_int_le(b)
                    self.assertEqual(val, val2)

    def test_bytes_to_int_le_invalid(self):
        with self.assertRaises(ValueError):
            # bytes_to_int_le expects bytes, passing int should error
            bytes_to_int_le(123)  # type: ignore

def load_tests(loader, tests, ignore):
    return utils.doctests(video_index.utils, tests)

if __name__ == '__main__':
    unittest.main()
