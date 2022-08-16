import asyncio
import json
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
        with open(config.output[self.get_instance_name()].credentials_json, 'r') as f:
            self._credentials = json.load(f)

        self._client = AsyncClient(
            homeserver=self._credentials["homeserver"],
            user=self._credentials["user_id"],
            device_id=self._credentials["device_id"],
            proxy=proxy.http(),
            store_path=config.output[self.get_instance_name()].store_path,
        )
        self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self._login())

    async def _login(self):
        await self._client.login(
            self._config.output[self.get_instance_name()].password,
            device_name=self._credentials["device_id"],
            token=self._credentials["access_token"]
        )
        resp = await self._client.sync(full_state=True)

    async def _send_message_impl(self, text):
        await self._client.room_send(
            room_id=self._config.output[self.get_instance_name()].room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": text},
            ignore_unverified_devices=True,
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
