from typing import List

from config import Config, TelegramOutputConfig

from output.abc import Handler
from telegram import Bot


class TelegramHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        self._bot = Bot(self._config.output.telegram.token)

    def send_message(self, text: str, files: List[str] = []):
        if files:
            for file in files:
                self._bot.send_document(
                    self._config.output.telegram.chat_id, open(file, 'rb'), caption=text)
        else:
            self._bot.send_message(self._config.output.telegram.chat_id, text)

    def get_name(self) -> str:
        return "telegram"

    def close(self) -> None:
        pass

    def get_config_type(self) -> type:
        return TelegramOutputConfig
