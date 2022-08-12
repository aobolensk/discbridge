import abc
from typing import List

from config import Config


class Handler(abc.ABC):
    def __init__(self, instance_name: str) -> None:
        super().__init__()
        self._instance_name = instance_name

    def init(self, core, config: Config) -> None:
        pass

    def close(self) -> None:
        pass

    def send_message(self, text: str, files: List[str]):
        pass

    def get_name(self) -> str:
        pass

    def get_instance_name(self) -> str:
        return self._instance_name
