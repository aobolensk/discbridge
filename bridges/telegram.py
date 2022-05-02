import datetime
import time
import requests
import shutil
import subprocess

from config import Config
from discord_webhook import DiscordWebhook
from utils import tmp_dir

from bridges.abc import Listener
from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater


class TelegramListener(Listener):
    def _on_message(self, update: Update, context: CallbackContext) -> None:
        if update.message.chat.id not in self._config.telegram.chat_ids:
            print(f"{datetime.datetime.now()}: filtered id: {update.message.chat.id}")
            return
        text = f"{update.message.from_user.username}: {update.message.text}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.execute()
        print(f"{datetime.datetime.now()}: {text}")

    def _on_sticker(self, update: Update, context: CallbackContext) -> None:
        if update.message.chat.id not in self._config.telegram.chat_ids:
            return
        r = requests.get(f"https://api.telegram.org/bot{self._config.telegram.token}/getFile?file_id={update.message.sticker.file_id}")
        tgs_file_path = r.json()["result"]["file_path"]
        r = requests.get(f"https://api.telegram.org/file/bot{self._config.telegram.token}/{tgs_file_path}", stream=True)
        if r.status_code == 200:
            with open(f"{tmp_dir()}/file.tgs", "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        subprocess.call(f"lottie_convert.py {tmp_dir()}/file.tgs {tmp_dir()}/file.gif", shell=True)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(f"{tmp_dir()}/file.gif", "rb").read(), filename=f"{tmp_dir()}/file.gif")
        webhook.execute()

    def _on_voice(self, update: Update, context: CallbackContext) -> None:
        if update.message.chat.id not in self._config.telegram.chat_ids:
            return
        print("_on_voice")
        r = requests.get(f"https://api.telegram.org/bot{self._config.telegram.token}/getFile?file_id={update.message.voice.file_id}")
        tgs_file_path = r.json()["result"]["file_path"]
        r = requests.get(f"https://api.telegram.org/file/bot{self._config.telegram.token}/{tgs_file_path}", stream=True)
        if r.status_code == 200:
            with open(f"{tmp_dir()}/file.ogg", "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(f"{tmp_dir()}/file.ogg", "rb").read(), filename=f"{tmp_dir()}/file.ogg")
        webhook.execute()

    def start(self, config: Config):
        print("start")
        self._config = config
        updater = Updater(config.telegram.token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self._on_message))
        dispatcher.add_handler(MessageHandler(Filters.sticker, self._on_sticker))
        dispatcher.add_handler(MessageHandler(Filters.voice, self._on_voice))

        updater.start_polling()
        while True:
            time.sleep(100)
