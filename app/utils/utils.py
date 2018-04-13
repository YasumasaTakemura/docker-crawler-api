import os
import base64


def get_enckey():
    key = os.getenv('SECRET')
    if not key:
        return None
    return key


def decrypt_key(key):
    if not key:
        raise ValueError('No Key Passed')
    return base64.b64decode(key)
