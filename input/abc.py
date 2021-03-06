import abc
import threading

from config import Config
from logger import log


class Listener(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    def run(self, core, config: Config):
        try:
            t = threading.Thread(target=self.start, args=(core, config))
            t.setDaemon(True)
            t.start()
        except Exception as e:
            log.error(e)

    def start(self, core, config: Config):
        pass

    def get_name(self) -> str:
        pass
