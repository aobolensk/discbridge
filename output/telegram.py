from typing import TYPE_CHECKING, List

from config import Config
from logger import log
from utils import proxy

from output.abc import Handler
from telegram import Bot
from telegram.utils.request import Request

if TYPE_CHECKING:
    from core import Core


class TelegramHandler(Handler):
    def init(self, core: 'Core', config: Config) -> None:
        self._core = core
        self._config = config
        proxy_setting = proxy.http() if config.output[self.get_instance_name()].proxy else None
        self._rq = Request(proxy_url=proxy_setting)
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
        pass
