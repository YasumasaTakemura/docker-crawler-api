# coding:utf-8
import unittest
import json
from main import app
import mock
from google.cloud import storage
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


class TestDB(unittest.TestCase):
    def setUp(self):
        client = storage.Client('PROJECT')
        print(client)


    def tearDown(self):
       pass

    def test_connection(self):
        pass

if __name__ == '__main__':
    unittest.main()
