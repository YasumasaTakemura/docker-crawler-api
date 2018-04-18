import unittest
import main
from app.db_connector.model import DBConnector, DDO, DMO
import json
import os

class TestDBConnection(unittest.TestCase):
    test_table = os.environ['DATABASE_NAME']

    @classmethod
    def setUpClass(cls):
        db = DBConnector()
        ddl = DDO(db)
        ddl.create_table_crawler(table=cls.test_table)

    def setUp(self):
        self.app = main.app.test_client()
        self.db = DBConnector()

    def tearDown(self):
        pass

    def test_update_crawled_status(self):
        dml = DMO(self.db)
        path = 'Restaurant_Review-g298283-d10161810-Reviews-Kayu_Puti-Langkawi_Langkawi_District_Kedah'
        res = dml.update_crawled_status(path=path, table=self.test_table)
        # print(res)

    def test_show_all(self):
        dml = DMO(self.db)
        res = dml.show(table=self.test_table)
        # print(res)
        # print(json.dumps(res))

    def test_bulk_insert(self):
        path = [
            'Restaurant_Review-g298283-d10161810-Reviews-Kayu_Puti-Langkawi_Langkawi_District_Kedah',
            'Restaurant_Review-g308257-d6446731-Reviews-Southbeach_Restaurant-Mana_Island_Mamanuca_Islands',
            'Restaurant_Review-g308257-d13142558-Reviews-Mana_Lagoon_Restaurant-Mana_Island_Mamanuca_Islands',
            'Restaurant_Review-g308261-d2485006-Reviews-Tokoriki_Oishii_Teppanyaki-Tokoriki_Island_Mamanuca_Islands'
        ]
        dml = DMO(self.db)
        records = dml.apply_fields(path)
        dml.push_paths(records, table=self.test_table)
        data = dml.show(table=self.test_table)
        for item in data:
            self.assertTrue(item[0] in path)
