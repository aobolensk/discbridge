import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from config import Config

from output.abc import Handler


class EmailHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        self._server = smtplib.SMTP_SSL(self._config.output.email.smtp_server)
        self._server.ehlo(self._config.output.email.email)
        self._server.login(self._config.output.email.email, self._config.output.email.password)
        self._server.auth_plain()

    def send_message(self, text: str, files: List[str] = []):
        msg = MIMEMultipart()
        msg["From"] = self._config.output.email.email
        msg["To"] = ', '.join(self._config.output.email.to_addrs)
        msg["CC"] = ', '.join(self._config.output.email.cc_addrs)
        msg["Subject"] = self._config.output.email.subject
        msg.attach(MIMEText(text, 'plain'))
        full_to_addrs_list = (
            self._config.output.email.to_addrs +
            self._config.output.email.cc_addrs +
            self._config.output.email.bcc_addrs
        )
        for file in files:
            with open(file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {file}")
                msg.attach(part)
        self._server.send_message(msg, self._config.output.email.email, full_to_addrs_list)

    def get_name(self) -> str:
        return "email"
