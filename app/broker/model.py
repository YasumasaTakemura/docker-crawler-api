# -*- coding: utf-8 -*-

import logging
import os

from app.settings import SETTING
from app.utils.model_utils import get_last_line, create_file,create_offset_file

logger = logging.getLogger('DB_Model')
logger.setLevel(logging.DEBUG)


class SingletonType(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class Topic(object):
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

    def __init__(self, topic: str):
        self.log_file = create_file(topic, 'log')
        self.offsets_file = create_offset_file(topic)
        self.index_file = create_file(topic, 'index.log')
        self.ts_file = create_file(topic, 'ts.log')
        self.load()

    def __len__(self):
        self.cache.seek(0, 0)
        length = sum(1 for _ in self.cache)
        return length

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError('expected int but got {}'.format(type(index)))
        if index == -1:
            return get_last_line(self.cache)

        self.cache.seek(0, 0)
        for i, line in enumerate(self.cache):
            if index == i:
                return line.replace('\n', '')

    def load(self):
        """
        Loads data on memory.This cache will be used in each methods.Do not copy or generate list from this cache for memory efficiency
        """
        self.cache = open(self.log_file, 'r')
        logger.info('List of Queue is now dumped and you got pointer of file')

    def check_dup(self, items: list) -> list:
        """ options to applied or not """
        if SETTING.DUPLICATION:
            return items

        cache = self.cache
        lines = list(map(lambda line: line.strip(), cache.readlines()))
        if not lines:
            return items
        lines_no_dup = [item for item in items if item not in set(lines)]
        return lines_no_dup

    def roll_back_commit(self):
        yield

    def commit(self, messages: map) -> list:
        # todo : rollback
        # self.roll_back_commit(self.offsets,msg)
        with open(self.log_file, 'a') as f:
            print('add', messages)
            lines = list(messages)
            f.writelines(lines)
        return lines

    def get_msg(self, offset):
        """ Get a message """
        self.cache.seek(offset)
        return self.cache.readline()

    def push(self, items):
        """ Add line at the end of data """
        if not isinstance(items, list):
            raise TypeError('items is required but got {}'.format(type(items)))
        lines = map(lambda item: item + '\n', self.check_dup(items))
        lines = self.commit(lines)
        return '\n'.join(lines)
