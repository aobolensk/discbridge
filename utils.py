import os
import tempfile


def tmp_dir() -> str:
    return tempfile.gettempdir() + os.sep + "discbridge"
