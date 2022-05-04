import os
import tempfile


def tmp_dir() -> str:
    return tempfile.gettempdir() + os.sep + "discbridge"

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
