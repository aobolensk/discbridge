import abc
import threading

from config import Config
from logger import log


class Listener(abc.ABC):
    def __init__(self, instance_name: str) -> None:
        super().__init__()
        self._instance_name = instance_name

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

    def get_instance_name(self) -> str:
        return self._instance_name
