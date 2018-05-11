# -*- coding: utf-8 -*-

import os
import logging
import datetime
from app.settings import SETTING
from app.broker.model import Topic

logger = logging.getLogger('DB_Model')
logger.setLevel(logging.DEBUG)


class SingletonType(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


# class Offset(metaclass=SingletonType):
class Consumer(object):
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
    base_dir = './log'

    def __init__(self, topic: Topic):
        self._offsets = 0
        self.topic = topic
        self.index_file = self.topic.index_file
        self.ts_file = self.topic.ts_file
        self.offsets_file = self.topic.offsets_file
        print(self.offsets_file)
        self.log_file = self.topic.log_file
        # self.index_table = dict()
        # self.update_index_size()

    @property
    def offsets(self):
        with open(self.offsets_file, 'r') as f:
            self._offsets = f.read()
        return int(self._offsets)

    @offsets.setter
    def offsets(self, val):
        with open(self.offsets_file, 'r') as rf:
            offsets_val = int(rf.read())
            with open(self.offsets_file, 'w') as wf:
                offsets_val += val
                wf.write(str(offsets_val))

    def get_msg(self, offsets=None):
        offsets = offsets if offsets else self.offsets
        msg = self.topic.get_msg(offsets)
        print(offsets)
        print(msg)
        return msg

    def commit(self, msg):
        length = len(msg)
        self.offsets = 0 if self.offsets else length
        td = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

        # do nothing if no messages passed
        if not SETTING.ALLOW_EMPTY and not msg:
            return

        try:
            with open(self.index_file, 'a') as f:
                f.write('{}\t{}\n'.format(self.offsets, length))

            with open(self.ts_file, 'a') as f:
                f.write('{}\t{}\n'.format(self.offsets, td))
            return msg
        except Exception as e:
            raise Exception(e)

    def flush(self):
        initial_val = "0"
        with open(self.offsets_file, 'w') as f:
            f.write(initial_val)
        return self.offsets
