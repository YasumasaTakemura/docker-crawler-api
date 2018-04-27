import numpy as np
import unittest


class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_numpy_string_array(self):
        data = ['hello','world','!']
        data = np.array(data)
        print(data)
        print(data.dtype)
