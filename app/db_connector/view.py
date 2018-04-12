
import logging
import os
from flask import request, Blueprint, abort, jsonify
from .model import DBConnector, DML, DDL
from app.store.store import Store

app = Blueprint('db', __name__, url_prefix=os.getenv('API_VERSION'))


@app.route('/', methods=['GET'])
def working():
    return 'working'


@app.route('/create_table', methods=['POST'])
def create_table():
    db = DBConnector()
    ddl = DDL(db)
    try:
        ddl.create_table_crawler()
        return 'table created', 200
    except Exception as e:
        logging.error(e)
        abort(400, 'no tables created')


@app.route('/show_records', methods=['GET'])
def show_records():
    db = DBConnector()
    dml = DML(db)
    try:
        res = dml.show()
        return jsonify(data=res)
    except Exception as e:
        logging.error(e)
        abort(400, 'no tables created')


@app.route('/get_next', methods=['GET'])
def get_next():
    db = DBConnector()
    dml = DML(db)
    path = dml.get_next_path()
    return path, 200


@app.route('/push_paths', methods=['POST'])
def push_urls():
    paths = request.form.getlist('path')
    db = DBConnector()
    dml = DML(db)
    records = dml.apply_fields(paths)
    if dml.push_paths(records):
        return 'paths added', 200
    logging.error('could not push urls')
    abort(400, 'could not push urls')


@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form.get('bucket_name')
    store = Store()
    bucket_name = store.create_bucket(bucket_name=bucket_name)
    if bucket_name:
        return bucket_name, 200
    abort(400, 'bucket was not created')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    data = request.form
    bucket_name = data.get('bucket_name')
    filename = data.get('filename')
    data = data.get('data')
    store = Store()
    res = store.write(bucket_name=bucket_name,enc_key=os.getenv('SECRET'),filename=filename,data=data)
    if res:
        return '/' + bucket_name + '/' + filename , 200
    abort(400, 'file was not uploaded')
