import os
from os.path import expanduser
home = expanduser("~")

base_dir = '{}/var/log'.format(home)


def create_dir():
    before = ''
    for path in 'var/log'.split('/'):
        before += path
        _dir = os.path.join(home, before)
        if not os.path.isdir(_dir):
            print('CREATE')
            os.mkdir(_dir)
        before += '/'

def create_file(filename, ext):
    dir = os.path.join(base_dir, filename)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    filename = filename + '/' + '.' + ext
    filename = os.path.join(base_dir, filename)
    print(filename)
    if not os.path.isfile(os.path.join(os.getcwd(), filename)):
        with open(filename, 'w'):
            # just create empty file
            print('CREATE_FILE')
            pass
    return filename


def create_offset_file(topic):
    dir = os.path.join(base_dir, topic)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    filename = os.path.join(dir, '.offsets')
    if os.path.isfile(filename):
        return filename
    initial_val = "0"
    with open(filename, 'w') as f:
        f.write(initial_val)
    print('=========')
    print(filename)
    return filename


def get_last_line(fp):
    """
    Get the end of line
    Loop the byte to find specific pattern from the end

    Args:
        fp : file obj for cache
    """
    fp.seek(-1, 2)
    p = fp.tell()
    initial_match = lambda index: (index.startswith(b'0') and index.endswith(b'\n'))
    match = lambda index: (index.startswith(b'\n') and index.endswith(b'\n'))
    while p >= 0:
        fp.seek(p)
        index = fp.read()
        if len(index) > 2 and (initial_match(index) or match(index)):  # length 1 means empty file
            last_index = index.strip().split(b' ')
            return last_index
        p -= 1
