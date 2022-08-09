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


@dataclass
class MatrixOutputConfig:
    server: str
    user: str
    password: str
    room_id: str


class Config:
    def __init__(self, json) -> None:
        # Input
        self.input = dotdict()
        for input_name, config in json["input"].items():
            self.input[input_name] = globals()[f"{input_name.title()}InputConfig"](**(config))
        # Output
        self.output = dotdict()
        for output_name, config in json["output"].items():
            self.output[output_name] = globals()[f"{output_name.title()}OutputConfig"](**(config))
