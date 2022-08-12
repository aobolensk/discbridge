import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from config import Config
from logger import log

from output.abc import Handler


class EmailHandler(Handler):
    def init(self, core, config: Config) -> None:
        self._core = core
        self._config = config
        self._server = smtplib.SMTP_SSL(self._config.output[self.get_instance_name()].smtp_server)
        self._server.ehlo(self._config.output[self.get_instance_name()].email)
        self._server.login(
            self._config.output[self.get_instance_name()].email,
            self._config.output[self.get_instance_name()].password)
        self._server.auth_plain()

    def send_message(self, text: str, files: List[str] = []):
        msg = MIMEMultipart()
        msg["From"] = self._config.output[self.get_instance_name()].email
        msg["To"] = ', '.join(self._config.output[self.get_instance_name()].to_addrs)
        msg["CC"] = ', '.join(self._config.output[self.get_instance_name()].cc_addrs)
        msg["Subject"] = self._config.output[self.get_instance_name()].subject
        msg.attach(MIMEText(text, 'plain'))
        full_to_addrs_list = (
            self._config.output[self.get_instance_name()].to_addrs +
            self._config.output[self.get_instance_name()].cc_addrs +
            self._config.output[self.get_instance_name()].bcc_addrs
        )
        for file in files:
            with open(file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {file}")
                msg.attach(part)
        self._server.send_message(msg, self._config.output[self.get_instance_name()].email, full_to_addrs_list)
        log.message(self.__class__.__name__, text, files)

    def get_name(self) -> str:
        return "email"

    def close(self) -> None:
        self._server.quit()
