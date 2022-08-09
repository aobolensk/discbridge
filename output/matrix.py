import asyncio
import threading
from typing import List

from config import Config
from logger import log
from nio import AsyncClient
from utils import proxy

from output.abc import Handler


class MatrixHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        self._client = AsyncClient(
            homeserver=config.output.matrix.server,
            user=config.output.matrix.user,
            device_id="DISCBRIDGE",
            proxy=proxy.http(),
            )
        self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self._login())

    async def _login(self):
        await self._client.login(self._config.output.matrix.password)

    async def _send_message_impl(self, text):
        await self._client.room_send(
            room_id=self._config.output.matrix.room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": text},
        )

    def _send_message(self, text):
        self._loop.run_until_complete(self._send_message_impl(text))

    def send_message(self, text: str, files: List[str] = []):
        threading.Thread(target=self._send_message, args=(text,)).start()
        log.message(self.__class__.__name__, text, files)

    def get_name(self) -> str:
        return "matrix"

    def close(self) -> None:
        self._loop.close()
