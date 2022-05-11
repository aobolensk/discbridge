import abc
from typing import List

from config import Config


class Handler(abc.ABC):
    def __init__(self) -> None:
        super().__init__()

    def init(self, core, config: Config) -> None:
        pass

    def close(self) -> None:
        pass

    def send_message(self, text: str, files: List[str]):
        pass

    def get_name(self) -> str:
        pass

    def get_config_type(self) -> type:
        pass
