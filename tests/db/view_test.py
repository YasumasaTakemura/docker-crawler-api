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
        res = self.app.get('/v2/')
        self.assertEqual(b'working', res.data)

    def test_get(self):
        res = self.app.get('/v2/get')
        self.assertEqual('hello-world', res.data.decode())

    def test_push(self):
        path = ['hello-world','hello-world2','hello-world3']
        res = self.app.post('/v2/push',data={'path':path})
        res = json.loads(res.data)
        self.assertTrue(res['data'][0]['path'])