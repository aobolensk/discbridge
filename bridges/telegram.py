import datetime
import time
import requests
import shutil
import subprocess
import uuid

from config import Config
from discord_webhook import DiscordWebhook
from utils import tmp_dir

from bridges.abc import Listener
from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater


class TelegramListener(Listener):
    def _download_file(self, file_id: str, ext=None):
        r = requests.get(f"https://api.telegram.org/bot{self._config.telegram.token}/getFile?file_id={file_id}")
        target_file_path = r.json()["result"]["file_path"]
        if ext is None:
            ext = target_file_path.split('.')[-1]
        r = requests.get(f"https://api.telegram.org/file/bot{self._config.telegram.token}/{target_file_path}", stream=True)
        output_file = tmp_dir() + '/' + uuid.uuid4().hex + '.' + ext
        if r.status_code == 200:
            with open(output_file, "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return output_file

    def _on_message(self, update: Update, context: CallbackContext) -> None:
        if self._config.telegram.chat_filter and update.message.chat.id not in self._config.telegram.chat_ids:
            print(f"{datetime.datetime.now()}: filtered id: {update.message.chat.id}")
            return
        text = f"{update.message.from_user.username}: {update.message.text}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.execute()
        print(f"{datetime.datetime.now()}: {text}")

    def _on_sticker(self, update: Update, context: CallbackContext) -> None:
        if self._config.telegram.chat_filter and update.message.chat.id not in self._config.telegram.chat_ids:
            return
        gif_file = tmp_dir() + "/file.gif"
        tgs_file = self._download_file(update.message.sticker.file_id)
        subprocess.call(f"lottie_convert.py {tgs_file} {gif_file}", shell=True)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(gif_file, "rb").read(), filename=gif_file)
        webhook.execute()

    def _on_voice(self, update: Update, context: CallbackContext) -> None:
        if self._config.telegram.chat_filter and update.message.chat.id not in self._config.telegram.chat_ids:
            return
        file = self._download_file(update.message.voice.file_id, ext="ogg")
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(file, "rb").read(), filename=file)
        webhook.execute()

    def _on_videonote(self, update: Update, context: CallbackContext) -> None:
        if self._config.telegram.chat_filter and update.message.chat.id not in self._config.telegram.chat_ids:
            return
        file = self._download_file(update.message.video_note.file_id)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(file, "rb").read(), filename=file)
        webhook.execute()

    def _on_photo(self, update: Update, context: CallbackContext) -> None:
        if self._config.telegram.chat_filter and update.message.chat.id not in self._config.telegram.chat_ids:
            return
        file = self._download_file(update.message.photo.file_id)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(file, "rb").read(), filename=file)
        webhook.execute()

    def _on_animation(self, update: Update, context: CallbackContext) -> None:
        if self._config.telegram.chat_filter and update.message.chat.id not in self._config.telegram.chat_ids:
            return
        file = self._download_file(update.message.animation.file_id)
        text = f"{update.message.from_user.username}: {update.message.text or ''}"
        webhook = DiscordWebhook(
            url=self._config.discord.webhook_link, rate_limit_retry=True,
            content=text)
        webhook.add_file(file=open(file, "rb").read(), filename=file)
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
        dispatcher.add_handler(MessageHandler(Filters.photo, self._on_photo))
        dispatcher.add_handler(MessageHandler(Filters.animation, self._on_animation))

        updater.start_polling()
        while True:
            time.sleep(100)
