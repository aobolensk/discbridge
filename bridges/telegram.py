import datetime
from email import message
import time

from config import Config
from discord_webhook import DiscordWebhook
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from bridges.abc import Listener


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

    def start(self, config: Config):
        print("start")
        self._config = config
        updater = Updater(config.telegram.token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(MessageHandler(Filters.text, self._on_message))

        updater.start_polling()
        while True:
            time.sleep(100)

