import unittest
import main
import os
from app.db_connector.model import FileDB

class TestDBConnection(unittest.TestCase):

    def setUp(self):
        self.db = FileDB()
        # print(self.db.conn.dequeue_counter)

    def tearDown(self):
        pass


    def test_incr_offsets(self):
        self.db.conn.incr_offsets()


    def test_push(self):
        paths = ['path/1','path/2']
        res = self.db.push(paths)
        self.assertTrue(res)
        res = self.db.conn.dequeue_counter
        print(res)
        self.db.get()
        res = self.db.conn.dequeue_counter
        print(res)


