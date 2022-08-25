import asyncio
from typing import TYPE_CHECKING, Optional

from config import Config
from logger import log
from utils import proxy, tmp_random_filename

import discord
from input.abc import Listener

if TYPE_CHECKING:
    from core import Core


class _DiscordClient(discord.Client):
    def __init__(self, instance_name: str, core: 'Core', config: Config, proxy: Optional[str] = None) -> None:
        super().__init__(proxy=proxy, intents=discord.Intents.all())
        self._instance_name = instance_name
        self._core = core
        self._config = config

    async def on_ready(self) -> None:
        pass

    def run(self, *args, **kwargs) -> None:
        loop = self.loop

        async def runner() -> None:
            try:
                await self.start(*args, **kwargs)
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(_) -> None:
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            future.remove_done_callback(stop_loop_on_completion)

        if not future.cancelled():
            try:
                return future.result()
            except KeyboardInterrupt:
                return None

    def _format_backend_header(self, msg: discord.Message) -> str:
        text = f"[{self._instance_name}] "
        if msg.channel.name:
            text += "#" + msg.channel.name + " "
        text += f"({msg.created_at.astimezone()})\n"
        return text

    def _format_header(self, msg: discord.Message) -> str:
        text = self._format_backend_header(msg)
        text += msg.author.name + ": "
        return text

    def _check_message(self, msg: discord.Message) -> bool:
        if (self._config.input[self._instance_name].chat_filter and
                msg.channel.id not in self._config.input[self._instance_name].chat_ids):
            return False
        if (self._config.input[self._instance_name].user_blocklist
                and msg.author.id in self._config.input[self._instance_name].user_blocklist_ids):
            log.info(
                f"{self._instance_name} (Discord): "
                f"Ignoring message from user {msg.author.id} (in blocklist)")
            return False
        if (self._config.input[self._instance_name].user_allowlist
                and msg.author.id not in self._config.input[self._instance_name].user_allowlist_ids):
            log.info(
                f"{self._instance_name} (Discord): "
                f"Ignoring message from user {msg.author.id} (not in allowlist)")
            return False
        return True

    async def on_message(self, message: discord.Message) -> None:
        if message.author.id == self.user.id:
            return
        if not self._check_message(message):
            return
        text = self._format_header(message)
        text += message.content
        files = []
        for attachment in message.attachments:
            output_file = tmp_random_filename(attachment.filename.split('.')[-1])
            with open(output_file, 'wb') as f:
                f.write(await attachment.read())
            files.append(output_file)
        self._core.send_message(text, files)


class DiscordListener(Listener):
    def start(self, core, config: Config) -> None:
        log.info(f"Input: {self.get_instance_name()} (DiscordListener) start")
        self._core = core
        self._config = config
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        proxy_setting = proxy.http() if config.input[self.get_instance_name()].proxy else None
        client = _DiscordClient(self.get_instance_name(), core, config, proxy=proxy_setting)
        client.run(self._config.input[self.get_instance_name()].token)

    def get_name(self) -> str:
        return "discord"
