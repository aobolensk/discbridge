from dataclasses import dataclass, field
from typing import List

from utils import dotdict


@dataclass
class TelegramInputConfig:
    token: str
    chat_filter: bool = False
    chat_ids: List[int] = field(default_factory=list)
    polling_interval: int = 600
    user_blocklist: bool = False
    user_blocklist_ids: List[int] = field(default_factory=list)
    user_allowlist: bool = False
    user_allowlist_ids: List[int] = field(default_factory=list)
    proxy: bool = False


@dataclass
class DiscordInputConfig:
    token: str
    chat_filter: bool = False
    chat_ids: List[int] = field(default_factory=list)
    user_blocklist: bool = False
    user_blocklist_ids: List[int] = field(default_factory=list)
    user_allowlist: bool = False
    user_allowlist_ids: List[int] = field(default_factory=list)
    proxy: bool = False


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
    proxy: bool = False


@dataclass
class TelegramOutputConfig:
    token: str
    chat_id: int
    proxy: bool = False


@dataclass
class DiscordOutputConfig:
    webhook_link: str
    proxy: bool = False


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
    proxy: bool = False


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
