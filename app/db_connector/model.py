# -*- coding: utf-8 -*-

import os
import logging
import datetime

logger = logging.getLogger('DB_Model')
logger.setLevel(logging.DEBUG)


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

    Member props:
        log_file       : file path
        size            : file size(counts of log file)
        index_table     : key for line index, value for offsets from top which seek(0,0)
        cache           : dumped log file
        dequeue_counter : offsets of index by in line
    """
    _instance = None

    def __init__(self):
        dir = './log'
        self.log_file = os.path.join(dir, '.log')
        self.index_file = os.path.join(dir, '.index')
        self.timestamp_file = os.path.join(dir, '.timeindex')
        self.offsets_file = os.path.join(dir, '.offsets')
        self.offsets = -1
        self.index_table = dict()
        self.create_file(self.log_file)
        self.create_file(self.index_file)
        self.create_file(self.timestamp_file)
        self.update_size()
        self.gen_cache()
        # self.dequeue_counter = 0

    def __len__(self):
        self.cache.seek(0, 0)
        length = sum(1 for _ in self.cache)
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

    @staticmethod
    def create_file(filename):
        if not os.path.exists(os.path.join(os.getcwd(), filename)):
            with open(filename, 'w'):
                # just create empty file
                pass

    def create_files(self):
        # .log
        if not os.path.exists(os.path.join(os.getcwd(), self.log_file)):
            with open(self.log_file, 'w'):
                # just create empty file
                pass

        # .index
        if not os.path.exists(os.path.join(os.getcwd(), self.index_file)):
            with open(self.index_file, 'w'):
                # just create empty file
                pass

        # .offsets
        initial_val = str(-1)
        if not os.path.exists(self.offsets_file):
            with open(self.offsets_file, 'w') as f:
                f.write(initial_val)

        # .timeindex
        if not os.path.exists(os.path.join(os.getcwd(), self.timestamp_file)):
            with open(self.timestamp_file, 'w'):
                # just create empty file
                pass

    def update_index_table(self):
        index_table = dict()
        self.cache.read(self.offsets)
        with open(self.index_file) as f:
            for i, msg in enumerate(f.readlines()):
                index_table.update({i: msg.split(' ')[0]})
        self.index_table = index_table
        self.cache.seek(0, 0)

    def update_size(self):
        self.size = os.path.getsize(self.log_file)

    @staticmethod
    def get_last_msg(f):
        f.seek(-1, 2)
        p = f.tell()
        while p > 0:
            msg = f.read()
            f.seek(p)
            if len(msg) > 2 and msg.startswith(b'\n') and msg.endswith(b'\n'):
                f.seek(p + 2)
                return f
            p -= 1

    def update_offsets(self):

        if self.offsets == -1:

            with open(self.index_file, 'rb') as f:
                print(len(f.read()))
                if len(f.read()) <= 1:
                    return
                f = self.get_last_msg(f)
                msg = f.read().strip().split(b' ')
                print(msg)
                # f.seek(int(msg[0]))
                # fp.seek(int(msg[0])-18)

                f.seek(34,0)
                print(f.read())
                f.seek(52,0)
                print(f.tell())
                print(f.readline())

    def gen_cache(self):
        """
        Generate cache
        This cache will be used in each methods
        Do not copy or generate list from this cache for memory efficiency
        """
        self.cache = open(self.log_file)
        logger.info('List of Queue is now dumped and you got pointer of file')

    def _find_last_line_index(self):
        size = self.size
        while size > 0:
            self.cache.seek(size)
            if self.cache.readline() == '\n':
                return size + 1
            size -= 1

    def get_last_line(self):
        # get last line as list
        offset = self._find_last_line_index()
        self.cache.seek(offset)
        return self.cache.readline().strip().split(' ')

    def check_dup(self, items):
        cache = self.cache
        self.cache.seek(0, 0)
        lines = list(map(lambda line: line.strip(), cache.readlines()))
        if not lines:
            return items
        lines_no_dup = [item for item in items if item not in set(lines)]
        return lines_no_dup

    def update_index(self, msg: str) -> str:
        """ update offsets and generate a line of index  """
        if self.offsets == -1:  # for initial action
            self.offsets = 0
            return '{} {}\n'.format(self.offsets, len(msg))
        self.offsets = self.offsets + len(msg)
        return '{} {}\n'.format(self.offsets, len(msg))

    def roll_back_commit(self):
        yield

    def commit_index(self, msg: str) -> None:
        # todo : rollback

        # do nothing if no messages passed
        if not msg:
            return

        try:
            with open(self.index_file, 'a') as f:
                msg = self.update_index(msg)
                f.write(msg)
            with open(self.timestamp_file, 'a') as f:
                msg = '{} {}\n'.format(self.offsets, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                f.write(msg)
            self.gen_cache()
            self.update_index_table()
        except Exception as e:
            raise Exception(e)

    def commit(self, msg: str) -> None:
        # todo : rollback
        # self.roll_back_commit(self.offsets,msg)
        with open(self.log_file, 'a') as f:
            f.write(msg + '\n')


class FileDB(object):
    def __init__(self):
        self.conn = self._connect()
        self.cache = self.conn.cache
        self.next_list = []

    @staticmethod
    def _connect():
        """ Connect to some object or DB driver"""
        return CacheFile()

    def _read_all(self):
        """ dump all data as list """
        return self.cache.readlines()

    def _find_by_path(self, path):
        """ find specific line by key """
        self.cache.seek(0, 0)
        for i in range(self.conn.size):
            line = self.cache.__next__().strip()
            if line == path:
                return line

    def _find_by_index(self, index):
        """ find specific line by index """
        # (int) -> (str)
        for i in range(self.conn.size):
            line = self.cache.__next__().strip()
            if i == index:
                return line
        raise IndexError('Out Of Index')

    def push(self, items):
        """ Add line at the end of data """
        if not isinstance(items, list):
            raise TypeError('list is required but got {}'.format(type(items)))
        for msg in self.conn.check_dup(items):
            self.conn.commit(msg)
        self.conn.update_size()
        return True

    def get(self, index=None):
        """ find specific line by key and process dequeue_counter """
        self.cache.seek(0,0)
        print(self.conn.offsets)
        self.conn.update_offsets()

        if index and index > self.conn.offsets:
            raise IndexError('limit of offsets is {} but got {}'.format(self.conn.offsets, index))

        offset = self.conn.offsets
        print(offset)
        if index:
            offset = self.conn.index_table.get(index)
        try:
            self.cache.read(offset)
            msg = self.cache.readline()
            self.conn.commit_index(msg)
            return msg
        except StopIteration as e:
            # rollback counter
            logger.info(e)
            self.conn.roll_back_commit()
            return
        except Exception as e:
            # rollback counter
            logger.info(e)
            self.conn.roll_back_commit()
            raise e
