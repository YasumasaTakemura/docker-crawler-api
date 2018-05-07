import logging
import os
import json
from flask import request, Blueprint, abort, jsonify
from .model import FileDB
from app.store.store import Store

logger = logging.getLogger('DB_View')
table_name = os.environ.get('DATABASE_NAME') or 'crawler'

app = Blueprint('db', __name__, url_prefix=os.getenv('API_VERSION'))

StorageFileName = 'test'


@app.route('/', methods=['GET', 'POST'])
def working():
    try:
        print(request.json)
    except:
        print(json.loads(request.form))
    else:
        print(request.form)

    return 'working', 200


@app.route('/show/<types>', methods=['GET'])
def show_records(types):

    print(types)

    if types == 'log':
        return jsonify(logs=[])

    if types == 'cnt':
        db = FileDB(StorageFileName)
        cnt = db.conn.dequeue_counter
        return jsonify(dequeue_counter=cnt)
    abort(400, )


@app.route('/get', methods=['GET'])
def get_next():
    db = FileDB(StorageFileName)
    record = db.get()
    return record + '\n' or '', 200


@app.route('/push', methods=['POST'])
def push():
    paths = request.form.getlist('path')
    logger.info(paths)
    db = FileDB(StorageFileName)
    if db.push(paths):
        return jsonify(data=paths), 200
    logger.error('could not push urls')
    abort(400, '')


@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form.get('bucket_name')
    store = Store()
    bucket_name = store.create_bucket(bucket_name=bucket_name)
    if bucket_name:
        return bucket_name, 200
    logger.error('bucket was not created')
    abort(400, '')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    data = request.form
    bucket_name = data.get('bucket_name')
    filename = data.get('filename')
    data = data.get('data')
    # logger.info('/{}/{}'.format(bucket_name, filename))
    store = Store()
    filename = store.write(bucket_name=bucket_name, filename=filename, data=data)
    return filename, 200


@app.route('/upload', methods=['POST'])
def upload():
    data = request.form
    bucket = data.get('bucket_name')
    path = data.get('path')
    data = data.get('data')
    logger.info('{}'.format(path))
    # logger.info('/{}/{}'.format(bucket, path))
    store = Store()
    db = DBConnector()
    dmo = DMO(db)
    dmo.update_crawled_status(path, table_name)
    filename = store.write(bucket_name=bucket, filename=path, data=data)
    if filename:
        return filename, 200
    logger.error('not uploaded')
    abort(400, '')
