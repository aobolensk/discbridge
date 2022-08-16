from dataclasses import dataclass, field
from typing import List

from utils import dotdict


@dataclass
class TelegramInputConfig:
    token: str
    chat_filter: bool = False
    chat_ids: List[int] = field(default_factory=list)
    polling_interval: int = 600


@dataclass
class DiscordInputConfig:
    token: str
    chat_filter: bool = False
    chat_ids: List[int] = field(default_factory=list)


@dataclass
class EmailInputConfig:
    email: str
    password: str
    imap_server: str
    check_interval: int = 60


@dataclass
class MatrixInputConfig:
    store_path: str
    credentials_json: str
    password: str
    room_id: str


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
    subject: str
    to_addrs: List[str] = field(default_factory=list)
    cc_addrs: List[str] = field(default_factory=list)
    bcc_addrs: List[str] = field(default_factory=list)


@dataclass
class MatrixOutputConfig:
    store_path: str
    credentials_json: str
    password: str
    room_id: str


class Config:
    def __init__(self, json) -> None:
        # Input
        self.input = dotdict()
        for input_name, config in json["input"].items():
            self.input[input_name] = globals()[f"{input_name.split('.')[0].title()}InputConfig"](**(config))
        # Output
        self.output = dotdict()
        for output_name, config in json["output"].items():
            self.output[output_name] = globals()[f"{output_name.split('.')[0].title()}OutputConfig"](**(config))
