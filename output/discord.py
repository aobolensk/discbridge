from typing import List

from config import Config
from discord_webhook import DiscordWebhook
from logger import log
from utils import proxy

from output.abc import Handler


class DiscordHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        proxy_setting_http = proxy.http() if config.output[self.get_instance_name()].proxy else None
        proxy_setting_https = proxy.https() if config.output[self.get_instance_name()].proxy else None
        self._proxy = {
            "http": proxy_setting_http,
            "https": proxy_setting_https,
        }

    def send_message(self, text: str, files: List[str] = []):
        webhook = DiscordWebhook(
            url=self._config.output[self.get_instance_name()].webhook_link, rate_limit_retry=True,
            content=text, proxies=self._proxy)
        for file in files:
            webhook.add_file(file=open(file, "rb").read(), filename=file)
        resp = webhook.execute()
        if resp.status_code in (200, 204):
            log.message(self.get_instance_name(), text, files)
        elif resp.status_code == 413:
            text_ext = (
                text + "\n" + f"`+ {len(files)} file(s) that couldn't be uploaded (too big to upload to Discord)`")
            self._retry_without_files(text_ext)
        else:
            log.error(f"[{self.get_instance_name()}] ERROR: {resp} ({text})")

    def _retry_without_files(self, text: str):
        webhook = DiscordWebhook(
            url=self._config.output[self.get_instance_name()].webhook_link, rate_limit_retry=True,
            content=text, proxies=self._proxy)
        resp = webhook.execute()
        if resp.status_code in (200, 204):
            log.message(self.get_instance_name(), text)
        else:
            log.error(f"[{self.get_instance_name()}] ERROR: {resp} ({text})")

    def get_name(self) -> str:
        return "discord"

    def close(self) -> None:
        pass
