
import asyncio
import datetime
import json

from config import Config
from logger import log
from nio import AsyncClient, MatrixRoom, RoomMessageText
from utils import proxy

from input.abc import Listener


class MatrixListener(Listener):
    def _format_header(self, room: MatrixRoom, event: RoomMessageText):
        result = (
            f"[Matrix] {room.display_name} "
            f"({datetime.datetime.fromtimestamp(event.server_timestamp / 1000)})\n"
        )
        result += f"{event.sender}: "
        return result

    async def _message_callback(self, room: MatrixRoom, event: RoomMessageText):
        text = self._format_header(room, event)
        text += event.body
        self._core.send_message(text)

    async def _login(self):
        await self._client.login(
            self._config.input[self.get_instance_name()].password,
            device_name=self._credentials["device_id"],
            token=self._credentials["access_token"]
        )
        await self._client.sync(timeout=30000)
        self._client.add_event_callback(self._message_callback, RoomMessageText)
        await self._client.sync_forever(timeout=30000, full_state=True)

    def start(self, core, config: Config):
        log.info(f"Input: {self.get_instance_name()} (MatrixListener) start")
        self._core = core
        self._config = config
        with open(config.input[self.get_instance_name()].credentials_json, 'r') as f:
            self._credentials = json.load(f)

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._client = AsyncClient(
            homeserver=self._credentials["homeserver"],
            user=self._credentials["user_id"],
            device_id=self._credentials["device_id"],
            proxy=proxy.http(),
            store_path=config.input[self.get_instance_name()].store_path,
        )
        self._loop.run_until_complete(self._login())

    def get_name(self) -> str:
        return "matrix"
