import json
import os
import time
from typing import List

from config import Config
from input.telegram import TelegramListener
from output.discord import DiscordHandler
from output.telegram import TelegramHandler
from utils import tmp_dir


class Core:
    def __init__(self) -> None:
        self._listeners = list()
        self._handlers = list()

    def run(self) -> None:
        self._read_config()
        os.makedirs(tmp_dir(), exist_ok=True)
        self._init_listeners()
        self._init_handlers()
        self._run_listeners()
        while True:
            time.sleep(100)

    def _read_config(self) -> None:
        self._config = Config(json.load(open("config.json")))
        print(self._config.__dict__)

    def _init_listeners(self) -> None:
        if "telegram" in self._config.input.keys():
            print("Input: Added Telegram")
            self._listeners.append(TelegramListener())

    def _run_listeners(self) -> None:
        for listener in self._listeners:
            listener.run(self, self._config)

    def _init_handlers(self) -> None:
        if "discord" in self._config.output.keys():
            print("Output: Added Discord")
            self._handlers.append(DiscordHandler())
        if "telegram" in self._config.output.keys():
            print("Output: Added Telegram")
            self._handlers.append(TelegramHandler())
        for handler in self._handlers:
            handler.init(self, self._config)

    def send_message(self, text: str, files: List[str] = []) -> None:
        for handler in self._handlers:
            handler.send_message(text, files)
