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
        file_path       : file path
        size            : file size(counts of log file)
        index_table     : key for line index, value for offsets from top which seek(0,0)
        cache           : dumped log file
        dequeue_counter : offsets of index by in line
    """
    _instance = None

    def __init__(self):
        self.file_path = 'url_pile'
        self.file_path_s = 'url_pile.status'
        self.offsets_filename = 'offsets'
        self.create_files()
        self.update_size()
        self.gen_cache()
        self.dequeue_counter = 0

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

    def create_files(self):

        # url_pile
        if not os.path.exists(os.path.join(os.getcwd(), self.file_path)):
            with open(self.file_path, 'w'):
                pass
        if not os.path.exists(os.path.join(os.getcwd(), self.file_path_s)):
            with open(self.file_path_s, 'w'):
                pass

        # offsets
        initial_val = str(-1)
        if not os.path.exists(self.offsets_filename):
            with open(self.offsets_filename, 'w') as f:
                f.write(initial_val)


    def update_size(self):
        self.size = os.path.getsize(self.file_path)

    def gen_cache(self):
        """
        Generate cache
        This cache will be used in each methods
        Do not copy or generate list from this cache for memory efficiency
        """
        self.cache = open(self.file_path)
        logger.info('List of Queue is now dumped and you got pointer of file')

    def update_status(self, line):
        with open(self.file_path_s, 'a') as f:
            f.writelines('{} {}\n'.format(line, datetime.datetime.now()))

    def incr_offsets(self):
        with open(self.offsets_filename) as rf:
            offsets = int(rf.read())
            with open(self.offsets_filename, 'w') as wf:
                offsets += 1
                wf.write(str(offsets))

    def _find_last_line_index(self):
        size = self.size
        while size > 0:
            self.cache.seek(size)
            if self.cache.readline() == '\n':
                return size + 1
            size -= 1

    def get_last_line(self):
        offset = self._find_last_line_index()
        self.cache.seek(offset)
        return self.cache.readline()

    def check_dup(self, items):
        self.cache.seek(0, 0)
        cache = self.cache
        lines = list(map(lambda line: line.strip(), cache.readlines()))

        if not lines:
            return items
        lines_no_dup = [item for item in items if item not in set(lines)]
        return lines_no_dup


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
        self.cache.seek(0, 0)
        for i in range(self.conn.size):
            line = self.cache.__next__().strip()
            if i == index:
                return line
        raise IndexError('Out Of Index')

    def push(self, items):
        """ Add line at the end of data """
        if not isinstance(items, list):
            raise TypeError('list is required but got {}'.format(type(items)))
        lines = [line + '\n' for line in self.conn.check_dup(items)]
        with open(self.conn.file_path, 'a') as f:
            f.writelines(lines)
        self.conn.gen_cache()
        self.conn.update_size()
        return True

    def get(self):
        """ find specific line by key and process dequeue_counter """
        dequeue_counter = self.conn.dequeue_counter  # for a rollback

        try:
            self.cache.seek(0, 0)
            line = self._find_by_index(self.conn.dequeue_counter)
            self.conn.update_status(line)
            self.conn.dequeue_counter += 1
            self.conn.incr_offsets()
            return line
        except StopIteration as e:
            # rollback counter
            logger.info(e)
            self.conn.dequeue_counter = dequeue_counter
            return
        except Exception as e:
            # rollback counter
            logger.info(e)
            self.conn.dequeue_counter = dequeue_counter
            raise e