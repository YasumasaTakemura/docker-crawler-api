import logging
import os
import json
from flask import request, Blueprint, abort, jsonify
from .model import DBConnector, DMO, DDO
from .model import FileDB
from app.store.store import Store

logger = logging.getLogger('DB_View')
table_name = os.environ.get('DATABASE_NAME') or 'crawler'

app = Blueprint('db', __name__, url_prefix=os.getenv('API_VERSION'))

StorageFileName = 'test'

@app.route('/', methods=['GET','POST'])
def working():
    try:
        print(request.json)
    except:
        print(json.loads(request.form))
    else:
        print(request.form)

    return 'working', 200


@app.route('/create_table', methods=['POST'])
def create_table():
    db = DBConnector()
    ddo = DDO(db)
    try:
        ddo.create_table_crawler()
        return 'table created', 200
    except Exception as e:
        logger.error(e)
        abort(400, 'no tables created')


@app.route('/show_records', methods=['GET'])
def show_records():
    db = DBConnector()
    dmo = DMO(db)
    try:
        res = dmo.show(table=table_name)
        return jsonify(data=res)
    except Exception as e:
        logger.error(e)
        abort(400, )


@app.route('/get', methods=['GET'])
def get_next():
    # db = DBConnector()
    # dmo = DMO(db)
    # path = dmo.get_next_path(table=table_name)
    db = FileDB(StorageFileName)
    record = db.get()
    return record or '', 200
    # return path or '', 200


@app.route('/push_paths', methods=['POST'])
def push_urls():
    paths = request.form.getlist('path')
    logger.info(paths)
    db = DBConnector()
    dmo = DMO(db)
    records = dmo.apply_fields(paths)
    # logger.info('=================')
    # logger.info(records)
    if dmo.push_paths(records, table=table_name):
        return jsonify(data=records), 200
    logger.error('could not push urls')
    abort(400, '')

@app.route('/push', methods=['POST'])
def push():
    paths = request.form.getlist('path')
    logger.info(paths)
    db = FileDB(StorageFileName)
    if db.push(paths):
        return jsonify(data=paths), 200
    logger.error('could not push urls')
    abort(400, '')

@app.route('/remove', methods=['POST'])
def remove():
    index = request.args.get('index')
    db = FileDB(StorageFileName)
    if not index:
        index = len(db.conn) -1
    line = db.remove(index)
    if line:
        return jsonify(data=line), 200
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
