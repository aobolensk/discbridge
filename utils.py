import os
import tempfile


def tmp_dir() -> str:
    path = tempfile.gettempdir() + os.sep + "discbridge"
    os.makedirs(path, exist_ok=True)
    return path
