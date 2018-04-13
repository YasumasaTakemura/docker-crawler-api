# coding:utf-8
import unittest
import json
from main import app
import os
import base64
import mock
from app.utils.utils import get_enckey, decrypt_key
from google.cloud import storage
from app.store.store import Store
import requests
from six.moves import http_client


def _make_credentials():
    import google.auth.credentials

    return mock.Mock(spec=google.auth.credentials.Credentials)


def _make_response(status=http_client.OK, content=b'', headers={}):
    response = requests.Response()
    response.status_code = status
    response._content = content
    response.headers = headers
    response.request = requests.Request()
    return response


def _make_json_response(data, status=http_client.OK, headers=None):
    headers = headers or {}
    headers['Content-Type'] = 'application/json'
    return _make_response(
        status=status,
        content=json.dumps(data).encode('utf-8'),
        headers=headers)


def _make_requests_session(responses):
    session = mock.create_autospec(requests.Session, instance=True)
    session.request.side_effect = responses
    return session


class TestVIew(unittest.TestCase):
    def setUp(self):
        app.config['TEST'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass


    def test_write_gcs(self):
        url='upload_file'
        bucket_name = os.getenv('BUCKET_NAME')
        if not bucket_name:
            bucket_name = 'test-bucket-name'
        filename = 'Category_Review-filename'
        data = 'hello,world!!'
        payload = {
            'bucket_name':bucket_name,
            'filename':filename,
            'data':data,
        }
        res = self.app.post(url,data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, '/{}/{}'.format(bucket_name,filename).encode())


if __name__ == '__main__':
    unittest.main()
