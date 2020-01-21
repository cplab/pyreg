import unittest
import os


class TestDestriping(unittest.TestCase):
    def test_complete(self):
        result_folder = '/data/destriped_data/Ex_0_Em_0'

        self.assertEqual(True, os.listdir(result_folder))


if __name__ == '__main__':
    unittest.main()
