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
        resp = webhook.execute()
        if resp.status_code in (200, 204):
            print(str(datetime.datetime.now()) + ": " + text + ((f"(+ {len(files)} file(s): " +
                ', '.join(files) + ")") if files else ''))
        elif resp.status_code == 413:
            text_ext = (text + "\n" +
                f"`+ {len(files)} file(s) that couldn't be uploaded (too big to upload to Discord)`")
            self._retry_without_files(text_ext)
        else:
            print(str(datetime.datetime.now()) + ": " + text + ((f"(+ {len(files)} file(s): " +
                ', '.join(files) + ")") if files else '') + f". Error: {resp}")

    def _retry_without_files(self, text: str):
        webhook = DiscordWebhook(
            url=self._config.output.discord.webhook_link, rate_limit_retry=True,
            content=text)
        resp = webhook.execute()
        if resp.status_code in (200, 204):
            print(str(datetime.datetime.now()) + ": " + text)
        else:
            print("ERROR: " + str(datetime.datetime.now()) + ": " + text)