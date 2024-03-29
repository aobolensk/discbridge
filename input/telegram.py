import shutil
import subprocess
import threading
import time
from typing import TYPE_CHECKING, Optional

import requests
from config import Config
from logger import log
from utils import proxy, tmp_random_filename

import telegram
from input.abc import Listener
from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater

if TYPE_CHECKING:
    from core import Core


class TelegramListener(Listener):
    def _download_file(self, file_id: str, ext: Optional[str] = None) -> str:
        r = requests.get(
            f"https://api.telegram.org/bot{self._config.input[self.get_instance_name()].token}"
            f"/getFile?file_id={file_id}")
        target_file_path = r.json()["result"]["file_path"]
        if ext is None:
            ext = target_file_path.split('.')[-1]
        r = requests.get(
            f"https://api.telegram.org/file/bot{self._config.input[self.get_instance_name()].token}/"
            f"{target_file_path}",
            stream=True)
        output_file = tmp_random_filename(ext)
        if r.status_code == 200:
            with open(output_file, "wb") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        return output_file

    def _format_backend_header(self, msg: telegram.Message) -> str:
        text = f"[{self.get_instance_name()}] "
        if msg.chat.title:
            text += msg.chat.title + " "
        if msg.chat.full_name:
            text += msg.chat.full_name + " "
        text += f"({msg.date.astimezone()})\n"
        return text

    def _format_header(self, msg: telegram.Message) -> str:
        return (
            self._format_backend_header(msg) +
            (f"Forwarded from: {msg.forward_from.full_name} ({msg.forward_from.username})\n"
             if msg.forward_from is not None else "") +
            msg.from_user.full_name +
            ((" (" + msg.from_user.username + ")") if msg.from_user.username else "") +
            ": "
        )

    def _check_message(self, msg: telegram.Message) -> bool:
        if (self._config.input[self.get_instance_name()].chat_filter
                and msg.chat.id not in self._config.input[self.get_instance_name()].chat_ids):
            log.info(
                f"{self.get_instance_name()} (Telegram): "
                f"Ignoring message in channel {msg.chat.id}")
            return False
        if (self._config.input[self.get_instance_name()].user_blocklist
                and msg.from_user.id in self._config.input[self.get_instance_name()].user_blocklist_ids):
            log.info(
                f"{self.get_instance_name()} (Telegram): "
                f"Ignoring message from user {msg.from_user.id} (in blocklist)")
            return False
        if (self._config.input[self.get_instance_name()].user_allowlist
                and msg.from_user.id not in self._config.input[self.get_instance_name()].user_allowlist_ids):
            log.info(
                f"{self.get_instance_name()} (Telegram): "
                f"Ignoring message from user {msg.from_user.id} (not in allowlist)")
            return False
        return True

    def _on_message(self, update: Update, context: CallbackContext) -> None:
        if not self._check_message(update.message):
            return
        text = self._format_header(update.message) + update.message.text
        self._core.send_message(text)

    def _on_sticker(self, update: Update, context: CallbackContext) -> None:
        if not self._check_message(update.message):
            return
        t = threading.Thread(target=self._sticker_process_async, args=(update, context))
        t.setDaemon(True)
        t.start()

    def _sticker_process_async(self, update: Update, context: CallbackContext):
        gif_file = tmp_random_filename("gif")
        tgs_file = self._download_file(update.message.sticker.file_id)
        subprocess.call(f"lottie_convert.py {tgs_file} {gif_file}", shell=True)
        text = self._format_header(update.message) + (update.message.text or '')
        self._core.send_message(text, [gif_file])

    def _on_attachment(self, update: Update, context: CallbackContext) -> None:
        if not self._check_message(update.message):
            return
        file = self._download_file(update.message.effective_attachment.file_id)
        text = self._format_header(update.message) + (update.message.caption or '')
        self._core.send_message(text, [file])

    def _on_status_update(self, update: Update, context: CallbackContext) -> None:
        if (self._config.input[self.get_instance_name()].chat_filter
                and update.message.chat.id not in self._config.input[self.get_instance_name()].chat_ids):
            return
        text = self._format_backend_header(update.message) + "Channel message: "
        msg = update.message
        if msg.group_chat_created:
            text += "Group chat created: " + msg.group_chat_created
        if msg.supergroup_chat_created:
            text += "Supergroup chat created: " + msg.supergroup_chat_created
        if msg.channel_chat_created:
            text += "Channel chat created: " + msg.channel_chat_created
        if msg.connected_website:
            text += "Connected website: " + msg.connected_website
        if msg.delete_chat_photo:
            text += "Delete chat photo: " + msg.delete_chat_photo
        if msg.left_chat_member:
            text += "Left chat member: " + msg.left_chat_member
        if msg.migrate_to_chat_id:
            text += "Migrate to chat id: " + msg.migrate_to_chat_id
        if msg.migrate_from_chat_id:
            text += "Migrate from chat id: " + msg.migrate_from_chat_id
        if msg.new_chat_members:
            text += "New chat members: " + msg.new_chat_members
        if msg.new_chat_photo:
            text += "New chat photo: " + msg.new_chat_photo
        if msg.new_chat_title:
            text += "New chat title: " + msg.new_chat_title
        if msg.message_auto_delete_timer_changed:
            text += "Message auto delete timer changed: " + msg.message_auto_delete_timer_changed
        if msg.pinned_message:
            text += "Pinned message: " + msg.pinned_message
        if msg.proximity_alert_triggered:
            text += "Proximity alert triggered: " + msg.proximity_alert_triggered
        if msg.voice_chat_scheduled:
            text += "Voice chat scheduled: " + msg.voice_chat_scheduled
        if msg.voice_chat_started:
            text += "Voice chat started: " + msg.voice_chat_started
        if msg.voice_chat_ended:
            text += "Voice chat ended: " + msg.voice_chat_ended
        if msg.voice_chat_participants_invited:
            text += "Voice chat participants invited: " + msg.voice_chat_participants_invited
        self._core.send_message(text)

    def start(self, core: 'Core', config: Config):
        log.info(f"Input: {self.get_instance_name()} (TelegramListener) start")
        self._core = core
        self._config = config
        proxy_setting = proxy.http() if config.input[self.get_instance_name()].proxy else None
        updater = Updater(config.input[self.get_instance_name()].token, request_kwargs={
            "proxy_url": proxy_setting,
        })
        dispatcher = updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self._on_message))
        dispatcher.add_handler(MessageHandler(Filters.sticker, self._on_sticker))
        dispatcher.add_handler(MessageHandler(Filters.animation, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.document, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.photo, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.video_note, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.video, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.voice, self._on_attachment))
        dispatcher.add_handler(MessageHandler(Filters.status_update, self._on_status_update))

        updater.start_polling(timeout=config.input[self.get_instance_name()].polling_interval)
        while True:
            time.sleep(config.input[self.get_instance_name()].polling_interval)

    def get_name(self) -> str:
        return "telegram"
