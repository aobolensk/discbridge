import logging
from typing import List


class Log:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._log = logging.getLogger("discbridge")
        self._log.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        self._log.addHandler(console_handler)
        self.debug = self._log.debug
        self.info = self._log.info
        self.error = self._log.error
        self.warning = self._log.warning

    def message(self, backend: str, text: str, files: List[str] = list()) -> None:
        self.info("[" + backend + "] Message:\n" + text + (
                (f"(+ {len(files)} file(s): " + ', '.join(files) + ")") if files else ''))


log = Log()
