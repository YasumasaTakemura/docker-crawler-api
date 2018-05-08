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

    # def test_push(self):
    #     paths = ['path/1', 'path/2']
    #     res = self.db.push(paths)
    #     self.assertTrue(res)
    #     res = self.db.conn.offsets
    #     print(res)
    #     msg = self.db.get()
    #     self.assertEqual(msg.strip(), paths[0])

    def test_get_last_line(self):
        print('-------------')
        print(self.db.conn.offsets)
        res = self.db.conn.update_offsets()
        print(res)