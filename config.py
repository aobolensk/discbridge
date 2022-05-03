from dataclasses import dataclass
from typing import List


@dataclass
class DiscordConfig:
    webhook_link: str


@dataclass
class TelegramConfig:
    token: str
    chat_filter: bool
    chat_ids: List[int]


@dataclass
class Config:
    discord: DiscordConfig
    telegram: TelegramConfig

    def __init__(self, json) -> None:
        self.discord = DiscordConfig(**json["discord"])
        self.telegram = TelegramConfig(**json["telegram"])
