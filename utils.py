import os
import tempfile
import uuid
from typing import Optional


def tmp_dir() -> str:
    return tempfile.gettempdir() + os.sep + "discbridge"


def current_dir_name() -> str:
    return os.path.basename(os.getcwd())


def tmp_random_filename(ext=None):
    if ext is None:
        return tmp_dir() + '/' + uuid.uuid4().hex
    else:
        return tmp_dir() + '/' + uuid.uuid4().hex + '.' + ext


class proxy:
    def http() -> Optional[str]:
        return os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')

    def https() -> Optional[str]:
        return os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def split_by_chunks(message: str, count: int):
    """Split message by chunks with particular size"""
    for i in range(0, len(message), count):
        yield message[i:i + count]
