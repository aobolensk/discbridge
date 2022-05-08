import importlib
import inspect
import json
import os
import time
from typing import List

import yaml

from config import Config
from input.abc import Listener
from output.abc import Handler
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
        if os.path.isfile("config.yaml"):
            self._config = Config(yaml.load(open("config.yaml"), yaml.CLoader))
        elif os.path.isfile("config.json"):
            self._config = Config(json.load(open("config.json")))
        print(self._config.__dict__)

    def _init_listeners(self) -> None:
        listeners_dir = "input"
        for file in filter(lambda x: x.endswith(".py"), os.listdir(listeners_dir)):
            module = importlib.import_module(listeners_dir + "." + os.path.splitext(file)[0])
            listeners = [obj[1] for obj in inspect.getmembers(module, inspect.isclass)
                        if issubclass(obj[1], Listener) and obj[1] != Listener]
            for listener in listeners:
                self._listeners.append(listener())
                print("Input: Added " + listener.__name__)

    def _run_listeners(self) -> None:
        for listener in self._listeners:
            listener.run(self, self._config)

    def _init_handlers(self) -> None:
        handlers_dir = "output"
        for file in filter(lambda x: x.endswith(".py"), os.listdir(handlers_dir)):
            module = importlib.import_module(handlers_dir + "." + os.path.splitext(file)[0])
            handlers = [obj[1] for obj in inspect.getmembers(module, inspect.isclass)
                        if issubclass(obj[1], Handler) and obj[1] != Handler]
            for handler in handlers:
                self._handlers.append(handler())
                print("Output: Added " + handler.__name__)
        for handler in self._handlers:
            handler.init(self, self._config)

    def send_message(self, text: str, files: List[str] = []) -> None:
        for handler in self._handlers:
            handler.send_message(text, files)
