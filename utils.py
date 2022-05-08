import os
import tempfile
import uuid


def tmp_dir() -> str:
    return tempfile.gettempdir() + os.sep + "discbridge"


def tmp_random_filename(ext=None):
    if ext is None:
        return tmp_dir() + '/' + uuid.uuid4().hex
    else:
        return tmp_dir() + '/' + uuid.uuid4().hex + '.' + ext

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
