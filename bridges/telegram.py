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
    def _download_file(self, file_id: str, output_file: str):
        r = requests.get(f"https://api.telegram.org/bot{self._config.telegram.token}/getFile?file_id={file_id}")
        target_file_path = r.json()["result"]["file_path"]
        r = requests.get(f"https://api.telegram.org/file/bot{self._config.telegram.token}/{target_file_path}", stream=True)
        if r.status_code == 200:
            with open(output_file, "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

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
        tgs_file = tmp_dir() + "/file.tgs"
        gif_file = tmp_dir() + "/file.gif"
        self._download_file(update.message.sticker.file_id, tgs_file)
        subprocess.call(f"lottie_convert.py {tgs_file} {gif_file}", shell=True)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(gif_file, "rb").read(), filename=gif_file)
        webhook.execute()

    def _on_voice(self, update: Update, context: CallbackContext) -> None:
        if update.message.chat.id not in self._config.telegram.chat_ids:
            return
        ogg_file = tmp_dir() + "/file.ogg"
        self._download_file(update.message.voice.file_id, ogg_file)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(ogg_file, "rb").read(), filename=ogg_file)
        webhook.execute()

    def _on_videonote(self, update: Update, context: CallbackContext) -> None:
        if update.message.chat.id not in self._config.telegram.chat_ids:
            return
        mp4_file = tmp_dir() + "/file.mp4"
        self._download_file(update.message.video_note.file_id, mp4_file)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(mp4_file, "rb").read(), filename=mp4_file)
        webhook.execute()

    def start(self, config: Config):
        print("start")
        self._config = config
        updater = Updater(config.telegram.token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self._on_message))
        dispatcher.add_handler(MessageHandler(Filters.sticker, self._on_sticker))
        dispatcher.add_handler(MessageHandler(Filters.voice, self._on_voice))
        dispatcher.add_handler(MessageHandler(Filters.video_note, self._on_videonote))

        updater.start_polling()
        while True:
            time.sleep(100)
