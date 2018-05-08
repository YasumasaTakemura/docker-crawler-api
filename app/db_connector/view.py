import logging
import os
import json
from flask import request, Blueprint, abort, jsonify
from .model import FileDB
from app.store.store import Store

logger = logging.getLogger('DB_View')
table_name = os.environ.get('DATABASE_NAME') or 'crawler'

app = Blueprint('db', __name__, url_prefix=os.getenv('API_VERSION'))


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
        db = FileDB()
        cnt = db.conn.dequeue_counter
        return jsonify(dequeue_counter=cnt)
    abort(400, )


@app.route('/get', methods=['GET'])
def get():
    index = request.args.get('index')
    db = FileDB()
    record = db.get(index)
    return record or '', 200


@app.route('/push', methods=['POST'])
def push():
    paths = request.form.getlist('path')
    logger.info(paths)
    db = FileDB()
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