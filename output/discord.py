from typing import TYPE_CHECKING, List

from config import Config
from discord_webhook import DiscordWebhook
from logger import log
from utils import proxy, split_by_chunks

from output.abc import Handler

if TYPE_CHECKING:
    from core import Core


class DiscordHandler(Handler):
    def init(self, core: 'Core', config: Config) -> None:
        self._core = core
        self._config = config
        proxy_setting_http = proxy.http() if config.output[self.get_instance_name()].proxy else None
        proxy_setting_https = proxy.https() if config.output[self.get_instance_name()].proxy else None
        self._proxy = {
            "http": proxy_setting_http,
            "https": proxy_setting_https,
        }

    def send_message(self, text: str, files: List[str] = list()) -> None:
        text_chunks = list(split_by_chunks(text, 2000))
        for index, text_chunk in enumerate(text_chunks):
            if index + 1 != len(text_chunks):
                self._send_message_chunk(text_chunk)
            else:
                self._send_message_chunk(text_chunk, files)

    def _send_message_chunk(self, text: str, files: List[str] = list()) -> None:
        webhook = DiscordWebhook(
            url=self._config.output[self.get_instance_name()].webhook_link, rate_limit_retry=True,
            content=text, proxies=self._proxy)
        for file in files:
            webhook.add_file(file=open(file, "rb").read(), filename=file)
        resp = webhook.execute()
        if resp.status_code in (200, 204):
            log.message(self.get_instance_name(), text, files)
        elif resp.status_code == 413:
            # Retry sending without files
            text_ext = (
                f"{text}\n`+ {len(files)} file(s) that couldn't be uploaded (too big to upload to Discord)`")
            self.send_message(text_ext)
        else:
            log.error(f"[{self.get_instance_name()}] ERROR: {resp} ({text})")

    def get_name(self) -> str:
        return "discord"

    def close(self) -> None:
        pass
