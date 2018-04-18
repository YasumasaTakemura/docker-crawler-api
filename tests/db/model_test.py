import unittest
import main
from env.settings import load_dotenv
from app.db_connector.model import DBConnector, DDL, DML
import json
import os

load_dotenv()

class TestDBConnection(unittest.TestCase):
    test_table = os.environ['DATABASE_NAME']

    @classmethod
    def setUpClass(cls):
        db = DBConnector()
        ddl = DDL(db)
        ddl.create_table_crawler(table=cls.test_table)

    def setUp(self):
        self.app = main.app.test_client()
        self.db = DBConnector()

    def tearDown(self):
        pass

    def test_update_crawled_status(self):
        dml = DML(self.db)
        path = 'Restaurant_Review-g298283-d10161810-Reviews-Kayu_Puti-Langkawi_Langkawi_District_Kedah'
        res = dml.update_crawled_status(path=path, table=self.test_table)
        # print(res)

    def test_show_all(self):
        dml = DML(self.db)
        res = dml.show()
        # res = dml.show(table=self.test_table)
        print(json.dumps(res))

    def test_bulk_insert(self):
        path = [
            'Restaurant_Review-g298283-d10161810-Reviews-Kayu_Puti-Langkawi_Langkawi_District_Kedah',
            'Restaurant_Review-g308257-d6446731-Reviews-Southbeach_Restaurant-Mana_Island_Mamanuca_Islands',
            'Restaurant_Review-g308257-d13142558-Reviews-Mana_Lagoon_Restaurant-Mana_Island_Mamanuca_Islands'
        ]
        dml = DML(self.db)
        records = dml.apply_fields(path)
        res = dml.push_paths(records, table=self.test_table)
        # print(res)
