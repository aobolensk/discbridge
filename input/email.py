import email
import imaplib
import time
from typing import TYPE_CHECKING

import html2text
from config import Config
from logger import log
from utils import tmp_random_filename

from input.abc import Listener

if TYPE_CHECKING:
    from core import Core

class EmailListener(Listener):
    def _format_header(self, msg: email.message.Message):
        result = f"[EMAIL] {msg['to']} ({msg['date']})\n"
        result += f"{msg['from']} (subject: {msg['subject']}):\n"
        return result

    def start(self, core: 'Core', config: Config):
        log.info(f"Input: {self.get_instance_name()} (EmailListener) start")
        self._core = core
        self._config = config
        while True:
            self._check_email()
            time.sleep(self._config.input[self.get_instance_name()].check_interval)

    def _check_email(self):
        conn = imaplib.IMAP4_SSL(self._config.input[self.get_instance_name()].imap_server)
        try:
            retcode, capabilities = conn.login(
                self._config.input[self.get_instance_name()].email,
                self._config.input[self.get_instance_name()].password)
        except Exception as e:
            log.error(f"EmailListener init failed: {e}")
            return
        conn.select()
        retcode, messages = conn.search(None, '(UNSEEN)')
        if retcode != 'OK':
            pass
        for num in messages[0].split():
            retcode, data = conn.fetch(num, '(RFC822)')
            if retcode != 'OK':
                log.warning(f"EmailListener fetch failed: {retcode}")
                continue
            msg = email.message_from_bytes(data[0][1])
            text = ""
            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        body = part.get_payload(decode=True)
                        text += body.decode('utf-8')
                        continue
                    if (part.get_content_maintype() == 'multipart' or
                            part.get('Content-Disposition') is None or
                            part.get_content_type() == 'text/plain'):
                        continue
                    filename = part.get_filename()
                    ext = filename.rsplit('.', 1)[-1]
                    if filename:
                        tmp_name = tmp_random_filename(ext)
                        with open(tmp_name, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                            attachments.append(tmp_name)
            else:
                text += msg.get_payload(decode=True).decode('utf-8')
            conn.store(num, '+FLAGS', '\\SEEN')
            text = self._format_header(msg) + html2text.html2text(text)
            self._core.send_message(text, attachments)

    def get_name(self) -> str:
        return "email"
