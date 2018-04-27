from app.db_connector.model import FileDB
from collections import deque
from io import FileIO

# data = ( i for i in [(1,'a'),(2,'b'),(3,'c')])
# data = FileIO('lines')
# a = open('lines')



cache = FileDB('lines')
# rs  = cache.get_last_line()
# r = cache.get_until(10)
# print(list(r))
cache.remove(2)
# print(cache[-3])
# print(rs)
# print(cache[-1])

# l = len(cache)
# print(l)