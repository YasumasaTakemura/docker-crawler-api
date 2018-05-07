import unittest
import main
import os

class TestDBConnection(unittest.TestCase):
    test_table = os.environ['DATABASE_NAME']
