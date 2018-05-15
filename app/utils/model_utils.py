import logging
import os

HOME = os.getcwd()
os.environ['BASE_DIR'] = os.path.join(HOME, 'var')


def create_dir(dirname: str):
    """ create new dir if does not exist """
    _dir = os.path.join(os.environ['BASE_DIR'], dirname)
    try:
        os.makedirs(_dir)
    except FileExistsError as e:
        logging.info(e)
        logging.info(e)
    return _dir


def create_file(filename):
    filename = os.path.join(os.environ['BASE_DIR'], filename)
    if not os.path.isfile(filename):
        with open(filename, 'w'):
            # just create empty file
            logging.info('FILE_CREATED')
    return filename


def create_offset_file(topic, _dir='log'):
    topic_path = os.path.join(_dir, topic)
    dir = os.path.join(os.environ['BASE_DIR'], topic_path)
    if not os.path.isdir(dir):
        os.mkdir(dir)
    filename = os.path.join(dir, 'offsets.log')
    if os.path.isfile(filename):
        return filename
    initial_val = "0"
    with open(filename, 'w') as f:
        f.write(initial_val)
    with open(filename) as f:
        logging.info(f.read())
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
