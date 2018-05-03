from app.db_connector.model import FileDB
from collections import deque
from io import FileIO
import atexit
# data = ( i for i in [(1,'a'),(2,'b'),(3,'c')])
# data = FileIO('lines')
# a = open('lines')


def test(x):
    return x * x
atexit.register(test,10)
atexit.register(test,20)
atexit.register(test,30)
cache = FileDB('lines')
print(cache.conn)
cache.push('e.text')
# print(cache.get(2))
# print(cache.conn.index_table)
# cache.remove(2)

cache2 = FileDB('lines')
print(cache2.conn)
assert cache.conn == cache2.conn
# print(cache2.conn.index_table)
# print(cache[-3])
# print(rs)
# print(cache[-1])

# l = len(cache)
# print(l)