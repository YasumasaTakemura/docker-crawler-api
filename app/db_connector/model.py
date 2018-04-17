# -*- coding: utf-8 -*-

import os
import logging
import psycopg2
from psycopg2 import ProgrammingError, IntegrityError
import json
import datetime
from flask import abort
logger = logging.getLogger('DB_Model')


base_dir = '{}/app/db_connector'.format(os.getcwd())

def read_query(filename):
    ext = '.sql'
    if not filename.endswith(ext):
        filename = filename + ext

    with open(filename) as f:
        return f.read()


def validate(value):
    """ validate value then fit by sql format """
    if isinstance(value, str):
        return "'{}'".format(value)
    if isinstance(value, datetime.datetime):
        # to_timestamp() is required to insert as timestamp
        return "to_timestamp('{}', 'yyyy-mm-dd hh24:mi:ss')".format(value)
    if value is None:
        return 'NULL'
    return value


class DBConnector(object):
    """singleton"""
    _instance = None

    def __init__(self):
        with self._start_connection() as conn:
            self.conn = conn
        self.cur = self.conn.cursor()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _start_connection(self):
        """ start connect DB"""
        user = os.environ.get('PG_USER')
        password = os.getenv('PG_PASSWORD')
        host = os.getenv('PG_HOST')
        if not all([user, password, host]):
            abort(400, 'check required variables are set')
        return psycopg2.connect(
            user=user,
            password=password,
            host=host,
        )

    def commit(self, query):
        """ do execute and commit at once """
        self.cur.execute(query)
        try:
            self.conn.commit()
            return True
        except IntegrityError:
            # in case record is duplicated
            return True
        except ProgrammingError as e:
            logging.error(e)
            self.cur.close()
            self.conn.close()
            abort(400, e)
        except Exception as e:
            logging.error(e)
            self.cur.close()
            self.conn.close()
            abort(400, e)


class DDL(object):
    def __init__(self, db):
        self.db = db

    def create_table_crawler(self, table='crawler'):
        query = read_query(base_dir + '/sql/create_table_crawler.sql')
        result = self.db.commit(query)
        return result

    def _drop_table(self, table='crawler'):
        """ use ONLY FOR unittest """
        query = read_query(base_dir + '/sql/drop_table_crawler.sql')
        result = self.db.commit(query)


class DML(object):
    def __init__(self, db):
        self.db = db
        self.cur = db.cur

    def push_paths(self, items):
        # type : (List[Dict[Any]]) => ()
        """ insert path extracted from html　"""

        values = ''
        for i, item in enumerate(items):
            value = "({},{},{},{},{},{})".format(
                validate(item['path']),
                validate(item['crawled']),
                validate(item['stored']),
                validate(item['crawled_at']),
                validate(item['created_at']),
                validate(item['updated_at']),
            )

            # no comma at last value
            if i != len(items) - 1:
                value += ', '
            values += value
        query = read_query(base_dir + '/sql/bulk_insert.sql')
        query = query.replace('@items', values)
        return self.db.commit(query)

    def show(self):
        # type : () => (str)
        query = read_query(base_dir + '/sql/show_all_records.sql')
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_next_path(self):
        # type : () => (str)
        query = read_query(base_dir + '/sql/get_next_url.sql')
        self.cur.execute(query)
        return self.cur.fetchone()[0]

    def update_crawled_status(self,path):
        # type : () => (str)
        query = read_query(base_dir + '/sql/update_crawled_status.sql')
        query = query.replace('@path', path)
        self.cur.execute(query)
        return self.cur.fetchone()[0]

    def apply_fields(self, urls):
        # type : (List[str]) => (List[str])
        # generate record ruled by schema
        with open(base_dir + '/schema/crawler.json') as f:
            file = f.read()
            template = json.loads(file)

        urls__ = []
        for url in urls:
            _tmp = {}
            for tmp in template:
                if tmp['name'] == 'path':
                    tmp['value'] = url
                if tmp['type'] == 'datetime' and tmp['value']:
                    tmp['value'] = datetime.datetime.now()
                _tmp.update({tmp['name']: tmp['value']})
            urls__.append(_tmp)
        return urls__
