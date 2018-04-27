# -*- coding: utf-8 -*-

import os
import logging
import psycopg2
from psycopg2 import ProgrammingError, IntegrityError
import json
import datetime
import pytz
import numpy as np

logger = logging.getLogger('DB_Model')
logger.setLevel(logging.DEBUG)

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
    query = read_query(query_path)
    return query.replace('@table', table)


class CacheFile(object):
    """
    - Data structure of file need to be CSV or TSV
    - Do Not write \n at Last line

    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.size = os.path.getsize(self.file_path)

        if not self.size:
            raise ValueError('not None')

        self.cache = self._gen_fileObj()
        self.offset = 0

    def _gen_fileObj(self):
        self.file_obj = open(self.file_path)
        logger.info('Pointer of file is passed')
        return self.file_obj

    def _fine_line(self, index):
        print()

    def _find_last_line_index(self):
        size = self.size

        while size > 0:
            self.cache.seek(size)
            if self.cache.readline() == '\n':
                self.offset = size + 1
                return self.offset
            size -= 1

    def get_last_line(self):
        offset = self._find_last_line_index()
        self.file_obj.seek(offset)
        return self.file_obj.readline()

    def __len__(self):
        return sum(1 for _ in self.cache)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError('expected int but got {}'.format(type(index)))
        if index >= self.size:
            raise IndexError('index need to be less than {}'.format(self.size))
        if index == -1:
            return self.get_last_line()

        self.cache.seek(0, 0)
        for i, line in enumerate(self.cache):
            if index == i:
                return line.replace('\n', '')


class FileDB(CacheFile):
    """singleton"""
    _instance = None

    def __init__(self, file_path):
        super().__init__(file_path)

    def __new__(cls, file_path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def incr(self):
    #     self.records_cnt += 1
    #
    # def decr(self):
    #     if self.records_cnt >= 0:
    #         self.records_cnt -= 1

    def connect(self):
        self.fp = open(self.file_path)
        logger.info('Pointer of file is passed')
        return self.fp

    def _read_all(self):
        fp = self.fp
        with fp as f:
            return f.readlines()

    def _find_by_path(self, path):
        cache = self.cache
        for i in range(self.size):
            line = cache.next().strip()
            if line == path:
                return line

    def _find_by_index(self, index):
        # (iter ) -> (str)
        cache = self.cache
        for i in range(self.size):
            if i == index:
                line = cache.next().strip()
                return line

    def _concat(self, indexBefore, indexAfter):
        for i in range(self.size):
            if i == index:
                line = self.cache.next().strip()
                return line

    def push(self, path):
        with open(self.file_path, 'a') as f:
            f.write(path)

    def get(self, i=0):
        if i == -1:
            return self._read_all()
        return self._find_by_index(i)

    def remove(self, index=None):
        if not index or -1:
            self.get_last_line()

        self.file_obj.seek(0, 0)

        with open(self.file_path + '_test', 'w') as f:
            for i, line in enumerate(self.file_obj):
                f.write(line)
                if i == index - 1:
                    break


        after = self.file_obj.readlines(index)
        print(after)
        with open(self.file_path + '_test', 'a') as f:
            f.writelines(after)

    def get_until(self, index):
        import itertools
        lines = itertools.islice(self.cache, index)

        return lines


class DBConnector(object):
    """singleton"""
    _instance = None

    def __init__(self):
        with self.connect() as conn:
            self.conn = conn
        self.cur = self.conn.cursor()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
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


class DDO(object):
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


class DMO(object):
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
            value = "({},{},{})".format(
                validate(item['path']),
                validate(item['crawled']),
                validate(item['stored']),
            )

            # no comma at last value
            if i != len(items) - 1:
                value += ', '
            values += value
        sql = '/sql/bulk_insert.sql'
        ts = pytz.timezone('Asia/Tokyo').localize(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        _query = replace_table_name(table, sql)
        _query = _query.replace('@timestamp', ts)
        query = _query.replace('@values', values)
        return self.db.commit(query)

    def show(self, table=base_table):
        # type : () => (str)
        sql = '/sql/show_all_records.sql'
        query = replace_table_name(table, sql)
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_next_path(self, table=base_table):
        # type : () => (str)
        sql = '/sql/get_next_url.sql'
        query = replace_table_name(table, sql)
        self.cur.execute(query)
        data = self.cur.fetchone()
        if data:
            return data[0]

    def update_crawled_status(self, path, table=base_table):
        # type : () => (str)
        sql = '/sql/update_crawled_status.sql'
        _query = replace_table_name(table, sql)
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
                    tmp['value'] = pytz.timezone('Asia/Tokyo').localize(datetime.datetime.now())
                _tmp.update({tmp['name']: tmp['value']})
            urls__.append(_tmp)
        return urls__
