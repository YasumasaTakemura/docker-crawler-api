# -*- coding: utf-8 -*-

import os
import logging
import psycopg2
from psycopg2 import ProgrammingError, IntegrityError
import json
import datetime
import pytz

# import numpy as np

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


class SingletonType(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class CacheFile(metaclass=SingletonType):
    """
    This class a extension of Generator which will have len() and get(), and a SINGLETON to manage url queues
    - Data structure of file needs to be CSV or TSV

    """
    _instance = None

    def __init__(self, file_path):
        self.file_path = file_path
        self.size = os.path.getsize(self.file_path)
        self.index_table = {}
        self.cache = self._gen_cache()
        self.offset = 0

    def _gen_cache(self):
        """
        Generate cache
        This cache will be used in each methods
        Do not copy or generate list from this cache for memory efficiency
        """
        self.cache = open(self.file_path,'r+')
        logger.info('List of Queue is now dumped and you got pointer of file')
        return self.cache

    def __init(self):
        """ init format or something """
        pass

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
        self.cache.seek(offset)
        return self.cache.readline()

    def __len__(self):
        self.cache.seek(0, 0)
        length = sum(1 for _ in self.cache)
        # self.cache.seek(0, 0)
        return length

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


class FileDB(object):
    """
    Steps
    1. FileDB(filename)

    """

    def __init__(self, file_path):
        self.conn = self._connect(file_path)
        self.cache = self.conn.cache
        self.size = self.conn.size
        self._create_index_table()

    @staticmethod
    def _connect(file_path):
        """ Connect to some object or DB driver"""
        return CacheFile(file_path)

    def _read_all(self):
        """ dump all data as list """
        return self.cache.readlines()

    def _find_by_path(self, path):
        """ find specific line by key """
        self.cache.seek(0, 0)
        for i in range(self.size):
            line = self.cache.__next__().strip()
            if line == path:
                return line

    def _find_by_index(self, index):
        """ find specific line by index """
        # (iter ) -> (str)
        self.cache.seek(0, 0)
        for i in range(self.size):
            line = self.cache.__next__().strip()
            if i == index:
                return line

    def push(self, items):
        """ add line at the end of data """
        if isinstance(items, str):
            items = list(items)
        created_at = datetime.datetime.now()
        items = map(lambda item: "{} {}".format(item, created_at), items)
        with open(self.conn.file_path, 'a') as f:
            f.write('\n')
            f.writelines(items)
        return True

    def get(self, i=0):
        """ find specific line by key """
        if i == -1:
            return self._read_all()[-1]
        return self._find_by_index(i)

    def _add_remove_flag(self,line , index):
        pass


    def remove(self, index):
        removed_line = ''
        if index > len(self.conn):
            raise IndexError('index error')
        if index < -1:
            raise ValueError('Do not support negative integer except -1')
        # if not index or -1:
        #     self.conn.get_last_line()

        if index == len(self.conn) - 1:
            offsets = len(self.conn) - 2
            print(self.conn.index_table)
            line_index = self.conn.index_table[offsets]
            print('===========')
            print(line_index)
            read_ = self.cache.read(line_index)
            print(read_)
            print(self.cache.tell())

        # # get data to index
        # self.cache.seek(0, 0)
        #
        # with open(self.conn.file_path, 'w') as f:
        #     for i, line in enumerate(self.cache):
        #         print(i,line,index)
        #         if i == index:
        #             print('===========')
        #             print(line)
        #             self.offset = f.tell() + len(line)
        #             removed_line = line
        #             f.write('\n')
        #             break
        #
        # # append data from index + 1 to the last line
        # self.cache.seek(self.offset, 0)
        # with open(self.conn.file_path, 'a') as f:
        #     f.writelines(self.cache)

        return removed_line

    def _create_index_table(self):
        offset = 0
        for i, line in enumerate(self.cache):
            self.conn.index_table.update({i: offset})
            offset += len(line)


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
