import abc
import threading
from typing import TYPE_CHECKING

from config import Config
from logger import log

if TYPE_CHECKING:
    from core import Core

class Listener(abc.ABC):
    def __init__(self, instance_name: str) -> None:
        super().__init__()
        self._instance_name = instance_name

    def run(self, core: 'Core', config: Config) -> None:
        try:
            t = threading.Thread(target=self.start, args=(core, config))
            t.setDaemon(True)
            t.start()
        except Exception as e:
            log.error(e)

    def start(self, core: 'Core', config: Config) -> None:
        pass

    def get_name(self) -> str:
        pass

    def get_instance_name(self) -> str:
        return self._instance_name
