import unittest
import main
from app.db_connector.model import DBConnector,DDL
import os


class TestDBConnection(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        # create table if not exist
        self.app.post('/v2/create_table')
        # self.assertEqual(b'table created' or b'no tables created', res.data)

    def tearDown(self):
        pass

    def test_connection(self):
        res = self.app.get('/v2/')
        self.assertEqual(b'working', res.data)

    def create_table(self):
        res = self.app.post('/v2/create_table')
        self.assertEqual(b'table created' or b'no tables created', res.data)

    def test_get_next(self):
        res = self.app.get('/v2/get_next')
        print(res.data)
        self.assertEqual(b'/test-review-path', res.data)

    def test_insert(self):
        path = ['/test-review-path']
        res = self.app.post('/v2/push_paths',data={'path':path})
        print(res.data)
        self.assertEqual(b'paths added', res.data)

    def test_bulk_insert(self):
        paths = ['/test-review-path','/test-review-path2','/test-review-path3']
        res = self.app.post('/v2/push_paths', data={'path': paths})
        print(res.data)
        self.assertEqual(b'paths added', res.data)
