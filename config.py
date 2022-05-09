from dataclasses import dataclass
from typing import List

from utils import dotdict


@dataclass
class TelegramInputConfig:
    token: str
    chat_filter: bool
    chat_ids: List[int]


@dataclass
class DiscordInputConfig:
    token: str
    chat_filter: bool
    chat_ids: List[int]


@dataclass
class TelegramOutputConfig:
    token: str
    chat_id: int


@dataclass
class DiscordOutputConfig:
    webhook_link: str


@dataclass
class EmailOutputConfig:
    email: str
    password: str
    smtp_server: str
    to_addrs: List[str]
    cc_addrs: List[str]
    bcc_addrs: List[str]
    subject: str


class Config:
    def __init__(self, json) -> None:
        # Input
        self.input = dotdict()
        if "telegram" in json["input"].keys():
            self.input.telegram = TelegramInputConfig(**json["input"]["telegram"])
        if "discord" in json["input"].keys():
            self.input.discord = DiscordInputConfig(**json["input"]["discord"])
        # Output
        self.output = dotdict()
        if "discord" in json["output"].keys():
            self.output.discord = DiscordOutputConfig(**json["output"]["discord"])
        if "telegram" in json["output"].keys():
            self.output.telegram = TelegramOutputConfig(**json["output"]["telegram"])
        if "email" in json["output"].keys():
            self.output.email = EmailOutputConfig(**json["output"]["email"])
