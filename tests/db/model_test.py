import unittest
import main
from app.db_connector.model import DBConnector,DDL,DML
import os


class TestDBConnection(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()
        # create table if not exist
        # self.app.post('/v2/create_table')
        # self.assertEqual(b'table created' or b'no tables created', res.data)

    def tearDown(self):
        pass

    def test_update_crawled_status(self):
        db = DBConnector()
        dml = DML(db)
        path = 'Restaurant_Review-g298283-d10161810-Reviews-Kayu_Puti-Langkawi_Langkawi_District_Kedah'
        res = dml.update_crawled_status(path=path)
        print(res)

