#!/usr/bin/env python3
import json
import os
import time

from bridges.telegram import TelegramListener
from config import Config
from utils import tmp_dir


def main():
    config = Config(json.load(open("config.json")))
    print(config)
    os.makedirs(tmp_dir(), exist_ok=True)
    TelegramListener().run(config)
    while True:
        time.sleep(100)


if __name__ == "__main__":
    main()
