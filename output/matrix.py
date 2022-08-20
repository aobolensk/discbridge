import asyncio
import json
import os
import threading
from typing import TYPE_CHECKING, List

import aiofiles
import aiofiles.os
import magic
from config import Config
from logger import log
from nio import AsyncClient
from PIL import Image
from utils import proxy

from output.abc import Handler

if TYPE_CHECKING:
    from core import Core


class MatrixHandler(Handler):
    def init(self, core: 'Core', config: Config) -> None:
        self._core = core
        self._config = config
        with open(config.output[self.get_instance_name()].credentials_json, 'r') as f:
            self._credentials = json.load(f)
        proxy_setting = proxy.http() if config.output[self.get_instance_name()].proxy else None
        self._client = AsyncClient(
            homeserver=self._credentials["homeserver"],
            user=self._credentials["user_id"],
            device_id=self._credentials["device_id"],
            proxy=proxy_setting,
            store_path=config.output[self.get_instance_name()].store_path,
        )
        self._loop = asyncio.new_event_loop()
        self._loop.run_until_complete(self._login())

    async def _login(self) -> None:
        await self._client.login(
            self._config.output[self.get_instance_name()].password,
            device_name=self._credentials["device_id"],
            token=self._credentials["access_token"]
        )
        await self._client.sync(full_state=True)

    async def _send_message_impl(self, text, files):
        await self._client.room_send(
            room_id=self._config.output[self.get_instance_name()].room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": text},
            ignore_unverified_devices=True,
        )
        for file in files:
            mime_type = magic.from_file(file, mime=True)
            file_stat = await aiofiles.os.stat(file)
            async with aiofiles.open(file, "r+b") as f:
                resp, _ = await self._client.upload(
                    f,
                    content_type=mime_type,
                    filename=os.path.basename(file),
                    filesize=file_stat.st_size)
            if mime_type.startswith("image/"):
                im = Image.open(file)
                width, height = im.size
                content = {
                    "body": os.path.basename(file),
                    "info": {
                        "size": file_stat.st_size,
                        "mimetype": mime_type,
                        "thumbnail_info": None,
                        "w": width,
                        "h": height,
                        "thumbnail_url": None,
                    },
                    "msgtype": "m.image",
                    "url": resp.content_uri,
                }
            else:
                if mime_type.startswith("video/"):
                    msg_type = "m.video"
                elif mime_type.startswith("audio/"):
                    msg_type = "m.audio"
                else:
                    msg_type = "m.file"
                content = {
                    "body": os.path.basename(file),
                    "info": {
                        "size": file_stat.st_size,
                        "mimetype": mime_type,
                    },
                    "msgtype": msg_type,
                    "url": resp.content_uri,
                }
            await self._client.room_send(
                self._config.output[self.get_instance_name()].room_id,
                message_type="m.room.message",
                content=content
            )

    def _send_message(self, text: str, files: List[str]) -> None:
        self._loop.run_until_complete(self._send_message_impl(text, files))

    def send_message(self, text: str, files: List[str] = []) -> None:
        threading.Thread(target=self._send_message, args=(text, files)).start()
        log.message(self.get_instance_name(), text, files)

    def get_name(self) -> str:
        return "matrix"

    def close(self) -> None:
        self._loop.close()
