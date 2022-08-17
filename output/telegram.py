from typing import List

from config import Config
from logger import log
from utils import proxy

from output.abc import Handler
from telegram import Bot
from telegram.utils.request import Request


class TelegramHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        self._rq = Request(proxy_url=proxy.http())
        self._bot = Bot(self._config.output[self.get_instance_name()].token, request=self._rq)

    def send_message(self, text: str, files: List[str] = []):
        if files:
            for file in files:
                self._bot.send_document(
                    self._config.output[self.get_instance_name()].chat_id, open(file, 'rb'), caption=text)
        else:
            self._bot.send_message(self._config.output[self.get_instance_name()].chat_id, text)
        log.message(self.get_instance_name(), text, files)

    def get_name(self) -> str:
        return "telegram"

    def close(self) -> None:
        self._bot.close()
