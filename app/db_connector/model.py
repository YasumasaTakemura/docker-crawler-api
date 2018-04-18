# -*- coding: utf-8 -*-

import os
import logging
import psycopg2
from psycopg2 import ProgrammingError, IntegrityError
import json
import datetime

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


def replace_table_name(table, sql):
    query_path = base_dir + sql
    _query = read_query(query_path)
    return _query.replace('@table', table)


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
        database = os.environ.get('DATABASE_NAME')
        if not all([user, password, host]):
            logger.error('check required variables are set')
            raise ValueError('check required variables are set')
        return psycopg2.connect(
            user=user,
            password=password,
            host=host,
            database=database,
        )

    def commit(self, query):
        """ do execute and commit at once """
        try:
            self.cur.execute(query)
            self.conn.commit()
            return True
        except IntegrityError:
            # in case record is duplicated
            return True
        except ProgrammingError as e:
            self.conn.rollback()
            logger.error(e)
        except Exception as e:
            logging.error(e)
            self.cur.close()
            self.conn.close()
            raise e


class DDL(object):
    def __init__(self, db):
        self.db = db

    def create_table_crawler(self, table='crawler'):
        _query = read_query(base_dir + '/sql/create_table_crawler.sql')
        query = _query.replace('@table', table)
        result = self.db.commit(query)
        return result

    def _drop_table(self, table='crawler'):
        """ use ONLY FOR unittest """
        query = read_query(base_dir + '/sql/drop_table_crawler.sql')
        result = self.db.commit(query)


class DML(object):
    base_table = 'crawler'

    def __init__(self, db):
        self.db = db
        self.cur = db.cur

    def push_paths(self, items, table='crawler'):
        # type : (List[Dict[Any]]) => ()
        """
        insert path extracted from html　
        this function is called after "apply_fields"
        """

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
        sql = '/sql/bulk_insert.sql'
        _query = replace_table_name(table,sql)
        query = _query.replace('@items', values)
        return self.db.commit(query)

    def show(self, table=base_table):
        # type : () => (str)
        sql = '/sql/show_all_records.sql'
        query = replace_table_name(table,sql)
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_next_path(self, table=base_table):
        # type : () => (str)
        sql = '/sql/get_next_url.sql'
        query = replace_table_name(table,sql)
        self.cur.execute(query)
        try:
            return self.cur.fetchone()[0]
        except IndexError as e:
            logger.error(e)
            raise IndexError(e)

    def update_crawled_status(self, path, table=base_table):
        # type : () => (str)
        sql = '/sql/update_crawled_status.sql'
        _query = replace_table_name(table,sql)
        query = _query.replace('@path', path)
        return self.db.commit(query)

    def apply_fields(self, urls):
        # type : (List[str]) => (List[str])
        # generate record ruled by schema/crawler.json
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
