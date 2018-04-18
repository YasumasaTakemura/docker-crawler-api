import unittest
from main import app
import os
import json
from env.settings import load_dotenv
load_dotenv()

class TestDBConnection(unittest.TestCase):
    test_table = os.environ['DATABASE_NAME']

    def setUp(self):
        app.testing = True
        self.app = app.test_client()


    def tearDown(self):
        pass

    def test_connection(self):
        res = self.app.get('/')
        self.assertEqual(b'working', res.data)

    # def create_table(self):
    #     res = self.app.post('/create_table')
    #     self.assertEqual(b'table created' or b'no tables created', res.data)

    def test_get_next(self):
        res = self.app.get('/get_next')
        print(res.data)
        self.assertEqual('Restaurant_Review-g308257-d6446731-Reviews-Southbeach_Restaurant-Mana_Island_Mamanuca_Islands', res.data.decode())
    #
    def test_insert(self):
        path = ['Restaurant_Review-g308261-d2485006-Reviews-Tokoriki_Oishii_Teppanyaki-Tokoriki_Island_Mamanuca_Islands']
        res = self.app.post('/push_paths',data={'path':path})
        res = json.loads(res.data)
        self.assertEqual(path[0], res['data'][0]['path'])
    #
    # def test_bulk_insert(self):
    #     paths = ['/test-review-path','/test-review-path2','/test-review-path3']
    #     res = self.app.post('/push_paths', data={'path': paths})
    #     print(res.data)
    #     self.assertEqual(b'paths added', res.data)

    # def test_upload_file(self):
    #     url='upload_file'
    #     bucket_name = os.getenv('BUCKET_NAME')
    #     if not bucket_name:
    #         bucket_name = 'test-bucket-name'
    #     filename = 'Hotel_Review-g308257-d2071436-Reviews-Mana_Lagoon_Backpackers-Mana_Island_Mamanuca_Islands'
    #     data = 'hello,world!!'
    #     payload = {
    #         'bucket_name':bucket_name,
    #         'filename':filename,
    #         'data':data,
    #     }
    #     res = self.app.post(url,data=payload)
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(res.data, '/{}/{}'.format(bucket_name,filename).encode())


    def test_upload(self):
        url='/upload_file'
        bucket_name = os.getenv('BUCKET_NAME')
        if not bucket_name:
            bucket_name = 'test-bucket-yasu'
        filename = 'Hotel_Review-g308257-d2071436-Reviews-Mana_Lagoon_Backpackers-Mana_Island_Mamanuca_Islands'
        data = 'hello,world!!'
        payload = {
            'bucket_name':bucket_name,
            'filename':filename,
            'data':data,
        }
        res = self.app.post(url,data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, '/{}/{}'.format(bucket_name,filename).encode())