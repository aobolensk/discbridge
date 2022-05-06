import datetime
import shutil
import subprocess
import threading
import time
import uuid

import requests
from config import Config
from utils import tmp_dir

import telegram
from input.abc import Listener
from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater


class TelegramListener(Listener):
    def _download_file(self, file_id: str, ext=None):
        r = requests.get(f"https://api.telegram.org/bot{self._config.input.telegram.token}/getFile?file_id={file_id}")
        target_file_path = r.json()["result"]["file_path"]
        if ext is None:
            ext = target_file_path.split('.')[-1]
        r = requests.get(f"https://api.telegram.org/file/bot{self._config.input.telegram.token}/{target_file_path}", stream=True)
        output_file = tmp_dir() + '/' + uuid.uuid4().hex + '.' + ext
        if r.status_code == 200:
            with open(output_file, "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return output_file

    def _format_header(self, msg: telegram.Message):
        return (
            f"[Telegram] ({msg.date.astimezone()})\n" +
            (f"Forwarded from: {msg.forward_from.full_name} ({msg.forward_from.username})\n" if msg.forward_from is not None else "") +
            f"{msg.from_user.full_name} ({msg.from_user.username}): "
        )

    def _on_message(self, update: Update, context: CallbackContext) -> None:
        if self._config.input.telegram.chat_filter and update.message.chat.id not in self._config.input.telegram.chat_ids:
            print(f"{datetime.datetime.now()}: filtered id: {update.message.chat.id}")
            return
        text = self._format_header(update.message) + update.message.text
        self._core.send_message(text)

    def _on_sticker(self, update: Update, context: CallbackContext) -> None:
        if self._config.input.telegram.chat_filter and update.message.chat.id not in self._config.input.telegram.chat_ids:
            return
        t = threading.Thread(target=self._sticker_process_async, args=(update, context))
        t.setDaemon(True)
        t.start()

    def _sticker_process_async(self, update: Update, context: CallbackContext):
        gif_file = tmp_dir() + '/' + uuid.uuid4().hex + ".gif"
        tgs_file = self._download_file(update.message.sticker.file_id)
        subprocess.call(f"lottie_convert.py {tgs_file} {gif_file}", shell=True)
        text = self._format_header(update.message) + (update.message.text or '')
        self._core.send_message(text, [gif_file])

    def _on_attachment(self, update: Update, context: CallbackContext) -> None:
        if self._config.input.telegram.chat_filter and update.message.chat.id not in self._config.input.telegram.chat_ids:
            return
        file = self._download_file(update.message.effective_attachment.file_id)
        text = self._format_header(update.message) + (update.message.caption or '')
        self._core.send_message(text, [file])

    def start(self, core, config: Config):
        print("start")
        self._core = core
        self._config = config
        updater = Updater(config.input.telegram.token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self._on_message))
        dispatcher.add_handler(MessageHandler(Filters.sticker, self._on_sticker))
        dispatcher.add_handler(MessageHandler(Filters.animation, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.document, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.photo, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.video_note, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.video, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.voice, self._on_attachment))

        updater.start_polling()
        while True:
            time.sleep(100)
