from google.cloud import storage
import base64
from flask import abort
from google.api_core.exceptions import Conflict
import bz2

class Store(object):
    """singleton"""
    _instance = None

    def __init__(self):
        self.connect()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        self.client = storage.Client()

    def create_bucket(self,bucket_name):
        try:
            bucket = self.client.create_bucket(bucket_name)
            return bucket.name
        except Conflict as e :
            abort(400,e)

    def delete_bucket(self,bucket_name):
        """Deletes a bucket. The bucket must be empty."""
        bucket = self.client.get_bucket(bucket_name)
        bucket.delete()
        print('Bucket {} deleted'.format(bucket.name))

    def list_blobs(self,bucket_name):
        """Lists all the blobs in the bucket."""
        # type : (str)=> (list)
        bucket = self.client.get_bucket(bucket_name)
        blobs = bucket.list_blobs()
        res = []
        for blob in blobs:
            res.append(blob.name)
        return res

    def list_blobs_with_prefix(self,bucket_name,prefix,delimiter='/'):
        """Lists all the blobs in the bucket."""
        # type : (str)=> (list)
        bucket = self.client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        res = []
        for blob in blobs:
            res.append(blob.name)
        if delimiter:
            for prefix in blobs.prefixes:
                res.append(prefix)
        return res

    def write(self,bucket_name,enc_key,filename,data):
        bucket = self.client.get_bucket(bucket_name)
        # Encryption key must be an AES256 key represented as a bytestring with
        # 32 bytes. Since it's passed in as a base64 encoded string, it needs
        # to be decoded.
        encryption_key = base64.b64decode(enc_key)
        blob = storage.Blob(filename, bucket,encryption_key=encryption_key)
        data = bz2.compress(data.encode(), 9)
        try:
            blob.upload_from_string(data,content_type='application/gzip')
            return True
        except Exception as e:
            return e

    def read(self,bucket_name,enc_key,filename):
        bucket = self.client.get_bucket(bucket_name)
        # Encryption key must be an AES256 key represented as a bytestring with
        # 32 bytes. Since it's passed in as a base64 encoded string, it needs
        # to be decoded.
        encryption_key = base64.b64decode(enc_key)
        blob = storage.Blob(filename, bucket, encryption_key=encryption_key)
        data = blob.download_to_filename(filename)
        return bz2.decompress(data)
