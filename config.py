from dataclasses import dataclass
from typing import List


@dataclass
class DiscordOutputConfig:
    webhook_link: str


@dataclass
class TelegramInputConfig:
    token: str
    chat_filter: bool
    chat_ids: List[int]


@dataclass
class Config:
    discord: DiscordOutputConfig
    telegram: TelegramInputConfig

    def __init__(self, json) -> None:
        self.discord = DiscordOutputConfig(**json["output"]["discord"])
        self.telegram = TelegramInputConfig(**json["input"]["telegram"])
