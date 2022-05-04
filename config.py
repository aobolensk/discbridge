from dataclasses import dataclass
from typing import List

from utils import dotdict


@dataclass
class DiscordOutputConfig:
    webhook_link: str


@dataclass
class TelegramInputConfig:
    token: str
    chat_filter: bool
    chat_ids: List[int]


class Config:
    def __init__(self, json) -> None:
        # Input
        self.input = dotdict()
        if "telegram" in json["input"].keys():
            self.input.telegram = TelegramInputConfig(**json["input"]["telegram"])
        # Output
        self.output = dotdict()
        if "discord" in json["output"].keys():
            self.output.discord = DiscordOutputConfig(**json["output"]["discord"])
