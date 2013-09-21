import os.path
import errno
import json


cache_dir = os.path.abspath(os.path.expanduser('~/.lipy/cache'))


def get_cache_dir():
    global cache_dir

    try:
        os.makedirs(cache_dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

        if not os.path.isdir(cache_dir):
            raise

    return cache_dir


def get_cache_filename(file_name):
    return os.path.join(
        get_cache_dir(),
        file_name
    )


def write_to_cache(file_name, result):
    with open(get_cache_filename(file_name), 'wb') as fp:
        fp.write(json.dumps(result))


def read_from_cache(name):
    with open(get_cache_filename(name), 'rb') as fp:
        return json.loads(fp.read())
