import json
import time

from bridges.telegram import TelegramListener
from config import Config


def main():
    config = Config(json.load(open("config.json")))
    print(config)
    TelegramListener().run(config)
    while True:
        time.sleep(100)


if __name__ == "__main__":
    main()
