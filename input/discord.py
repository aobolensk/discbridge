import asyncio

from config import Config, DiscordInputConfig
from utils import tmp_random_filename

import discord
from input.abc import Listener


class _DiscordClient(discord.Client):
    def __init__(self, core, config: Config):
        super().__init__()
        self._core = core
        self._config = config

    async def on_ready(self):
        pass

    def run(self, *args, **kwargs):
        loop = self.loop

        async def runner():
            try:
                await self.start(*args, **kwargs)
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(f):
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

    def _format_backend_header(self, msg: discord.Message):
        text = "[Discord] "
        if msg.channel.name:
            text += "#" + msg.channel.name + " "
        text += f"({msg.created_at.astimezone()})\n"
        return text

    def _format_header(self, msg: discord.Message):
        text = self._format_backend_header(msg)
        text += msg.author.name + ": "
        return text

    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id:
            return
        if self._config.input.discord.chat_filter and message.channel.id not in self._config.input.discord.chat_ids:
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
    def start(self, core, config: Config):
        print("Input: DiscordListener start")
        self._core = core
        self._config = config
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        client = _DiscordClient(core, config)
        client.run(self._config.input.discord.token)

    def get_name(self):
        return "discord"

    def get_config_type(self) -> type:
        return DiscordInputConfig
