from typing import List

from config import Config
from logger import log
from utils import proxy

from output.abc import Handler
from matrix_client.client import MatrixClient


class MatrixHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        self._client = MatrixClient(config.output.matrix.server)
        self._client.login(config.output.matrix.user, config.output.matrix.password)
        self._room = self._client.join_room(config.output.matrix.room_id)

    def send_message(self, text: str, files: List[str] = []):
        self._room.send_text(text)
        log.message(self.__class__.__name__, text, files)

    def get_name(self) -> str:
        return "matrix"

    def close(self) -> None:
        pass
