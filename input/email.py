import imaplib
import email
import time

import html2text

from config import Config
from logger import log

from input.abc import Listener


class EmailListener(Listener):
    def _format_header(self, msg: email.message.Message):
        result = f"[EMAIL] {msg['to']} ({msg['date']})\n"
        result += f"{msg['from']} (subject: {msg['subject']}):\n"
        return result

    def start(self, core, config: Config):
        log.info("Input: EmailListener start")
        self._core = core
        self._config = config
        while True:
            self._check_email()
            time.sleep(60)

    def _check_email(self):
        conn = imaplib.IMAP4_SSL(self._config.input.email.imap_server)
        try:
            retcode, capabilities = conn.login(self._config.input.email.email, self._config.input.email.password)
        except Exception as e:
            log.error(f"EmailListener init failed: {e}")
            return
        conn.select()
        retcode, messages = conn.search(None, '(UNSEEN)')
        if retcode == 'OK':
            for num in messages[0].split():
                retcode, data = conn.fetch(num, '(RFC822)')
                if retcode == 'OK':
                    msg = email.message_from_bytes(data[0][1])
                    text = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/html':
                                body = part.get_payload(decode=True)
                                text += body.decode('utf-8')
                    else:
                        text += msg.get_payload(decode=True).decode('utf-8')
                    conn.store(num, '+FLAGS', '\\SEEN')
                    text = self._format_header(msg) + html2text.html2text(text)
                    self._core.send_message(text)

    def get_name(self) -> str:
        return "email"
