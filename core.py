import importlib
import inspect
import os
import signal
import sys
from typing import List

import yaml

from config import Config
from input.abc import Listener
from logger import log
from output.abc import Handler
from utils import tmp_dir


class Core:
    def __init__(self, args) -> None:
        self._listeners = list()
        self._handlers = list()
        self._args = args

    def _stop_signal_handler(self, sig, frame):
        self._close_handlers()
        print('Stopped the bridge!')
        sys.exit(0)

    def run(self) -> None:
        self._read_config()
        os.makedirs(tmp_dir(), exist_ok=True)
        self._init_listeners()
        self._init_handlers()
        self._run_listeners()
        signal.signal(signal.SIGINT, self._stop_signal_handler)
        print("Press Ctrl+C to stop")
        signal.pause()

    def _read_config(self) -> None:
        if self._args.config:
            self._config = Config(yaml.load(open(self._args.config), yaml.CLoader))
        elif os.path.isfile("config.yaml"):
            self._config = Config(yaml.load(open("config.yaml"), yaml.CLoader))
        else:
            log.error("No config file found!")
            sys.exit(1)
        log.debug(self._config.__dict__)

    def _init_listeners(self) -> None:
        listeners_dir = "input"
        for file in filter(lambda x: x.endswith(".py"), os.listdir(listeners_dir)):
            module = importlib.import_module(listeners_dir + "." + os.path.splitext(file)[0])
            listeners = [obj[1] for obj in inspect.getmembers(module, inspect.isclass)
                         if issubclass(obj[1], Listener) and obj[1] != Listener]
            for input in self._config.input.keys():
                for listener in listeners:
                    if input.startswith(listener.get_name(listener)):
                        self._listeners.append(listener(input))
                        log.info(f"Input: Added {input} ({listener.__name__})")

    def _run_listeners(self) -> None:
        for listener in self._listeners:
            listener.run(self, self._config)

    def _init_handlers(self) -> None:
        handlers_dir = "output"
        for file in filter(lambda x: x.endswith(".py"), os.listdir(handlers_dir)):
            module = importlib.import_module(handlers_dir + "." + os.path.splitext(file)[0])
            handlers = [obj[1] for obj in inspect.getmembers(module, inspect.isclass)
                        if issubclass(obj[1], Handler) and obj[1] != Handler]
            for output in self._config.output.keys():
                for handler in handlers:
                    if output.startswith(handler.get_name(handler)):
                        self._handlers.append(handler(output))
                        log.info(f"Output: Added {output} ({handler.__name__})")
        for handler in self._handlers:
            handler.init(self, self._config)

    def _close_handlers(self) -> None:
        for handler in self._handlers:
            handler.close()

    def send_message(self, text: str, files: List[str] = []) -> None:
        for handler in self._handlers:
            handler.send_message(text, files)
