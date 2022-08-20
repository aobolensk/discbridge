
import asyncio
import datetime
import json
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import aiofiles
from config import Config
from logger import log
from nio import (AsyncClient, MatrixRoom, RoomEncryptedMedia, RoomMessage,
                 RoomMessageMedia, RoomMessageText, crypto)
from utils import proxy, tmp_random_filename

from input.abc import Listener

if TYPE_CHECKING:
    from core import Core

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

    async def _media_callback(self, room: MatrixRoom, event: RoomMessage):
        text = self._format_header(room, event)
        mxc_link = urlparse(event.url)
        media_data = (
            await self._client.download(mxc_link.netloc, mxc_link.path.strip("/"))).body
        if event.body == "Voice message":
            extension = "ogg"
        else:
            extension = event.body.split(".")[-1]
        filename = tmp_random_filename(ext=extension)
        async with aiofiles.open(filename, "wb") as f:
            if isinstance(event, RoomMessageMedia):
                await f.write(media_data)
            elif isinstance(event, RoomEncryptedMedia):
                await f.write(
                    crypto.attachments.decrypt_attachment(
                        media_data,
                        event.source["content"]["file"]["key"]["k"],
                        event.source["content"]["file"]["hashes"]["sha256"],
                        event.source["content"]["file"]["iv"]))
        self._core.send_message(text, [filename])

    async def _login(self):
        await self._client.login(
            self._config.input[self.get_instance_name()].password,
            device_name=self._credentials["device_id"],
            token=self._credentials["access_token"]
        )
        await self._client.sync(timeout=30000)
        self._client.add_event_callback(self._message_callback, RoomMessageText)
        self._client.add_event_callback(self._media_callback, RoomMessageMedia)
        self._client.add_event_callback(self._media_callback, RoomEncryptedMedia)
        await self._client.sync_forever(timeout=30000, full_state=True)

    def start(self, core: 'Core', config: Config):
        log.info(f"Input: {self.get_instance_name()} (MatrixListener) start")
        self._core = core
        self._config = config
        with open(config.input[self.get_instance_name()].credentials_json, 'r') as f:
            self._credentials = json.load(f)

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        proxy_setting = proxy.http() if config.input[self.get_instance_name()].proxy else None
        self._client = AsyncClient(
            homeserver=self._credentials["homeserver"],
            user=self._credentials["user_id"],
            device_id=self._credentials["device_id"],
            proxy=proxy_setting,
            store_path=config.input[self.get_instance_name()].store_path,
        )
        self._loop.run_until_complete(self._login())

    def get_name(self) -> str:
        return "matrix"
