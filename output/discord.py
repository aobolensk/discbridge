import datetime
from typing import List

from config import Config
from discord_webhook import DiscordWebhook

from output.abc import Handler


class DiscordHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config

    def send_message(self, text: str, files: List[str] = []):
        webhook = DiscordWebhook(
            url=self._config.output.discord.webhook_link, rate_limit_retry=True,
            content=text)
        for file in files:
            webhook.add_file(file=open(file, "rb").read(), filename=file)
        webhook.execute()
        print(str(datetime.datetime.now()) + ": " + text + ((f"(+ {len(files)} file(s): " +
            ', '.join(files) + ")") if files else ''))
